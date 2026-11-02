"""R01 stage 1: write the agreed stator/rotor drawing (inputs only) to data/machine_geometry.json.
Stage 2 (compute_R01.py) appends the quantities derived from it.  Every number has a unit in its key and a note in `notes`."""
import json, math, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = 48
R = 0.165
tau_s = 2 * math.pi * R / Q

stator = dict(
    Q_slots=Q, R_bore_m=R, L_stk_m=0.36, R_out_m=0.235, slot_depth_m=0.045, slot_width_m=0.009, slot_opening_m=0.003,
    tooth_tip_height_m=0.0015, yoke_height_m=0.025, stacking_factor=0.95, lamination="M270-35A (0.35 mm)", rho_fe_kg_m3=7650.0,
)
stator["slot_pitch_at_bore_m"] = tau_s
stator["tooth_width_tip_m"] = tau_s - stator["slot_width_m"]
stator["tooth_width_root_m"] = 2 * math.pi * (R + stator["slot_depth_m"]) / Q - stator["slot_width_m"]
stator["tooth_width_equivalent_m"] = stator["tooth_width_tip_m"] + (stator["tooth_width_root_m"] - stator["tooth_width_tip_m"]) / 3
stator["R_yoke_inner_m"] = R + stator["slot_depth_m"]
stator["R_yoke_mean_m"] = stator["R_yoke_inner_m"] + stator["yoke_height_m"] / 2

cond_w, cond_h, ins = 7.5e-3, 5.4e-3, 0.25e-3
winding = dict(
    coils=Q, coil_pitch_slots=7, turns_per_coil=3, layers=2, conductors_per_slot=6, module_count=16, coils_per_module=3,
    module_coil_rule="module j = coils j, j+16, j+32 (star, isolated neutral); coil k has sides in slots k (top layer) and k+7 (bottom layer)",
    conductor_bare_width_m=cond_w, conductor_bare_height_m=cond_h, conductor_insulation_per_side_m=ins,
    conductor_type="rectangular hairpin-type copper",
    liner_per_side_m=0.5e-3, layer_separator_m=1.0e-3,
    rho_cu_120C_ohm_m=2.4e-8, end_winding_extension_m=0.02, end_winding_factor=1.2, lambda_end_winding=0.3,
)
winding["conductor_area_m2"] = cond_w * cond_h
winding["layer_height_m"] = 3 * (cond_h + 2 * ins)
winding["top_air_m"] = stator["slot_depth_m"] - stator["tooth_tip_height_m"] - winding["liner_per_side_m"] - 2 * winding["layer_height_m"] - winding["layer_separator_m"]
winding["top_air_note"] = "wedge 3.0 mm + clearance/cooling gap; non-magnetic wedge assumed"
Dmid = 2 * R + stator["slot_depth_m"]
winding["end_half_length_m"] = winding["end_winding_factor"] * math.pi * Dmid * 7 / Q + 2 * winding["end_winding_extension_m"]
winding["mean_turn_length_m"] = 2 * (stator["L_stk_m"] + winding["end_half_length_m"])
winding["R_coil_120C_ohm"] = winding["rho_cu_120C_ohm_m"] * 3 * winding["mean_turn_length_m"] / winding["conductor_area_m2"]
winding["copper_mass_kg"] = Q * 3 * winding["conductor_area_m2"] * winding["mean_turn_length_m"] * 8900.0
slot_gross = stator["slot_width_m"] * stator["slot_depth_m"]
winding["copper_area_per_slot_m2"] = 6 * winding["conductor_area_m2"]
winding["fill_gross_slot"] = winding["copper_area_per_slot_m2"] / slot_gross
winding["fill_insulated_window"] = 6 * winding["conductor_area_m2"] / (6 * (cond_w + 2 * ins) * (cond_h + 2 * ins))
winding["current_density_at_310A_A_mm2"] = 310.44 / (winding["conductor_area_m2"] * 1e6)
winding["current_density_at_266A_A_mm2"] = 266.09 / (winding["conductor_area_m2"] * 1e6)

# Carter coefficients (stator and rotor slot openings)
def carter(tau, b0, g):
    gam = (b0 / g) ** 2 / (5 + b0 / g)
    return tau / (tau - gam * g)

g_mech = 1.0e-3
tau_r = 2 * math.pi * (R - g_mech) / 58
kc_s = carter(tau_s, stator["slot_opening_m"], g_mech)
kc_r = carter(tau_r, 1.5e-3, g_mech)
airgap = dict(g_mechanical_IM_m=g_mech, carter_stator=kc_s, carter_rotor_IM=kc_r, g_eff_carter_IM_m=g_mech * kc_s * kc_r,
              note="g_eff = g * k_c,s * k_c,r. NO saturation factor in g_eff: iron saturation is a separate flux-dependent curve (magnetising_curve in derived).")

# IM cage
bar_w = 7.0e-3
bar_h = 150e-6 / bar_w
rotor_im = dict(slots=58, R_rotor_m=R - g_mech, bar_width_m=bar_w, bar_height_m=bar_h, bar_area_m2=150e-6, bridge_height_m=1.0e-3,
                bridge_opening_m=1.5e-3, bar_length_m=0.38, ring_area_m2=600e-6, ring_mean_diameter_m=0.27, rho_cage_150C_ohm_m=2.57e-8,
                lambda_bar=bar_h / (3 * bar_w) + 1.0e-3 / 1.5e-3, lambda_ring=0.3, skew="none",
                rotor_tooth_width_m=tau_r - bar_w, tip_speed_limit_m_s=125.0,
                shaft_radius_m=0.060)
