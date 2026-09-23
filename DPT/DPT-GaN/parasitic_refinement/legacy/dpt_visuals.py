"""Live DPT schematic and periodic half-bridge conduction estimates."""
import tkinter as tk

FIELDS = [
 ('Icond', 'RMS current within each ON interval (A)', '16'),
 ('DutyLS', 'Low-side ON fraction of full cycle', '0.5'),
 ('DutyHS', 'High-side ON fraction of full cycle', '0.5'),
 ('RdsLS', 'Low-side Rds(on) at operating temperature (ohm)', '2m'),
 ('RdsHS', 'High-side Rds(on) at operating temperature (ohm)', '2m'),
]

def conduction_loss(values, number):
    current=number(values.get('Icond',values['Itest']))
    dl=number(values.get('DutyLS','0.5'));dh=number(values.get('DutyHS','0.5'))
    rl=number(values.get('RdsLS','2m'));rh=number(values.get('RdsHS','2m'))
    if min(current,dl,dh)<0 or max(dl,dh)>1 or dl+dh>1+1e-12 or min(rl,rh)<=0:
        raise ValueError('Conduction current must be nonnegative, Rds positive, and ON fractions between 0 and 1 with sum <= 1.')
    low=current*current*dl*rl;high=current*current*dh*rh
    return low,high,low+high

class SetupDiagram(tk.Canvas):
    def __init__(self,parent,values):
        super().__init__(parent,bg='#f7fafc',highlightthickness=0)
        self.values=values
        self.bind('<Configure>',lambda event:self.redraw())
    def redraw(self):
        self.delete('all');v=self.values()
        s=min(max(self.winfo_width(),100)/940,max(self.winfo_height(),100)/410)
        def line(*pts):self.create_line(*[z*s for z in pts],fill='#334a60',width=2)
        def text(x,y,label,**kw):self.create_text(x*s,y*s,text=label,font=('Segoe UI',max(7,int(10*s))),fill='#25394d',**kw)
        def block(x,y,w,h,label):
            self.create_rectangle(x*s,y*s,(x+w)*s,(y+h)*s,fill='white',outline='#5482a0',width=2)
            text(x+w/2,y+h/2,label)
        def dot(x,y):self.create_oval((x-3)*s,(y-3)*s,(x+3)*s,(y+3)*s,fill='#334a60',outline='')
        text(20,17,'DPT setup — live values; gate-driver and parasitic blocks simplified',anchor='w')
        line(75,150,75,55,115,55);block(115,40,100,30,'Rcharge '+v['Rcharge']);line(215,55,330,55)
        self.create_oval(50*s,150*s,100*s,200*s,outline='#5482a0',width=2)
        text(75,164,'+');text(75,186,'−');text(22,224,'Vdc '+v['Vin']+' V',anchor='w')
        line(75,200,75,370,830,370)
        line(265,55,265,95);block(228,95,74,30,'ESR '+v['ESR'])
        line(265,125,265,150);block(228,150,74,30,'ESL '+v['ESL'])
        line(265,180,265,224);line(246,224,284,224);line(246,232,284,232);line(265,232,265,370)
        text(285,247,'Cin '+v['Cin']+' F',anchor='w');dot(265,55);text(265,36,'bus')
        block(330,40,160,30,'Lloop '+v['Lloop']+' H');text(410,87,'series Rloop '+v['Rloop']+' ohm')
        line(490,55,830,55);dot(620,55);text(642,38,'rail')
        line(620,55,620,113);block(585,113,70,44,'QHS')
        line(620,157,620,171);block(585,171,70,26,'CSI '+v['CSI']);line(620,197,620,220)
        line(830,55,830,123);block(782,123,96,55,'Lload\n'+v['Lload']+' H')
        text(850,190,'Rload '+v['Rload'],anchor='w');line(830,178,830,220,620,220)
        dot(620,220);text(664,232,'sw',anchor='w')
        line(620,220,620,239);block(585,239,70,24,'Vsense=0')
        line(620,263,620,275);block(585,275,70,42,'QLS / DUT')
        line(620,317,620,330);block(585,330,70,24,'CSI '+v['CSI']);line(620,354,620,370)
        dot(620,370);line(620,370,620,380);line(604,380,636,380);line(609,386,631,386);line(615,392,625,392)
        block(372,116,155,44,'HS held OFF\nVoff='+v['Voff']+' V');line(527,136,585,136)
        text(551,103,'RgHS '+v['Rg_HS']);text(445,179,'Return: sw (after CSI)')
        block(365,267,170,58,'Two-pulse driver\nRg on/off: '+v['Rg_on']+' / '+v['Rg_off']);line(535,296,585,296)
        text(448,346,'Return: ground (after CSI)')
        text(785,305,'Vds HS: rail − sh\nVds LS: drain − sl\nBoth devices: EPC2361')
        text(22,399,'Upper reverse conduction during the off interval. Diagram represents the DPT, not continuous PWM.',anchor='w')
