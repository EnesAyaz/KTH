"""Regression and LTspice integration checks. Run: python test_dpt.py"""
import re
import struct
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
import dpt_gui as d

def read_log(path):
 b=path.read_bytes()
 return b.decode('utf-16-le' if b'\0' in b[:100] else 'utf-8',errors='replace')

def measures(text):
 return {k:float(v) for k,v in re.findall(r'^(\w+):[^\r\n]*?=([-+\d.eE]+)',text,re.M)}

def raw_data(path):
 b=path.read_bytes(); marker='Binary:\n'.encode('utf-16-le'); index=b.index(marker)
 header=b[:index].decode('utf-16-le')
 n=int(re.search(r'No. Variables:\s*(\d+)',header)[1])
 count=int(re.search(r'No. Points:\s*(\d+)',header)[1])
 names=re.findall(r'^\s*\d+\s+(\S+)\s+\S+',header,re.M)
 data=b[index+len(marker):]
 rows=list(struct.iter_unpack('<d'+'f'*(n-1),data))
 assert len(rows)==count
 return names,rows

class DPTTests(unittest.TestCase):
 def test_values_and_timing(self):
  self.assertAlmostEqual(d.number('100pH'),1e-10)
  self.assertAlmostEqual(d.number('1Meg'),1e6)
  self.assertAlmostEqual(d.validate(d.DEFAULTS)['T1'],16*20e-6/48)
  self.assertEqual(d.validate(dict(d.DEFAULTS,AutoT1='0',Tcharge='8u'))['T1'],8e-6)
  for key,value in [('Cin','0'),('Lloop','-1n'),('Toff','0'),('Maxstep','10n'),('AutoT1','2'),('Vin','NaN'),('Fsw','0'),('Vlimit','48'),('Vlimit','121')]:
   with self.subTest(key=key),self.assertRaises(ValueError):d.validate(dict(d.DEFAULTS,**{key:value}))
 def test_simulations(self):
  exe=d.find_ltspice()
  if not exe:self.skipTest('LTspice not installed')
  reports={}
  out=d.BASE/'dpt_validation';out.mkdir(exist_ok=True)
  for case,changes in [('default',{}),('layout_20n',{'Lloop':'20n'}),('cin_10u',{'Cin':'10u'})]:
   values=dict(d.DEFAULTS,**changes);asc=d.export(values,out/case/'DPT.asc')
   r=subprocess.run([exe,'-b',str(asc.with_suffix('.cir'))],cwd=asc.parent,timeout=45,capture_output=True)
   self.assertEqual(r.returncode,0)
   log=read_log(asc.with_suffix('.log'));m=measures(log);self.assertEqual(len(m),16)
   self.assertTrue(all(abs(v)<1e9 for v in m.values()));reports[case]=m
   if case=='default':
    names,rows=raw_data(asc.with_suffix('.raw'));cmd=names.index('V(cmd)')
    rises=sum(a[cmd]<2.5<=b[cmd] for a,b in zip(rows,rows[1:]))
    falls=sum(a[cmd]>=2.5>b[cmd] for a,b in zip(rows,rows[1:]))
    self.assertEqual((rises,falls),(2,2))
    self.assertTrue(15<m['i_first_off']<17)
    hs=[row[names.index('V(rail)')]-row[names.index('V(sh)')] for row in rows]
    self.assertAlmostEqual(max(hs),m['vds_hs_peak'],delta=0.01)
    self.assertAlmostEqual(m['eon2_uj'],m['eon2_window']*1e6,delta=1e-5)
    self.assertAlmostEqual(m['psw_dut_w'],(m['eon2_window']+m['eoff1_window'])*d.number(values['Fsw']),delta=1e-5)
    self.assertTrue(14<m['i_second_on']<17)
    subprocess.run([exe,'-netlist',str(asc)],cwd=asc.parent,timeout=20,check=True,capture_output=True)
    generated=asc.with_suffix('.net').read_text(errors='replace')
    generated=generated.replace('XXHS','XHS').replace('XXDUT','XDUT')
    parts,_,_=d.circuit(values)
    for _,name,nodes,val,extra in parts:
     expected=' '.join([name]+nodes+[val]+([extra] if extra else []))
     self.assertIn(expected,generated)
    # Simulate LTspice's own schematic netlist, separately from the GUI's netlist.
    check=asc.parent/'schematic_check.cir';check.write_text(generated)
    result=subprocess.run([exe,'-b',str(check)],cwd=check.parent,timeout=45,capture_output=True)
    self.assertEqual(result.returncode,0)
    got=measures(read_log(check.with_suffix('.log')))
    for k,v in m.items():self.assertAlmostEqual(got[k],v,delta=max(abs(v)*1e-3,1e-12))
  self.assertGreater(reports['layout_20n']['vds_peak'],reports['default']['vds_peak'])
  self.assertLess(reports['cin_10u']['i_first_off'],reports['default']['i_first_off'])
  import json
  (out/'results.json').write_text(json.dumps(reports,indent=2))
  print(reports)
 def test_results_and_legacy_settings(self):
  legacy={k:v for k,v in d.DEFAULTS.items() if k!='Fsw'}
  self.assertEqual(d.normalize_settings(legacy)['Fsw'],'500k')
  log='eon2_window: integral=2e-6\neoff1_window: integral=3e-6\neoff2_window: integral=4e-6\nvds_hs_peak: MAX(v)=125'
  rows,_=d.result_summary(log,dict(d.DEFAULTS,Fsw='100k'))
  table={label:(value,unit) for label,value,unit in rows}
  self.assertEqual(table['DUT Eon2 - second turn-on'],('2','uJ'))
  self.assertEqual(table['High-side maximum Vds'],('125','V'))
  self.assertEqual(table['Estimated DUT Psw: Eon2 + Eoff1'],('0.5','W'))
  rows,_=d.result_summary(log,dict(d.DEFAULTS,Fsw='200k'))
  self.assertEqual(dict((k,v) for k,v,u in rows)['Estimated DUT Psw: Eon2 + Eoff1'],'1')
  rows,notes=d.result_summary(log.replace('integral=2e-6','integral=-2e-6'),d.DEFAULTS)
  self.assertEqual(dict((k,v) for k,v,u in rows)['Estimated DUT Psw: Eon2 + Eoff1'],'Review energy')
  self.assertIn('negative',notes)
 def test_voltage_ceiling_and_preset(self):
  old={k:v for k,v in d.DEFAULTS.items() if k not in ('Fsw','Vlimit')}
  self.assertEqual(d.normalize_settings(old)['Vlimit'],'100')
  log='vds_peak: MAX(v)=95\nvds_hs_peak: MAX(v)=90'
  _,notes=d.result_summary(log,d.DEFAULTS)
  self.assertIn('margin 5.000 V',notes)
  _,notes=d.result_summary(log.replace('=95','=105'),d.DEFAULTS)
  self.assertIn('Exceeded.',notes)
  app=d.App();app.withdraw()
  try:
   app.load_75_50();app.update()
   self.assertEqual(app.vars['Vin'].get(),'75')
   self.assertEqual(app.vars['Itest'].get(),'50')
   d.validate(app.values())
  finally:app.destroy()
 def test_conduction_and_schematic(self):
  values=dict(d.DEFAULTS,Icond='50',DutyLS='0.5',DutyHS='0.5',RdsLS='2m',RdsHS='2m')
  self.assertEqual(d.conduction_loss(values),(2.5,2.5,5.0))
  self.assertEqual(d.conduction_loss(dict(values,DutyLS='0.25',DutyHS='0.75',RdsHS='4m')),(1.25,7.5,8.75))
  self.assertEqual(d.conduction_loss(dict(values,Icond='0')),(0,0,0))
  with self.assertRaises(ValueError):d.validate(dict(values,DutyLS='0.7',DutyHS='0.7'))
  with self.assertRaises(ValueError):d.validate(dict(values,RdsLS='0'))
  legacy={k:v for k,v in d.DEFAULTS.items() if k not in ('Icond','DutyLS','DutyHS','RdsLS','RdsHS')}
  legacy['Itest']='50'
  self.assertEqual(d.normalize_settings(legacy)['Icond'],'50')
  # Analytic assumptions must not change the simulated circuit or pulse timing.
  self.assertEqual(d.netlist(values),d.netlist(dict(values,Icond='75',DutyLS='0.3',DutyHS='0.6',RdsLS='8m')))
  rows,_=d.result_summary('vds_peak: MAX(v)=90\nvds_hs_peak: MAX(v)=80',values)
  self.assertEqual(dict((k,v) for k,v,u in rows)['Estimated half-bridge ON conduction'],'5')
  app=d.App()
  try:
   app.load_75_50();app.update()
   tabs=app.diagram.master.master;tabs.select(app.diagram.master);app.update()
   labels=[app.diagram.itemcget(i,'text') for i in app.diagram.find_all() if app.diagram.type(i)=='text']
   for label in ['QHS','QLS / DUT','Vdc 75 V','Lloop 1n H','Cin 470u F']:self.assertIn(label,labels)
   app.vars['Vin'].set('80');app.update()
   labels=[app.diagram.itemcget(i,'text') for i in app.diagram.find_all() if app.diagram.type(i)=='text']
   self.assertIn('Vdc 80 V',labels)
   for i in app.diagram.find_all():
    bounds=app.diagram.bbox(i)
    self.assertGreaterEqual(bounds[0],-3)
    self.assertLessEqual(bounds[2],app.diagram.winfo_width()+3)
  finally:app.destroy()
 def test_gui_run(self):
  app=d.App();app.withdraw()
  try:
   self.assertEqual(set(app.vars),set(d.DEFAULTS))
   app.run();deadline=time.monotonic()+50
   while app.running and time.monotonic()<deadline:app.update();time.sleep(.05)
   self.assertFalse(app.running)
   self.assertTrue(app.status.get().startswith('Completed:'),app.status.get())
  finally:app.destroy()

if __name__=='__main__':unittest.main(verbosity=2)
