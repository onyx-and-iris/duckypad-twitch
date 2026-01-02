from enum import IntEnum

Buttons = IntEnum('Buttons', 'mute_mics only_discord only_stream', start=0)

# Voicemeeter Channels
VMStrips = IntEnum('Strips', 'onyx_mic iris_mic onyx_pc iris_pc st_input_5 system comms pretzel', start=0)
VMBuses = IntEnum('Buses', 'onyx_mic iris_mic both_mics', start=5)

# VBAN Channels
VBANChannels = IntEnum('VBANChannels', 'onyx_mic iris_mic comms workstation', start=0)


# XAir Channels
class XAirStrips(IntEnum):
    system = 0
    comms = 2
    pretzel = 4
    game_pcs = 6
    onyx_mic = 10
    iris_mic = 11


class XAirBuses(IntEnum):
    onyx_mix = 0
    iris_mix = 2
    stream_mix = 4
