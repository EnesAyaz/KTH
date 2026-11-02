s = open("spb_core.py", encoding="utf-8").read()
a = s.index("ROOT = os.path.dirname")
b = s.index("# ---- B-H curve")
new_head = '''ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN_JSON = os.path.join(ROOT, "02_analytics", "results", "torque_speed_envelope.json")
GEOM_JSON = os.path.join(ROOT, "data", "machine_geometry.json")
LEGACY = os.environ.get("SPB_GEOM", "agreed") == "legacy"      # legacy = T04 assumptions (analyst stator dict, g_eff 1.3 mm, 3 mm wedge)
MU0 = 4e-7 * math.pi
RPM = 2 * math.pi / 60
SQ2 = math.sqrt(2)
J = json.load(open(AN_JSON))
INV, VEH, STJ = J["inverter"], J["vehicle"], J["stator"]
GEOM = json.load(open(GEOM_JSON))
VMAX, IMAX = INV["V_ph_rms_max_V"], INV["I_module_rms_max_A"]
if os.environ.get("SPB_P_KW"):                                  # e.g. 300: use the 300 kW current rating (V limit unchanged)
    IMAX = IMAX * float(os.environ["SPB_P_KW"]) / (INV["P_rated_W"] / 1e3)
M = 48
Q = 48
NC = 3
Y = 7
TAU = 2 * math.pi / Q
if LEGACY:
    R = STJ["R_gap_m"]; LST = STJ["L_stk_m"]; GEFF = STJ["g_eff_m"]
    KST = 0.95
    SLOT_W, SLOT_H, YOKE_H = STJ["slot_w_m"], STJ["slot_h_m"], STJ["yoke_h_m"]
    TOOTH_W = STJ["tooth_w_m"]; TOOTH_W_TIP = TOOTH_W
    RS = STJ["R_coil_ohm"]
    M_TEETH, M_YOKE = STJ["m_teeth_kg"], STJ["m_yoke_kg"]
    L_END_HALF = STJ["l_end_half_m"]
else:
    _s, _w, _a = GEOM["stator"], GEOM["winding"], GEOM["airgap"]
    R = _s["R_bore_m"]; LST = _s["L_stk_m"]; GEFF = _a["g_eff_carter_IM_m"]
    KST = _s["stacking_factor"]
    SLOT_W, SLOT_H, YOKE_H = _s["slot_width_m"], _s["slot_depth_m"], _s["yoke_height_m"]
    TOOTH_W = _s["tooth_width_equivalent_m"]; TOOTH_W_TIP = _s["tooth_width_tip_m"]
    RS = _w["R_coil_120C_ohm"]
    _rho = _s["rho_fe_kg_m3"]
    M_TEETH = Q * 0.5 * (_s["tooth_width_tip_m"] + _s["tooth_width_root_m"]) * SLOT_H * LST * KST * _rho
    M_YOKE = math.pi * (_s["R_out_m"] ** 2 - _s["R_yoke_inner_m"] ** 2) * LST * KST * _rho
    L_END_HALF = _w["end_half_length_m"]
KG = MU0 * R * LST / GEFF                   # gap permeance per radian
RYM = R + SLOT_H + YOKE_H / 2
LY = 2 * math.pi * RYM / Q                  # yoke segment length
AY = KST * LST * YOKE_H
AT = KST * LST * TOOTH_W                    # tooth area used for the iron MMF
AT_TIP = KST * LST * TOOTH_W_TIP            # tooth area at the bore: B limit is checked here
if LEGACY:
    B_TOOTH_CAP = STJ["B_gap_max_T"] * STJ["slot_pitch_m"] / TOOTH_W / KST
    B_YOKE_CAP = STJ["B_yoke_max_T"] / KST
else:
    B_TOOTH_CAP = GEOM["limits"]["B_tooth_tip_max_T"]
    B_YOKE_CAP = GEOM["limits"]["B_yoke_max_T"]

'''
s = s[:a] + new_head + s[b:]
# B-H from geometry
s = s.replace('''_B = np.array([0, .2, .4, .6, .8, 1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.2, 2.5])
_H = np.array([0, 45, 70, 90, 115, 160, 260, 370, 600, 1000, 1850, 3700, 7500, 16000, 35000, 100000, 100000 + 0.3 / MU0])''',
'''_B = np.array(GEOM["material"]["B_T"], float)
_H = np.array(GEOM["material"]["H_A_per_m"], float)''')
# slot leakage
a = s.index("H_WEDGE = 3e-3")
b = s.index("def L_slot_mode")
new_slot = '''H_WEDGE = 3e-3
H_LAYER = (SLOT_H - H_WEDGE) / 2


def slot_lambdas():
    """self/mutual slot permeance coefficients (units of mu0*L_stk*N_c^2) of the top (a) and bottom (b) coil side."""
    if LEGACY:
        h1 = h2 = H_LAYER; hw = H_WEDGE; w = SLOT_W
        return (h2 / 3 + hw) / w, (h1 / 3 + h2 + hw) / w, (h2 / 2 + hw) / w
    wd, st = GEOM["winding"], GEOM["stator"]
    hA = hB = wd["layer_height_m"]; sep = wd["layer_separator_m"]; top = wd["top_air_m"]
    w = st["slot_width_m"]; b0 = st["slot_opening_m"]; tip = st["tooth_tip_height_m"]
    laa = (hA / 3 + top) / w + tip / b0
    lbb = (hB / 3 + sep + hA + top) / w + tip / b0
    lab = (hA / 2 + top) / w + tip / b0
    return laa, lbb, lab


L_END = MU0 * NC ** 2 * 2 * L_END_HALF * (0.3 if LEGACY else GEOM["winding"]["lambda_end_winding"])


'''
s = s[:a] + new_slot + s[b:]
s = s.replace("H_T = SLOT_H\n", "H_T = SLOT_H - (0 if LEGACY else GEOM['stator']['tooth_tip_height_m'] * 0)\n")
# tooth B output at the tip
s = s.replace('return dict(phi=phi, psi=psi, U=U, Bt=np.abs(phi) / AT, By=np.abs(Phi) / AY)', 'return dict(phi=phi, psi=psi, U=U, Bt=np.abs(phi) / AT_TIP, By=np.abs(Phi) / AY)')
# caps
a = s.index("def psi_max(p):")
b = s.index("def im_grid")
s = s[:a] + '''def psi_max(p):
    im_c, ps_c, Bt_c, By_c = mag_curve(p)
    if CAP_MODE["mode"] == "mec":
        return ps_c.max() * 0.99
    ok = (Bt_c <= B_TOOTH_CAP) & (By_c <= B_YOKE_CAP)
    return float(ps_c[np.where(ok)[0].max()])


''' + s[b:]
# rotor cage from geometry
s = s.replace('RHO_CAGE = 2.57e-8; BAR_A = 150e-6; BAR_L = 0.38; RING_A = 600e-6; RING_D = 0.27\nLAM_BAR, LAM_RING = 1.5, 0.3',
'''_r = GEOM["rotor_im"]
RHO_CAGE = _r["rho_cage_150C_ohm_m"]; BAR_A = _r["bar_area_m2"]; BAR_L = _r["bar_length_m"]; RING_A = _r["ring_area_m2"]; RING_D = _r["ring_mean_diameter_m"]
LAM_BAR, LAM_RING = (1.5, 0.3) if LEGACY else (_r["lambda_bar"], _r["lambda_ring"])''')
open("spb_core.py", "w", encoding="utf-8").write(s)
