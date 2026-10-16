# Start a Word COM instance for the digest scripts (dot-source, then $w = New-WordApp).
# When the user's Word templates folder (Normal.dotm) sits on an unreachable network share, a new Word instance shows
# "Word cannot open the existing file (...Normal.dotm)" and rejects every COM call until the box is closed. Only that
# box of the instance started here is confirmed (OK); Word then continues with its built-in Normal template.
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

function Close-NormalDotmWarning([int]$wordPid) {
    $root = [System.Windows.Automation.AutomationElement]::RootElement
    $cond = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $wordPid)
    foreach ($win in $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)) {
        $all = $win.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
        $text = ($all | ForEach-Object { $_.Current.Name }) -join " "
        if ($text -notmatch "Normal\.dotm") { continue }
        foreach ($e in $all) {
            if ($e.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $e.Current.Name -eq "OK") {
                $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
                return $true
            }
        }
    }
    return $false
}

function New-WordApp {
    $before = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    $app = New-Object -ComObject Word.Application
    $new = @(Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object { $before -notcontains $_.Id } | ForEach-Object { $_.Id })
    $global:WordStartPids = $new
    "Word started: pid $new" | Out-Host
    Wait-WordReady { $app.Visible = $false }          # a setter (failed property reads are silent); keeps the alert setting
    return $app
}

# run $probe (a COM call) until Word accepts it, closing the Normal.dotm warning in between (it also comes up when a
# document is opened)
function Wait-WordReady([scriptblock]$probe) {
    for ($k = 0; $k -lt 60; $k++) {
        try { & $probe; return } catch { }
        foreach ($p in $global:WordStartPids) {
            if (Close-NormalDotmWarning $p) { "closed the Normal.dotm warning of Word $p" | Out-Host }
        }
        Start-Sleep -Milliseconds 500
    }
}
