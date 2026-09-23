"""GaN device parameter model, loaded from data/devices/*.yaml.

All numeric datasheet quantities are converted to SI base units on load
(V, A, F, ohm, J, C/W) so downstream modules never juggle unit prefixes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEVICES_DIR = Path(__file__).resolve().parents[2] / "data" / "devices"


@dataclass
class SwitchingEnergyRef:
    v_ds_test: float
    i_d_test: float
    r_g_on_test: float
    r_g_off_test: float
    e_on_test: float
    e_off_test: float


@dataclass
class GaNDevice:
    part_number: str
    manufacturer: str

    v_ds_max: float
    i_d_max_cont: float
    i_d_max_pulsed: float
    t_j_max: float
    t_j_op_recommended: float

    r_ds_on_25c: float
    r_ds_on_tc1: float
    r_ds_on_tc2: float

    v_gs_drive: float
    v_gs_th: float
    v_gs_plateau: float
    q_gs: float
    q_gd: float
    q_g_total: float
    r_g_internal: float

    c_oss_ref_v: float
    c_oss_ref: float
    c_oss_table: list[tuple[float, float]]

    v_sd0: float
    r_sd: float

    sw_ref: SwitchingEnergyRef

    r_th_jc: float
    r_th_jb: float

    ltspice_subckt: str
    ltspice_lib_file: str
    ltspice_symbol_file: str
    ltspice_pin_order: str

    source_file: str = field(default="", repr=False)
    c_iss_ref: float = 0.0   # datasheet reference CISS=CGS+CGD at c_oss_ref_v, F (0 if not given)
    c_rss_ref: float = 0.0   # datasheet reference CRSS=CGD at c_oss_ref_v, F (0 if not given)

    def r_ds_on(self, t_j_c: float) -> float:
        """R_ds_on(Tj) via the datasheet's linear/quadratic temp-coefficient fit."""
        dt = t_j_c - 25.0
        return self.r_ds_on_25c * (1.0 + self.r_ds_on_tc1 * dt + self.r_ds_on_tc2 * dt**2)

    def c_oss(self, v_ds: float) -> float:
        """C_oss(Vds) by linear interpolation of the datasheet table (falls back to ref value)."""
        if not self.c_oss_table:
            return self.c_oss_ref
        xs = [p[0] for p in self.c_oss_table]
        ys = [p[1] for p in self.c_oss_table]
        if v_ds <= xs[0]:
            return ys[0]
        if v_ds >= xs[-1]:
            return ys[-1]
        for i in range(len(xs) - 1):
            if xs[i] <= v_ds <= xs[i + 1]:
                frac = (v_ds - xs[i]) / (xs[i + 1] - xs[i])
                return ys[i] + frac * (ys[i + 1] - ys[i])
        return ys[-1]

    def v_sd(self, i: float) -> float:
        """Third-quadrant (reverse, Vgs=0) conduction voltage at |current| = i."""
        return self.v_sd0 + self.r_sd * abs(i)


def _get(d: dict, *path, required: bool = True, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            if required:
                raise KeyError(f"Missing required device field: {'.'.join(path)}")
            return default
        cur = cur[key]
    return cur


def load_device(name_or_path: str) -> GaNDevice:
    """Load a device by filename stem (looked up in data/devices/) or by full path."""
    p = Path(name_or_path)
    if not p.exists():
        p = DEVICES_DIR / f"{name_or_path}.yaml"
    if not p.exists():
        raise FileNotFoundError(f"Device file not found: {name_or_path} (looked in {DEVICES_DIR})")

    with open(p, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)

    coss_table_raw = _get(d, "capacitance", "c_oss_table_V_pF", required=False, default=[])
    coss_table = [(float(v), float(c) * 1e-12) for v, c in coss_table_raw]

    sw_ref = SwitchingEnergyRef(
        v_ds_test=_get(d, "switching_energy_reference", "v_ds_test_V"),
        i_d_test=_get(d, "switching_energy_reference", "i_d_test_A"),
        r_g_on_test=_get(d, "switching_energy_reference", "r_g_on_test_ohm"),
        r_g_off_test=_get(d, "switching_energy_reference", "r_g_off_test_ohm"),
        e_on_test=_get(d, "switching_energy_reference", "e_on_test_uJ") * 1e-6,
        e_off_test=_get(d, "switching_energy_reference", "e_off_test_uJ") * 1e-6,
    )

    return GaNDevice(
        part_number=_get(d, "part_number"),
        manufacturer=_get(d, "manufacturer", required=False, default=""),
        v_ds_max=_get(d, "ratings", "v_ds_max_V"),
        i_d_max_cont=_get(d, "ratings", "i_d_max_continuous_A"),
        i_d_max_pulsed=_get(d, "ratings", "i_d_max_pulsed_A"),
        t_j_max=_get(d, "ratings", "t_j_max_C"),
        t_j_op_recommended=_get(d, "ratings", "t_j_op_recommended_C"),
        r_ds_on_25c=_get(d, "on_resistance", "r_ds_on_25C_mOhm") * 1e-3,
        r_ds_on_tc1=_get(d, "on_resistance", "temp_coeff_linear_per_C"),
        r_ds_on_tc2=_get(d, "on_resistance", "temp_coeff_quadratic_per_C2", required=False, default=0.0),
        v_gs_drive=_get(d, "gate_charge", "v_gs_drive_V"),
        v_gs_th=_get(d, "gate_charge", "v_gs_th_V"),
        v_gs_plateau=_get(d, "gate_charge", "v_gs_plateau_V"),
        q_gs=_get(d, "gate_charge", "q_gs_nC") * 1e-9,
        q_gd=_get(d, "gate_charge", "q_gd_nC") * 1e-9,
        q_g_total=_get(d, "gate_charge", "q_g_total_nC") * 1e-9,
        r_g_internal=_get(d, "gate_charge", "r_g_internal_ohm"),
        c_oss_ref_v=_get(d, "capacitance", "c_oss_ref_V"),
        c_oss_ref=_get(d, "capacitance", "c_oss_ref_pF") * 1e-12,
        c_oss_table=coss_table,
        v_sd0=_get(d, "third_quadrant_conduction", "v_sd0_V"),
        r_sd=_get(d, "third_quadrant_conduction", "r_sd_ohm"),
        sw_ref=sw_ref,
        r_th_jc=_get(d, "thermal", "r_th_jc_C_per_W"),
        r_th_jb=_get(d, "thermal", "r_th_jb_C_per_W", required=False, default=0.0),
        ltspice_subckt=_get(d, "ltspice_model", "subckt_name", required=False, default=""),
        ltspice_lib_file=_get(d, "ltspice_model", "lib_file", required=False, default=""),
        ltspice_symbol_file=_get(d, "ltspice_model", "symbol_file", required=False, default=""),
        ltspice_pin_order=_get(d, "ltspice_model", "pin_order", required=False, default="D G S"),
        source_file=str(p),
        c_iss_ref=_get(d, "capacitance", "c_iss_ref_pF", required=False, default=0.0) * 1e-12,
        c_rss_ref=_get(d, "capacitance", "c_rss_ref_pF", required=False, default=0.0) * 1e-12,
    )


def list_devices() -> list[str]:
    return sorted(p.stem for p in DEVICES_DIR.glob("*.yaml"))
