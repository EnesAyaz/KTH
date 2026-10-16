# ICPE 2027-ECCE Asia digest: fills a copy of the official template (reports/paper/ICPE_Template.docx) with
# reports/paper/icpe/digest_content.json (scripts/make_icpe_digest_content.py) and exports the PDF for submission.
#   powershell -ExecutionPolicy Bypass -File scripts\build_icpe_digest.ps1
param(
    [switch]$NoEq, [switch]$NoFig, [int]$Upto = 9999, [switch]$Show,
    [string]$Root = (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
)
$ErrorActionPreference = "Stop"
$Paper = Join-Path $Root "reports\paper"
$Dir = Join-Path $Paper "icpe"
$Tpl = Join-Path $Paper "ICPE_Template.docx"
$Docx = Join-Path $Dir "submission\SPB_BB_ICPE2027_digest.docx"
$Pdf = Join-Path $Dir "submission\SPB_BB_ICPE2027_digest.pdf"
$C = Get-Content (Join-Path $Dir "digest_content.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$CM = 28.3465

Copy-Item $Tpl $Docx -Force
Unblock-File $Docx            # the downloaded template carries the web mark -> Protected View, read-only
$w = New-Object -ComObject Word.Application
# Word may attach to an instance the user is working in: never hide or quit it then, only close our own file
$own = ($w.Documents.Count -eq 0)
if ($own) { $w.Visible = [bool]$Show }
$w.DisplayAlerts = 0
# the Zotero Word plug-in hooks save/export and never returns in a hidden instance: unload it for this session
# only (Zotero.dotm stays in the Word start-up folder and loads again in the user's own Word)
if ($own) { foreach ($a in $w.AddIns) { if ($a.Name -like "Zotero*") { $a.Installed = $false } } }
# Save and export of the edited document still stall in this session (add-in hooks; PDFMaker cannot be
# disconnected without admin rights). The finished document is therefore taken out as Flat OPC XML, which
# needs no save, and a fresh Word session opens that file and writes the .docx and the PDF.
try {
    $d = $w.Documents.Open($Docx, $false, $false, $false)
    "read-only: " + $d.ReadOnly + ", remove-personal-info flag: " + $d.RemovePersonalInformation
    $d.RemovePersonalInformation = $false      # its save-time warning dialog blocks a hidden Word; fields cleared below
    $w.Options.WarnBeforeSavingPrintingSendingMarkup = $false

    # template body formats to reuse
    $P = $d.Paragraphs
    $fBody = $P.Item(9).Format
    $bodyFirst = $fBody.FirstLineIndent; $bodyBefore = $fBody.SpaceBefore; $bodyAfter = $fBody.SpaceAfter
    $bodyRule = $fBody.LineSpacingRule; $bodyLine = $fBody.LineSpacing
    $bodyFont = $P.Item(9).Range.Font.Name
    "template body: font $bodyFont, first-line $bodyFirst, before $bodyBefore, after $bodyAfter, H1 list '" + $P.Item(8).Range.ListFormat.ListString + "'"

    # topic text box; remove the example group (equation sample)
    for ($i = $d.Shapes.Count; $i -ge 1; $i--) {
        $s = $d.Shapes.Item($i)
        $s.Delete()                              # topic box overlaps the abstract; the topic goes into paragraph 1
    }
    # title and the empty lines above it sit in fixed-position frames: make them normal flowing paragraphs
    for ($i = $d.Frames.Count; $i -ge 1; $i--) { $d.Frames.Item($i).Delete() }
    $t0 = $P.Item(1).Range; $t0.InsertBefore($C.topic)
    $t0 = $P.Item(1).Range; $t0.Font.Size = 10; $t0.Font.Italic = -1; $t0.ParagraphFormat.Alignment = 0

    # delete everything after the abstract (template sections, guideline page); keep the empty spacer paragraph 7
    $d.Range($P.Item(8).Range.Start, $d.Content.End).Delete() | Out-Null
    for ($i = $d.Sections.Count; $i -ge 2; $i--) { }

    # title: one paragraph (16 pt, centred, as in the template)
    $t1 = $P.Item(3).Range; $t1.MoveEnd(1, -1) | Out-Null; $t1.Text = $C.title
    $P.Item(4).Range.Delete() | Out-Null

    # abstract: keep the formatted "Abstract-" lead, replace the text after the dash
    $ab = $P.Item(5)
    if ($ab.Range.Text.Trim().Length -lt 3) { $ab = $P.Item(6) }
    $txt = $ab.Range.Text
    $dash = $txt.IndexOf([char]0x2014)
    $rg = $d.Range($ab.Range.Start + $dash + 1, $ab.Range.End - 1); $rg.Delete() | Out-Null
    $lead = $d.Range($ab.Range.Start, $ab.Range.Start + $dash + 1); $lead.Font.Bold = -1; $lead.Font.Italic = -1
    $pos = $ab.Range.Start + $dash + 1
    foreach ($run in $C.abstract) {
        $r = $d.Range($pos, $pos); $r.InsertAfter($run[0])
        $r.Font.Bold = [int]($run[1] -match "b"); $r.Font.Italic = [int]($run[1] -match "i")
        $r.Font.Subscript = [int]($run[1] -match "s"); $r.Font.Superscript = [int]($run[1] -match "p")
        $pos = $r.End
    }

    function NextPara {
        $last = $d.Paragraphs.Last
        if ($last.Range.Text.Trim().Length -gt 0 -or $last.Range.Information(12)) {
            $d.Content.InsertParagraphAfter()
            $last = $d.Paragraphs.Last
        }
        $last.Range.ListFormat.RemoveNumbers()
        return $last
    }
    function AddRuns($para, $runs, $size) {
        $pos = $para.Range.End - 1
        foreach ($run in $runs) {
            $r = $d.Range($pos, $pos); $r.InsertAfter($run[0])
            $r.Font.Bold = [int]($run[1] -match "b"); $r.Font.Italic = [int]($run[1] -match "i")
            $r.Font.Subscript = [int]($run[1] -match "s"); $r.Font.Superscript = [int]($run[1] -match "p")
            if ($size) { $r.Font.Size = $size }
            $pos = $r.End
        }
    }
    function Body($para, $size, $align) {
        $para.Range.Style = "Normal"
        $f = $para.Format
        $f.FirstLineIndent = $bodyFirst; $f.SpaceBefore = 0; $f.SpaceAfter = 3
        $f.LineSpacingRule = 0; $f.Alignment = $align
        $para.Range.Font.Name = $bodyFont; $para.Range.Font.Size = $size
    }
    function Caption($runs) {
        $q = NextPara
        $q.Range.Style = "Caption"
        $q.Format.Alignment = 3; $q.Format.SpaceBefore = 2; $q.Format.SpaceAfter = 6; $q.Format.FirstLineIndent = 0
        $q.Range.Font.Size = 10
        AddRuns $q $runs 10
    }

    $nb = 0
    foreach ($b in $C.blocks) {
        $nb++; if ($nb -gt $Upto) { break }
        switch ($b.t) {
            "h1" {
                $q = NextPara
                $q.Range.Style = "Heading 1"
                $q.Range.InsertBefore($b.text)
            }
            "p" {
                $q = NextPara; Body $q 11 3; AddRuns $q $b.runs 11
            }
            "ref" {
                $q = NextPara; Body $q 10 3; $q.Format.FirstLineIndent = 0; $q.Format.SpaceAfter = 0
                AddRuns $q $b.runs 10
            }
            "eq" {
                if ($NoEq) { continue }
                $q = NextPara; Body $q 11 1; $q.Format.FirstLineIndent = 0
                $q.Format.SpaceBefore = 2; $q.Format.SpaceAfter = 2
                $r = $d.Range($q.Range.Start, $q.Range.Start)
                $r.InsertAfter($b.um + "#(" + $b.n + ")")
                $om = $d.OMaths.Add($r)
                $om.OMaths.Item(1).BuildUp()
            }
            "fig" {
                if ($NoFig) { continue }
                $q = NextPara; Body $q 11 1; $q.Format.FirstLineIndent = 0; $q.Format.SpaceBefore = 4
                $q.Format.KeepWithNext = -1
                $r = $d.Range($q.Range.Start, $q.Range.Start)
                $ish = $d.InlineShapes.AddPicture($b.img, $false, $true, $r)
                $ish.LockAspectRatio = -1
                $ish.Width = [single]($b.w_cm * $CM)
                Caption $b.cap
            }
            "table" {
                Caption $b.cap
                $d.Paragraphs.Last.Format.KeepWithNext = -1
                $d.Paragraphs.Last.Format.Alignment = 1
                $d.Content.InsertParagraphAfter()
                $q = $d.Paragraphs.Last
                Body $q 10 1; $q.Format.FirstLineIndent = 0
                $nr = $b.rows.Count; $nc = $b.rows[0].Count
                $tb = $d.Tables.Add($q.Range, $nr, $nc)
                $tb.Borders.Enable = $false
                for ($i = 1; $i -le $nr; $i++) {
                    for ($j = 1; $j -le $nc; $j++) {
                        $cell = $tb.Cell($i, $j)
                        $cell.Width = [single]($b.w_cm[$j - 1] * $CM)
                        $pos = $cell.Range.Start
                        foreach ($run in $b.rows[$i - 1][$j - 1]) {
                            $r = $d.Range($pos, $pos); $r.InsertAfter($run[0])
                            $r.Font.Bold = [int]($run[1] -match "b"); $r.Font.Italic = [int]($run[1] -match "i")
                            $r.Font.Subscript = [int]($run[1] -match "s"); $r.Font.Superscript = [int]($run[1] -match "p")
                            $r.Font.Size = 10
                            $pos = $r.End
                        }
                        $cell.Range.ParagraphFormat.Alignment = 0
                        $cell.Range.ParagraphFormat.FirstLineIndent = 0
                        $cell.Range.ParagraphFormat.SpaceAfter = 0
                    }
                }
                $tb.Rows.Alignment = 1
                $tb.Rows.Item(1).Borders.Item(-1).LineStyle = 1      # top
                $tb.Rows.Item(1).Borders.Item(-3).LineStyle = 1      # bottom of the header
                $tb.Rows.Item($nr).Borders.Item(-3).LineStyle = 1    # bottom
            }
        }
    }
    # statement of compliance (required by the call)
    $q = NextPara; Body $q 10 3; $q.Format.FirstLineIndent = 0; $q.Format.SpaceBefore = 8
    AddRuns $q $C.compliance 10
    $q.Range.Font.Italic = -1

    # page set-up of the call: A4, top 3 cm, bottom / left / right 2.5 cm
    foreach ($sec in $d.Sections) {
        $sec.PageSetup.PaperSize = 7
        $sec.PageSetup.SectionStart = 0          # continuous: the title section must not force a new page
        $sec.PageSetup.TextColumns.SetCount(1)   # the template's title section is two-column (title was in a frame)
        $sec.PageSetup.TopMargin = 3.0 * $CM
        $sec.PageSetup.BottomMargin = 2.5 * $CM
        $sec.PageSetup.LeftMargin = 2.5 * $CM
        $sec.PageSetup.RightMargin = 2.5 * $CM
    }
    # blind review: no personal information in the file
    foreach ($k in @("Author", "Last author", "Company", "Manager", "Comments", "Keywords", "Subject")) {
        try { $d.BuiltInDocumentProperties.Item($k).Value = "" } catch { }
    }
    try { $d.BuiltInDocumentProperties.Item("Title").Value = $C.title } catch { }
    $d.Repaginate()
    "pages: " + $d.ComputeStatistics(2) + ", words: " + $d.ComputeStatistics(0)
    $Xml = [IO.Path]::ChangeExtension($Docx, ".xml")
    [IO.File]::WriteAllText($Xml, $d.WordOpenXML, (New-Object Text.UTF8Encoding($false)))
    "flat OPC written"
    $d.Close($false)
}
finally {
    if ($own -and $w.Documents.Count -eq 0) { $w.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
}

# ---- stage 2 in its own process, after this Word instance has quit
$Xml = [IO.Path]::ChangeExtension($Docx, ".xml")
Start-Sleep -Seconds 3
& powershell -ExecutionPolicy Bypass -File (Join-Path $Root "scripts\export_icpe_digest.ps1") -Xml $Xml -Pdf $Pdf -Docx $Docx
Remove-Item $Xml -ErrorAction SilentlyContinue
& python (Join-Path $Root "scripts\clean_docx_meta.py") $Docx