rotor_im["lambda_bar_note"] = "h/(3b) + bridge_height/bridge_opening (rectangular bar, semi-closed slot)"

# WRSM rotor (8 salient poles); gap chosen in stage 2, written here as a default that stage 2 may overwrite
rotor_wrsm = dict(poles=8, pole_arc_ratio=0.7, pole_body_width_m=0.050, field_slot_depth_m=0.055, shaft_radius_m=0.040,
                  interpolar_path_length_m=0.030, field_fill=0.5, rho_cu_120C_ohm_m=2.4e-8, mean_turn_length_m=1.0,
                  rotor_yoke_rule="yoke thickness >= 2x the 8-pole value so the ++-- (2p=4) pattern stays below 1.6 T",
                  group_A_poles=[0, 3, 4, 7], group_B_poles=[1, 2, 5, 6],
                  pattern_2p8=[1, -1, 1, -1, 1, -1, 1, -1], pattern_2p4=[1, 1, -1, -1, 1, 1, -1, -1],
                  pattern_transition="[1 k -k -1 1 k -k -1], k=-1 -> 2p8, k=+1 -> 2p4 (Field Excitation/FE_MMF.m)",
                  g_mechanical_m=None, B0_noload_T=0.7122233430090569,
                  B0_note="no-load air-gap flux density at full field, kept from T03 so psi_f,max is unchanged")

material = dict(name="M270-35A-like generic", B_T=[0, .2, .4, .6, .8, 1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.2, 2.5],
                H_A_per_m=[0, 45, 70, 90, 115, 160, 260, 370, 600, 1000, 1850, 3700, 7500, 16000, 35000, 100000, 100000 + 0.3 / (4e-7 * math.pi)],
                iron_loss_anchors=[dict(f_Hz=50, B_T=1.5, W_per_kg=2.7), dict(f_Hz=400, B_T=1.0, W_per_kg=17.5)],
                build_factor=1.5,
                note="B-H is a generic M270-35A table (not a measured curve); loss anchors are catalogue points used by both models")

limits = dict(B_tooth_tip_max_T=1.65, B_yoke_max_T=1.45,
              limits_note="design rules from T03/T03b; applied to the TRUE flux density (with stacking factor). T03 used B_gap<=0.90 T and B_yoke<=1.45 T without stacking factor.",
              friction_windage_W="0.5 kW*(n/4500)+1.0 kW*(n/4500)^3 (T03; superseded by T03d)")

g = dict(
    meta=dict(file="data/machine_geometry.json", task="R01", date=str(datetime.date.today()), owner="simulator",
              purpose="single source of truth for the T03/T03b/T03c analytic models and the T04 simulation; derived section written by 03_simulation/compute_R01.py",
              based_on="T03 stator: 48 slots, pitch 7, 3 turns/coil, R_gap 165 mm, L_stk 360 mm, R_out 235 mm, slot 9 x 45 mm, yoke 25 mm"),
    stator=stator, winding=winding, airgap=airgap, rotor_im=rotor_im, rotor_wrsm=rotor_wrsm, material=material, limits=limits,
    notes=[
        "Copper: 6 hairpin-type conductors of 7.5 x 5.4 mm bare (40.5 mm2) per slot = the T03 turn area, so R_coil (2.155 mOhm at 120 C) and copper mass (62.9 kg, T03b constraint) are unchanged.",
        "Slot fill 0.60 of the gross 9 x 45 mm slot (0.86 of the insulated window), current density 7.7 A/mm2 at 310 A and 6.6 A/mm2 at 266 A (oil-cooled, as T03).",
        "Radial slot layout from the bottom: liner 0.5, bottom layer 17.7, separator 1.0, top layer 17.7, air/wedge 6.6, tooth tip 1.5 = 45 mm. The 6.6 mm above the conductors is not copper: it counts in slot leakage.",
        "Teeth are parallel-slot (tapered): 12.6 mm at the bore, 18.5 mm at the root. B limit is checked at the tip; the iron MMF uses the width at one third of the height (14.6 mm).",
        "Air gap 1.0 mm mechanical for the IM; k_c from stator and rotor slot openings; saturation is NOT in g_eff (T03 used k_c*k_sat = 1.3).",
        "End winding: length 1.2*pi*D_mid*y/Q + 2*20 mm per side and lambda_end 0.3 are T03 values, not verified by this work.",
        "Rotor cage: 58 rectangular bars 7.0 x 21.4 mm, 1 mm bridge, copper rings 600 mm2 at 270 mm mean diameter (T03/T03b values; the bar shape is new but its area is unchanged).",
        "WRSM rotor: 8 salient poles, 50 mm pole body, 55 mm deep interpolar slots, shaft radius 40 mm; the air gap and field winding are set in the derived section (compute_R01.py), because the IM gap does not give a physical WRSM.",
    ],
)
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
json.dump(g, open(os.path.join(ROOT, "data", "machine_geometry.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in winding.items() if isinstance(v, float)}, indent=0))
print(airgap, stator["tooth_width_tip_m"], stator["tooth_width_root_m"], rotor_im["lambda_bar"], winding["top_air_m"])
