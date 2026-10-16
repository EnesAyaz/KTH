# Stage 2 of the ICPE digest build (called by build_icpe_digest.ps1 in its own process): opens the Flat OPC file
# written by stage 1 in a fresh Word session, exports the PDF and saves the .docx.
# Read-only open with Word's default alert setting is the combination that exports reliably on this machine
# (the Zotero and Adobe PDFMaker add-ins stall save/export of a document edited through COM).
param([string]$Xml, [string]$Pdf, [string]$Docx)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "word_start.ps1")
$w = New-WordApp
$own = ($w.Documents.Count -eq 0)
try {
    $global:WordDoc = $null
    Wait-WordReady { $global:WordDoc = $w.Documents.Open($Xml, $false, $true, $false); if (-not $global:WordDoc) { throw "open rejected" } }
    $d = $global:WordDoc
    Wait-WordReady { $d.RemovePersonalInformation = $false }
    "pages: " + $d.ComputeStatistics(2)
    $d.ExportAsFixedFormat($Pdf, 17)
    "wrote $Pdf"
    try {
        $d.SaveAs2($Docx, 16)
        "wrote $Docx"
        $d.Close($false)
    }
    catch {
        # this Word session drops the COM connection right after the export: write the package without Word
        "SaveAs2 failed ($($_.Exception.Message)); .docx from the Flat OPC file instead"
        & python (Join-Path $PSScriptRoot "flatopc_to_docx.py") $Xml $Docx
    }
}
finally {
    try { if ($own -and $w.Documents.Count -eq 0) { $w.Quit() } } catch { }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    # a disconnected hidden instance started here stays behind: end it (never the user's own Word)
    foreach ($p in $global:WordStartPids) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
}
