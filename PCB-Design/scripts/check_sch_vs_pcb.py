"""
Compare the netlist exported from the KiCad schematic with the pad nets of the routed PCB.
The comparison is by connectivity: every schematic net must contain exactly the pins of one PCB net (and the other
way round). Where the schematic net carries a label, its name must also equal the PCB net name.

    kicad-cli sch export netlist --format kicadsexpr -o <tmp>/sch.net hardware/spb-bb-fab/spb-bb-fab.kicad_sch
    python scripts/check_sch_vs_pcb.py <tmp>/sch.net
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pcb = {r: p for r, v, p in json.load(open(os.path.join(ROOT, "hardware", "spb-bb-fab", "pad_nets.json")))}
txt = open(sys.argv[1], encoding="utf-8").read()
sch_groups = {}
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)\)\s*(?=\(net |\)\s*\)\s*$)', txt, re.S):
    name = m.group(1).lstrip("/")
    pins = set((n.group(1), n.group(2)) for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
    sch_groups[name] = pins
pcb_groups = collections.defaultdict(set)
for ref, pads in pcb.items():
    for pin, net in pads.items():
        if net:
            pcb_groups[net].add((ref, pin))
pin2pcb = {(r, p): n for r, pads in pcb.items() for p, n in pads.items()}
bad = 0
seen = set()
for name, pins in sch_groups.items():
    nets = set(pin2pcb.get(p, "?") for p in pins)
    if nets == {""}:
        continue                                  # unconnected on both
    if len(nets) != 1 or "" in nets or "?" in nets:
        print("SCH net %s joins PCB nets %s: %s" % (name, sorted(nets), sorted(pins)))
        bad += 1
        continue
    n = nets.pop()
    if pcb_groups[n] != pins:
        print("SCH net %s has %d of %d pins of PCB net %s; missing %s" % (
            name, len(pins), len(pcb_groups[n]), n, sorted(pcb_groups[n] - pins)[:6]))
        bad += 1
    elif not (name.startswith("Net-(") or name.startswith("unconnected-")) and name != n:
        print("SCH label %s on PCB net %s" % (name, n))
        bad += 1
    seen.add(n)
for n in pcb_groups:
    if n not in seen and len(pcb_groups[n]) > 0 and not any(pcb_groups[n] == g for g in sch_groups.values()):
        print("PCB net %s not reproduced in the schematic" % n)
        bad += 1
refs_sch = set(r for g in sch_groups.values() for r, _ in g)
print("checked %d PCB nets, %d schematic nets, %d parts with pins: %d problems" % (
    len(pcb_groups), len(sch_groups), len(refs_sch), bad))
sys.exit(1 if bad else 0)
