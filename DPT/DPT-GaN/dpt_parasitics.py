"""Explicit external PCB parasitics; EPC intrinsic device model is unchanged."""
GROUPS = {
 'Power parasitics': [
  ('Refined','Use refined parasitics: 1=yes, 0=legacy','1'),
  ('Lloop','Total bulk-to-bridge PCB loop inductance (H)','600p'),
  ('Rloop','Total bulk-to-bridge PCB loop resistance (ohm)','5m'),
  ('CSI','Shared-source inductance absent from device model (H)','100p'),
  ('RCSI','Additional shared-source PCB resistance per device (ohm)','100u'),
  ('LplusFrac','Fraction of Lloop in positive feed (0..1)','0.5'),
  ('LreturnFrac','Fraction of Lloop in negative return (0..1)','0.5'),
  ('RplusFrac','Fraction of Rloop in positive feed (0..1)','0.5'),
  ('RreturnFrac','Fraction of Rloop in negative return (0..1)','0.5')],
 'Gate parasitics': [
  ('LgLS','LS gate-forward inductance (H)','500p'),
  ('LgrLS','LS private gate-return inductance (H)','500p'),
  ('RgTraceLS','LS gate-forward trace resistance (ohm)','20m'),
  ('RgrLS','LS private gate-return resistance (ohm)','20m'),
  ('LgHS','HS gate-forward inductance (H)','500p'),
  ('LgrHS','HS private gate-return inductance (H)','500p'),
  ('RgTraceHS','HS gate-forward trace resistance (ohm)','20m'),
  ('RgrHS','HS private gate-return resistance (ohm)','20m')]
}
DECOUPLING = [
 ('Cdecap','Local bridge decoupling capacitance: 0=disabled (F)','0'),
 ('ESRdecap','Local decoupling ESR (ohm)','5m'),
 ('ESLdecap','Local decoupling ESL (H)','200p')]
# Existing parameters Lloop/Rloop/CSI retain their meanings and values on migration.
NEW_DEFAULTS={k:v for rows in [*GROUPS.values(),DECOUPLING] for k,_,v in rows if k not in {'Lloop','Rloop','CSI'}}
LEGACY_DEFAULTS={k:'0' for k in NEW_DEFAULTS}
LEGACY_DEFAULTS.update(LplusFrac='1',RplusFrac='1',ESRdecap='5m',ESLdecap='200p')
FRACTIONS={'LplusFrac','LreturnFrac','RplusFrac','RreturnFrac'}


def refine_parts(parts):
    out=[]
    for kind,name,nodes,value,extra in parts:
        nodes=list(nodes)
        if name=='Llayout':
            value='{max(Lloop*LplusFrac,1e-15)}';extra='Rser={Rloop*RplusFrac}'
        elif name=='Lsh':nodes=['sh','hs_ref'];extra='Rser={RCSI}'
        elif name=='Lsl':nodes=['sl','pgnd'];extra='Rser={RCSI}'
        elif name=='Vhs':nodes=['offhs','hret']
        elif name=='Rhs':nodes=['offhs','hdrive']
        elif name in {'Von','Voff'}:nodes=[nodes[0],'lret']
        elif name in {'Rup','Rdown'}:nodes=[nodes[0],'ldrive']
        out.append((kind,name,nodes,value,extra))
    out += [
      ('ind','Lmid',['hs_ref','sw'],'{max(Lloop*(1-LplusFrac-LreturnFrac),1e-15)}','Rser={Rloop*max(1-RplusFrac-RreturnFrac,0)}'),
      ('ind','Lreturn',['pgnd','0'],'{max(Lloop*LreturnFrac,1e-15)}','Rser={Rloop*RreturnFrac}'),
      ('ind','LgateLS',['ldrive','gl'],'{max(LgLS,1e-15)}','Rser={RgTraceLS}'),
      ('ind','LgateReturnLS',['lret','pgnd'],'{max(LgrLS,1e-15)}','Rser={RgrLS}'),
      ('ind','LgateHS',['hdrive','gh'],'{max(LgHS,1e-15)}','Rser={RgTraceHS}'),
      ('ind','LgateReturnHS',['hret','hs_ref'],'{max(LgrHS,1e-15)}','Rser={RgrHS}')]
    return out


def decoupling_parts():
    return [
      ('res','Rdecap',['rail','decap_esl'],'{ESRdecap}',''),
      ('ind','Ldecap',['decap_esl','decap'],'{max(ESLdecap,1e-15)}','Rser=0'),
      ('cap','Cdecap',['decap','pgnd'],'{Cdecap}','')]

NOTES = {
 'DC link & layout': 'Cin is the bulk capacitor. Optional local decoupling connects rail to the bridge return, with its own ESR/ESL. Enter effective capacitance at DC bias. Zero disables this branch; re-export after enabling it.',
 'Power parasitics': 'Defaults split external layout L/R equally between the upper positive feed and lower return, with zero middle-path allocation. Equal parasitics do not guarantee equal DPT voltage stress. The remaining L/R fractions form the HS-source-to-DUT switch-node path. Lloop excludes capacitor ESL and shared-source inductance. Default total loop budget is 1 nH including 0.2 nH capacitor ESL and 2 x 0.1 nH CSI, informed by EPC layout examples. Allocation fractions are assumptions; see FAST-PRESET-NOTES.md. Legacy mode keeps the original circuit and ignores the new controls.',
 'Gate parasitics': 'Private gate-forward and gate-return paths are separate from shared-source CSI. These values are illustrative PCB assumptions. EPC internal gate resistance and device losses remain in the vendor model; do not add them again.'
}
