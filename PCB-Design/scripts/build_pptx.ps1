# Build an editable PowerPoint deck from reports/slides/revb_pptx/deck.json (written by scripts/make_revb_deck.py).
#   powershell -ExecutionPolicy Bypass -File scripts\build_pptx.ps1 [-Out reports\slides\spb_revb_design_flow.pptx]
# Native PowerPoint objects only: text boxes, tables, shapes, pictures. Markup: **bold**, !!alert!!, _{sub}, ^{sup}.
param([string]$Spec = "", [string]$Out = "")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $Spec) { $Spec = Join-Path $root "reports\slides\revb_pptx\deck.json" }
if (-not $Out) { $Out = Join-Path $root "reports\slides\spb_revb_design_flow.pptx" }
$base = Split-Path -Parent $Spec
$deck = [IO.File]::ReadAllText($Spec, [Text.Encoding]::UTF8) | ConvertFrom-Json

function RGB([int]$r, [int]$g, [int]$b) { return $r + 256 * $g + 65536 * $b }
$C = @{
  kth = RGB 25 84 166; kthl = RGB 98 152 210; kth10 = RGB 232 239 248; hs = RGB 200 70 50; hs10 = RGB 250 233 230
  ls = RGB 50 100 190; pri = RGB 60 140 80; pri10 = RGB 230 243 233; meas = RGB 20 140 60; meas10 = RGB 226 243 232
  black = RGB 30 30 30; gray = RGB 120 120 120; white = RGB 255 255 255; dec = RGB 238 244 251; alert = RGB 200 70 50
}
$FONT = "Arial"

function Parse-Markup([string]$s) {
  # returns plain text and a list of runs (start index 0-based, length, kind)
  $runs = New-Object System.Collections.ArrayList
  $sb = New-Object System.Text.StringBuilder
  $rx = [regex]'\*\*(.+?)\*\*|!!(.+?)!!|_\{(.+?)\}|\^\{(.+?)\}'
  $pos = 0
  foreach ($m in $rx.Matches($s)) {
    [void]$sb.Append($s.Substring($pos, $m.Index - $pos))
    $kind = if ($m.Groups[1].Success) { "b" } elseif ($m.Groups[2].Success) { "a" } elseif ($m.Groups[3].Success) { "sub" } else { "sup" }
    $inner = ($m.Groups[1..4] | Where-Object { $_.Success } | Select-Object -First 1).Value
    # nested sub/sup inside bold/alert
    $inner2 = [regex]::Replace($inner, '_\{(.+?)\}|\^\{(.+?)\}', { param($mm) if ($mm.Groups[1].Success) { $mm.Groups[1].Value } else { $mm.Groups[2].Value } })
    [void]$runs.Add(@($sb.Length, $inner2.Length, $kind))
    [void]$sb.Append($inner2)
    $pos = $m.Index + $m.Length
  }
  [void]$sb.Append($s.Substring($pos))
  return @($sb.ToString(), $runs)
}

function Apply-Runs($tr, $runs, [int]$offset) {
  foreach ($r in $runs) {
    $ch = $tr.Characters($offset + $r[0] + 1, $r[1])
    switch ($r[2]) {
      "b" { $ch.Font.Bold = -1 }
      "a" { $ch.Font.Bold = -1; $ch.Font.Color.RGB = $C.alert }
      "sub" { $ch.Font.Subscript = -1 }
      "sup" { $ch.Font.Superscript = -1 }
    }
  }
}

function Set-Text($shape, $paras, [double]$size, [bool]$bullets, $color = $C.black, [string]$align = "left") {
  $size = [Math]::Round($size * $script:SCALE * $script:FS * 1.33, 1)
  $plain = @(); $allruns = @()
  foreach ($p in $paras) { $r = Parse-Markup ([string]$p[1]); $plain += $r[0]; $allruns += , @($r[1]) }
  $tf = $shape.TextFrame
  try { $tf.WordWrap = -1; $tf.AutoSize = 0 } catch { }     # not settable on table cells
  $tr = $tf.TextRange
  $tr.Text = ($plain -join "`r")
  $tr.Font.Name = $FONT
  $tr.Font.Size = [single]$size
  if ($env:PPTX_DEBUG) { Write-Host "SET [$($tr.Text.Substring(0, [Math]::Min(30, $tr.Text.Length)))] color=$color" }
  try { $tr.Font.Color.RGB = $color } catch { $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = $color }
  $tr.ParagraphFormat.Alignment = @{ left = 1; center = 2; right = 3 }[$align]
  $off = 0
  for ($i = 0; $i -lt $plain.Count; $i++) {
    $para = $tr.Paragraphs($i + 1)
    $lvl = [int]$paras[$i][0]
    if ($bullets) {
      $para.ParagraphFormat.Bullet.Visible = -1
      $para.ParagraphFormat.Bullet.Character = $(if ($lvl -gt 0) { 8211 } else { 8226 })
      $para.IndentLevel = $lvl + 1
      $para.ParagraphFormat.SpaceAfter = 4
      if ($lvl -gt 0) { $para.Font.Size = [single]($size - 1) }
    }
    Apply-Runs $tr $allruns[$i] $off
    $off += $plain[$i].Length + 1
  }
  if ($bullets) {
    $shape.TextFrame.Ruler.Levels(1).FirstMargin = 0; $shape.TextFrame.Ruler.Levels(1).LeftMargin = 14
    $shape.TextFrame.Ruler.Levels(2).FirstMargin = 18; $shape.TextFrame.Ruler.Levels(2).LeftMargin = 32
  }
}

