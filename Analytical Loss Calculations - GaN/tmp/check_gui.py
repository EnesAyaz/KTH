import tkinter as tk
import matplotlib.pyplot as plt
from waveform_plotter import draw_waveforms
from epc2361_loss import LossInputs
fig,axes=plt.subplots(1,2)
for _ in range(3): draw_waveforms(fig,axes,LossInputs())
assert len(fig.texts)==2
plt.close(fig)
original=tk.Tk.__init__
def hidden(self,*a,**k):
    original(self,*a,**k)
    self.withdraw()
def one_frame(self,*a,**k):
    self.update_idletasks()
    self.destroy()
tk.Tk.__init__=hidden
tk.Tk.mainloop=one_frame
import waveform_plotter,loss_calculator
waveform_plotter.main()
loss_calculator.main()
print('Both GUI layouts initialized successfully; repeated redraw passed.')
