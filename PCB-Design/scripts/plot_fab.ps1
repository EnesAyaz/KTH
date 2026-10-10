# plot each copper layer of the fab board to PNG (scripts/plot_fab.ps1)
$cli = "C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
$b = "hardware\spb-bb-fab\spb-bb-fab.kicad_pcb"
$o = "hardware\spb-bb-fab\plots"
New-Item -ItemType Directory -Force $o | Out-Null
foreach ($l in @(@("F.Cu,F.SilkS,F.Mask,Edge.Cuts","L1_top"), @("In1.Cu,Edge.Cuts","L2"), @("In2.Cu,Edge.Cuts","L3"), @("B.Cu,B.SilkS,Edge.Cuts","L4_bottom"))) {
  & $cli pcb export pdf --layers $l[0] -o "$o\$($l[1]).pdf" $b | Out-Null
  pdftoppm -r 600 -png -singlefile "$o\$($l[1]).pdf" "$o\$($l[1])"
}
