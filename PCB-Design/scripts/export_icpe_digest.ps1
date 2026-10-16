# Stage 2 of the ICPE digest build (called by build_icpe_digest.ps1 in its own process): opens the Flat OPC file
# written by stage 1 in a fresh Word session, exports the PDF and saves the .docx.
# Read-only open with Word's default alert setting is the combination that exports reliably on this machine
# (the Zotero and Adobe PDFMaker add-ins stall save/export of a document edited through COM).
param([string]$Xml, [string]$Pdf, [string]$Docx)
$ErrorActionPreference = "Stop"
$w = New-Object -ComObject Word.Application
$own = ($w.Documents.Count -eq 0)
try {
    $d = $w.Documents.Open($Xml, $false, $true, $false)
    "pages: " + $d.ComputeStatistics(2)
    $d.ExportAsFixedFormat($Pdf, 17)
    "wrote $Pdf"
    $d.SaveAs2($Docx, 16)
    "wrote $Docx"
    $d.Close($false)
}
finally {
    if ($own -and $w.Documents.Count -eq 0) { $w.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
}
