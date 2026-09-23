"""Parameter editor for the supplied EPC LTspice schematic. Standard library only."""
from pathlib import Path
import math
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASE = Path(__file__).resolve().parent
PARAMS = {
    'Vin': 'DC supply voltage (V)', 'dutyCycle': 'Duty cycle (0 to 1)',
    'Iout': 'Target output current (A)', 'freq': 'Switching frequency (Hz)',
    'tdead': 'Dead time (s)', 'Tj1': 'Device temperature (deg C)',
    'RGD_PU': 'Driver pull-up resistance (ohm)',
    'RGD_PD': 'Driver pull-down resistance (ohm)',
    'CSI': 'Common-source inductance (H)', 'CSI_DISABLE': 'Bypass CSI (0 or 1)',
}
COMPONENTS = {
    'L1': 'Output inductance (H)', 'C1': 'Output capacitance (F)',
    'R12': 'High-side turn-on gate resistor (ohm)',
    'R11': 'High-side turn-off gate resistor (ohm)',
    'R22': 'Low-side turn-on gate resistor (ohm)',
    'R21': 'Low-side turn-off gate resistor (ohm)',
    'V15': 'High-side driver supply (V)', 'V25': 'Low-side driver supply (V)',
}

def read_text(path):
    data = Path(path).read_bytes()
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise ValueError('Unsupported file encoding')

def number(value):
    match = re.fullmatch(r'\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(meg|[tgkmunpfµμ]?)(?:[a-zA-Z]*)\s*', value, re.I)
    if not match:
        raise ValueError('Use a number with an optional SPICE suffix, e.g. 48, 500k, 10n, 100pH.')
    scales = {'': 1, 't': 1e12, 'g': 1e9, 'meg': 1e6, 'k': 1e3, 'm': 1e-3,
              'u': 1e-6, 'µ': 1e-6, 'μ': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15}
    result = float(match[1]) * scales[match[2].lower()]
    if not math.isfinite(result):
        raise ValueError('Value must be finite.')
    return result

def parameters(text):
    result = {}
    for line in text.splitlines():
        if re.match(r'TEXT .* !\.param\s', line, re.I):
            result.update(re.findall(r'(\w+)\s*=\s*([^\s]+)', line))
    return result

def component_values(text):
    result = {}
    for block in re.split(r'(?m)(?=^SYMBOL )', text):
        name = re.search(r'(?m)^SYMATTR InstName (\S+)', block)
        value = re.search(r'(?m)^SYMATTR Value ([^\r\n]+)', block)
        if name and value:
            result[name[1]] = value[1]
    return result

def render(text, params, components):
    lines = []
    for line in text.splitlines(keepends=True):
        if re.match(r'TEXT .* !\.param\s', line, re.I):
            for key, value in params.items():
                line = re.sub(r'(?<!\w)' + re.escape(key) + r'\s*=\s*[^\s]+',
                              lambda m, k=key, v=value: k + '=' + v, line)
        if re.match(r'TEXT .* !\.include\s', line, re.I) and 'epcganlibrary.lib' in line.lower():
            line = re.sub(r'!\.include[^\r\n]*', '!.include "EPCGaNLibrary.lib"', line, flags=re.I)
        lines.append(line)
    blocks = re.split(r'(?m)(?=^SYMBOL )', ''.join(lines))
    for i, block in enumerate(blocks):
        name = re.search(r'(?m)^SYMATTR InstName (\S+)', block)
        if name and name[1] in components:
            blocks[i] = re.sub(r'(?m)^SYMATTR Value [^\r\n]+',
                               lambda m: 'SYMATTR Value ' + components[name[1]], block)
    return ''.join(blocks)

