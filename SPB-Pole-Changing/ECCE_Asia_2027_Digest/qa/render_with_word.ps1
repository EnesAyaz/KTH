param([string]$InputDocx,[string]$OutputStem)
$ErrorActionPreference='Stop'
$word=New-Object -ComObject Word.Application
$word.Visible=$false
$word.DisplayAlerts=0
try {
 $doc=$word.Documents.Open($InputDocx,$false,$true)
 $doc.Fields.Update() | Out-Null
 $doc.Repaginate()
 $pages=$doc.ComputeStatistics(2)
 Write-Output "Word page count: $pages"
 $doc.ExportAsFixedFormat(($OutputStem+'.pdf'),17)
 try { $doc.Close(0) } catch { Write-Output 'Word disconnected after successful export.' }
} finally { try { $word.Quit() } catch {} }
& 'C:\Users\enesa\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe' -r 140 -png ($OutputStem+'.pdf') $OutputStem
if($LASTEXITCODE -ne 0){throw 'Page rasterization failed'}
