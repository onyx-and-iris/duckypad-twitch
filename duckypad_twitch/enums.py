from enum import IntEnum

Buttons = IntEnum('Buttons', 'mute_mics only_discord only_stream', start=0)

Strips = IntEnum('Strips', 'onyx_mic iris_mic onyx_pc iris_pc', start=0)
Buses = IntEnum('Buses', 'MR18 ASIO[1,2] ASIO[3,4] ASIO[5,6] ASIO[7,8] onyx_mic iris_mic both_mics', start=5)
