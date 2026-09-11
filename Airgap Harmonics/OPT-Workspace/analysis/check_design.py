"""Check draft arithmetic; does not validate the circuit or FEA."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
p = json.loads((ROOT / "config/draft_parameters.json").read_text())
i = p["i_mpp_A"]
v = p["series_cells_assumed"] * p["v_mpp_V"]
report = {
    "status": "Arithmetic only; series-cell count assumed, return voltage interpreted as total drop",
    "matched_field_resistance_ohm": (v-p["return_voltage_table_V"])/i,
    "draft_field_resistance_ohm": p["field_resistance_table_ohm"],
    "return_voltage_implied_by_draft_resistance_V": v-i*p["field_resistance_table_ohm"],
    "field_copper_loss_per_resistance_W": i*i*p["field_resistance_table_ohm"],
    "return_loss_from_table_voltage_W": i*p["return_voltage_table_V"],
    "draft_return_loss_W": p["return_loss_table_W"],
    "mmf_At": p["field_turns"]*i,
}
for mode in ("4pole", "2pole"):
    report[f"efficiency_{mode}_percent"] = 100*p["rated_output_W"]/(p["rated_output_W"]+p[f"loss_{mode}_W"])
out=ROOT/"results/tables/design_check.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
