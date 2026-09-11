"""Ideal source/sink output impedances selected by the gate command."""


def gate_path(config, point):
    if 'rg_on_ohm' not in point:
        return f"Rg drive gx {point['rg_external_ohm'] + config['driver_resistance_ohm']}"
    ron = point['rg_on_ohm'] + config['driver_source_resistance_ohm']
    roff = point['rg_off_ohm'] + config['driver_sink_resistance_ohm']
    if min(ron, roff) <= 0:
        raise ValueError('Total source/sink resistance must be positive')
    return f'Bgate drive gx I=V(drive,gx)/if(V(drive)>2.5,{ron},{roff})'