function Add-Flow($sl, $steps, [int]$active) {
  $n = $steps.Count; $x0 = 30.0; $w = 900.0; $gap = 4.0; $bw = ($w - ($n - 1) * $gap) / $n
  for ($i = 0; $i -lt $n; $i++) {
    $b = $sl.Shapes.AddShape(5, $x0 + $i * ($bw + $gap), 54, $bw, 30)
    $on = ($i + 1) -eq $active
    $b.Fill.ForeColor.RGB = $(if ($on) { $C.kth } else { $C.kth10 })
    $b.Line.ForeColor.RGB = $C.kthl; $b.Line.Weight = 0.5
    $b.TextFrame.MarginLeft = 1; $b.TextFrame.MarginRight = 1; $b.TextFrame.MarginTop = 0; $b.TextFrame.MarginBottom = 0
    $t = $b.TextFrame.TextRange; $t.Text = ($steps[$i] -replace "`n", "`v"); $t.Font.Size = 7.5; $t.Font.Name = $FONT
    $t.Font.Color.RGB = $(if ($on) { $C.white } else { $C.black })
    $b.Name = "flow$($i + 1)"
  }
}

# KTH 16:9 template (720 x 405 pt): the spec is written on a 960 x 540 frame -> scale 0.75; fonts x FS
$TEMPLATE = Join-Path (Split-Path -Parent $root) "KTH_16_9 .pptx"
$SCALE = 0.75; $FS = 0.92
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open($TEMPLATE, $true, $true, $false)     # read-only, untitled copy
while ($pres.Slides.Count -gt 0) { $pres.Slides(1).Delete() }
$LAY = @{}
foreach ($l in $pres.SlideMaster.CustomLayouts) { $LAY[$l.Name] = $l }
$k = 0
foreach ($s in $deck.slides) {
  $k++
  if ($s.kind -eq "title" -or $s.kind -eq "end") {
    $sl = $pres.Slides.AddSlide($k, $LAY["Title slide_eng"])
    foreach ($sh in @($sl.Shapes)) {
      if ($sh.Type -ne 14) { continue }
      $pt = $sh.PlaceholderFormat.Type
      if ($pt -eq 3 -or $pt -eq 1) { $sh.TextFrame.TextRange.Text = $(if ($s.kind -eq "end") { "Thank you - questions?" } else { $s.title }) }
      elseif ($pt -eq 4 -or $pt -eq 2) {
        $sub = $(if ($s.kind -eq "end") { "Enes Ayaz, KTH Royal Institute of Technology" } else { ($s.subtitle -replace "`n", " ") + "`r" + $s.author })
        $sh.TextFrame.TextRange.Text = $sub
      }
    }
    try { $sl.HeadersFooters.Footer.Visible = 0; $sl.HeadersFooters.DateAndTime.Visible = 0; $sl.HeadersFooters.SlideNumber.Visible = 0 } catch { }
    continue
  }
  $sl = $pres.Slides.AddSlide($k, $LAY["Endast rubrik"])
  foreach ($sh in @($sl.Shapes)) {
    if ($sh.Type -eq 14 -and $sh.PlaceholderFormat.Type -eq 1) {
      $sh.TextFrame.TextRange.Text = $s.title
      $sh.TextFrame.TextRange.Font.Size = $(if ($s.title.Length -gt 58) { 18 } else { 21 })
    }
  }
  try {
    $hf = $sl.HeadersFooters
    $hf.Footer.Visible = -1; $hf.Footer.Text = $(if ($s.section) { $s.section } else { $script:lastsec })
    $hf.SlideNumber.Visible = -1; $hf.DateAndTime.Visible = 0
  } catch { }
  if ($s.section) { $script:lastsec = $s.section }
  foreach ($it in $s.items) {
    $b = $null
    if ($it.box) { $b = @($it.box | ForEach-Object { [double]$_ * $SCALE }) }
    if ($env:PPTX_DEBUG) { Write-Host "slide $k item $($it.type)" }
    switch ($it.type) {
      "text" {
        $sh = $sl.Shapes.AddTextbox(1, $b[0], $b[1], $b[2], $b[3])
        Set-Text $sh $it.paras ([double]$it.size) $true
      }
      "label" {
        $sh = $sl.Shapes.AddTextbox(1, $b[0], $b[1], $b[2], $b[3])
        $sh.TextFrame.MarginLeft = 2; $sh.TextFrame.MarginTop = 0
        Set-Text $sh @($it.text -split "`n" | ForEach-Object { , @(0, $_) }) ([double]$it.size) $false $C[$it.color] $it.align
        if ($it.bold) { $sh.TextFrame.TextRange.Font.Bold = -1 }
      }
      "image" {
        $f = Join-Path $base $it.file
        if (Test-Path $f) {
          $pic = $sl.Shapes.AddPicture($f, 0, -1, $b[0], $b[1])
          $sc = [Math]::Min($b[2] / $pic.Width, $b[3] / $pic.Height)
          $pic.LockAspectRatio = -1
          $pic.Width = $pic.Width * $sc
          $pic.Left = $b[0] + ($b[2] - $pic.Width) / 2
          $pic.Top = $b[1]
        } else {
          $ph = $sl.Shapes.AddShape(1, $b[0], $b[1], $b[2], $b[3]); $ph.Fill.ForeColor.RGB = $C.kth10
          $ph.TextFrame.TextRange.Text = "missing: $($it.file)"
        }
      }
      "table" {
        $rows = $it.rows; $nr = $rows.Count; $nc = $rows[0].Count
        $tb = $sl.Shapes.AddTable($nr, $nc, $b[0], $b[1], $b[2], [Math]::Min($b[3], 16.5 * $nr))
        $tbl = $tb.Table
        if ($it.colw) { for ($ci = 1; $ci -le $nc; $ci++) { $tbl.Columns($ci).Width = [double]$it.colw[$ci - 1] * $SCALE } }
        for ($r = 1; $r -le $nr; $r++) {
          for ($ci = 1; $ci -le $nc; $ci++) {
            $cell = $tbl.Cell($r, $ci)
            $cell.Shape.TextFrame.MarginTop = 2; $cell.Shape.TextFrame.MarginBottom = 2
            $cell.Shape.TextFrame.MarginLeft = 4; $cell.Shape.TextFrame.MarginRight = 4
            Set-Text $cell.Shape @(, @(0, [string]$rows[$r - 1][$ci - 1])) ([double]$it.size) $false $(if ($r -eq 1) { $C.white } else { $C.black })
            $cell.Shape.Fill.ForeColor.RGB = $(if ($r -eq 1) { $C.kth } elseif ($r % 2 -eq 0) { $C.kth10 } else { $C.white })
            if ($r -eq 1 -or ($it.bold_last -and $r -eq $nr)) { $cell.Shape.TextFrame.TextRange.Font.Bold = -1 }
          }
          $tbl.Rows($r).Height = 13
        }
      }
      "decision" {
        $sh = $sl.Shapes.AddShape(5, $b[0], $b[1], $b[2], $b[3])
        $sh.Fill.ForeColor.RGB = $C.dec; $sh.Line.ForeColor.RGB = $C.kth; $sh.Line.Weight = 1.25
        $sh.TextFrame.MarginLeft = 8; $sh.TextFrame.MarginTop = 2; $sh.TextFrame.MarginBottom = 2; $sh.TextFrame.VerticalAnchor = 3
        Set-Text $sh @(, @(0, ("**Decision:** " + $it.text))) 15 $false
        $sh.Name = "decision"
      }
      "note" {
        $sh = $sl.Shapes.AddTextbox(1, 18, 362, 620, 18)
        Set-Text $sh @(, @(0, $it.text)) 8 $false $C.gray
      }
      "rect" {
        $sh = $sl.Shapes.AddShape($(if ($it.round) { 5 } else { 1 }), $b[0], $b[1], $b[2], $b[3])
        $sh.Fill.ForeColor.RGB = $C[$it.fill]; $sh.Line.ForeColor.RGB = $C[$it.line]; $sh.Line.Weight = 1.25
        $sh.TextFrame.MarginLeft = 2; $sh.TextFrame.MarginRight = 2
        if ($it.text) {
          Set-Text $sh @($it.text -split "`n" | ForEach-Object { , @(0, $_) }) ([double]$it.size) $false $C[$it.color] "center"
          $sh.TextFrame.VerticalAnchor = 3
          if ($it.bold) { $sh.TextFrame.TextRange.Font.Bold = -1 }
        }
      }
      "line" {
        $p = @($it.pts | ForEach-Object { [double]$_ * $SCALE })
        $ln = $sl.Shapes.AddLine($p[0], $p[1], $p[2], $p[3])
        $ln.Line.ForeColor.RGB = $C[$it.color]; $ln.Line.Weight = [single]$it.w
        if ($it.arrow) { $ln.Line.EndArrowheadStyle = 2 }
      }
    }
  }
}
if (Test-Path $Out) { Remove-Item $Out -Confirm:$false }
$pres.SaveAs($Out, 24)
$pres.Close()
$pp.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
"saved $Out ($k slides)"
