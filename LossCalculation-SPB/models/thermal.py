"""Shared sink with a separate junction-to-sink branch for each device."""

def shared_sink(total_fet_w, hottest_device_w, ambient_c, junction_limit_c,
                junction_to_sink, sink_to_ambient):
    local_rise = hottest_device_w * junction_to_sink
    temperature = ambient_c + total_fet_w * sink_to_ambient + local_rise
    required = (junction_limit_c - ambient_c - local_rise) / total_fet_w
    return temperature, required