def validate(params, components):
    p = {k: number(v) for k, v in params.items()}
    for key, val in p.items():
        if key not in ('Tj1', 'CSI_DISABLE', 'tdead') and val <= 0:
            raise ValueError(f'{key} must be greater than zero.')
    if not 0 < p['dutyCycle'] < 1:
        raise ValueError('Duty cycle must be between 0 and 1.')
    if p['tdead'] < 0 or 1 / p['freq'] * (1 - p['dutyCycle']) - 2 * p['tdead'] <= 0:
        raise ValueError('Dead time leaves no low-side pulse. Reduce dead time or frequency.')
    if p['Tj1'] <= -273.15 or p['CSI_DISABLE'] not in (0, 1):
        raise ValueError('Temperature must exceed absolute zero; CSI bypass must be 0 or 1.')
    if 10 / p['freq'] > 0.0006:
        raise ValueError('Frequency is too low for the existing 0.6 ms transient / last 10 cycles setting.')
    for key, value in components.items():
        if number(value) <= 0:
            raise ValueError(f'{key} must be greater than zero.')

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('EPC GaN — LTspice parameter editor')
        self.geometry('790x710')
        self.minsize(700, 650)
        self.source = BASE / 'Example-EPC.asc'
        self.text, self.encoding = '', 'cp1252'
        self.params, self.components = {}, {}
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='EPC GaN circuit parameters', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        self.filename = ttk.Label(outer, wraplength=740)
        self.filename.pack(anchor='w', pady=(8, 12))
        tabs = ttk.Notebook(outer)
        tabs.pack(fill='both', expand=True)
        for title, fields, variables in [('Operating point & driver', PARAMS, self.params),
                                         ('Components', COMPONENTS, self.components)]:
            page = ttk.Frame(tabs, padding=14)
            tabs.add(page, text=title)
            page.columnconfigure(1, weight=1)
            for row, (key, label) in enumerate(fields.items()):
                ttk.Label(page, text=f'{label}  [{key}]').grid(row=row, column=0, sticky='w', pady=7)
                variables[key] = tk.StringVar()
                ttk.Entry(page, textvariable=variables[key], width=22).grid(row=row, column=1, sticky='ew', padx=(20, 0))
        ttk.Label(outer, text='SPICE suffixes: m = milli, u = micro, n = nano, p = pico, k = kilo, Meg = mega.\nBoth transistors use Tj1. Load resistance remains Vin × dutyCycle / Iout.',
                  wraplength=740).pack(anchor='w', pady=12)
        self.status = tk.StringVar(value='')
        ttk.Label(outer, textvariable=self.status, wraplength=740).pack(anchor='w', pady=4)
        actions = ttk.Frame(outer)
        actions.pack(fill='x', pady=(10, 0))
        ttk.Button(actions, text='Load schematic...', command=self.choose).pack(side='left')
        ttk.Button(actions, text='Reset values', command=self.reload).pack(side='left', padx=8)
        ttk.Button(actions, text='Save and open in LTspice', command=lambda: self.save(True)).pack(side='right')
        ttk.Button(actions, text='Save copy...', command=self.save).pack(side='right', padx=8)
        self.reload()

    def choose(self):
        filename = filedialog.askopenfilename(initialdir=self.source.parent, filetypes=[('LTspice schematic', '*.asc')])
        if filename:
            self.load(Path(filename))

    def reload(self):
        self.load(self.source)

    def load(self, source):
        try:
            text, encoding = read_text(source)
            p, c = parameters(text), component_values(text)
            missing = (set(PARAMS) - p.keys()) | (set(COMPONENTS) - c.keys())
            if missing:
                raise ValueError('This editor needs the supplied EPC circuit. Missing: ' + ', '.join(sorted(missing)))
            self.source, self.text, self.encoding = source, text, encoding
            for key, variable in self.params.items():
                variable.set(p[key])
            for key, variable in self.components.items():
                variable.set(c[key])
            self.filename.config(text=str(source))
            self.status.set('Loaded. Save a copy to apply your changes.')
        except (OSError, ValueError) as exc:
            messagebox.showerror('Could not load schematic', str(exc))

    def save(self, open_after=False):
        try:
            if not self.text:
                raise ValueError('Load the example schematic first.')
            p = {k: v.get().strip() for k, v in self.params.items()}
            c = {k: v.get().strip() for k, v in self.components.items()}
            validate(p, c)
            for name in ('EPCGaN.asy', 'EPCGaNLibrary.lib'):
                if not (self.source.parent / name).is_file():
                    raise ValueError(f'Missing {name} beside the source schematic.')
            filename = filedialog.asksaveasfilename(initialdir=self.source.parent,
                initialfile=self.source.stem + '-edited.asc', defaultextension='.asc',
                filetypes=[('LTspice schematic', '*.asc')])
            if not filename:
                return
            dest = Path(filename)
            if dest.resolve() == self.source.resolve():
                raise ValueError('Choose a new filename to preserve the source schematic.')
            for name in ('EPCGaN.asy', 'EPCGaNLibrary.lib'):
                src, target = self.source.parent / name, dest.parent / name
                if src.resolve() != target.resolve():
                    if target.exists() and target.read_bytes() != src.read_bytes():
                        raise ValueError(f'{target} already contains a different model file. Choose another folder.')
            output = render(self.text, p, c).encode(self.encoding)
            for name in ('EPCGaN.asy', 'EPCGaNLibrary.lib'):
                src, target = self.source.parent / name, dest.parent / name
                if src.resolve() != target.resolve() and not target.exists():
                    shutil.copy2(src, target)
            dest.write_bytes(output)
            self.status.set(f'Saved {dest.name}. Estimated output: {number(p["Vin"]) * number(p["dutyCycle"]):g} V')
            if open_after:
                os.startfile(str(dest))
        except (OSError, ValueError) as exc:
            messagebox.showerror('Save / open', str(exc))

if __name__ == '__main__':
    Editor().mainloop()
