import logging

from .enums import VMStrips
from .layer import ILayer
from .states import SceneState

logger = logging.getLogger(__name__)


class Scene(ILayer):
    """Scene concrete class"""

    def __init__(self, duckypad, **kwargs):
        super().__init__(duckypad)
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.reset_states()

    @property
    def identifier(self):
        return type(self).__name__

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val

    def reset_states(self):
        self._state = SceneState()

    def start(self):
        self.vm.strip[VMStrips.onyx_pc].mute = True
        self.vm.strip[VMStrips.iris_pc].mute = True
        self.obsws.switch_to_scene('START')

    def dual_stream(self):
        ENABLE_PC = {
            'mute': False,
            'A5': True,
            'gain': 0,
        }
        self.vm.strip[VMStrips.onyx_pc].apply(ENABLE_PC)
        self.vm.strip[VMStrips.iris_pc].apply(ENABLE_PC)
        self.obsws.switch_to_scene('DUAL STREAM')

    def brb(self):
        self.vm.strip[VMStrips.onyx_pc].mute = True
        self.vm.strip[VMStrips.iris_pc].mute = True
        self.obsws.switch_to_scene('BRB')

    def end(self):
        self.vm.strip[VMStrips.onyx_pc].mute = True
        self.vm.strip[VMStrips.iris_pc].mute = True
        self.obsws.switch_to_scene('END')

    def onyx_solo(self):
        self.vm.strip[VMStrips.onyx_pc].mute = False
        self.vm.strip[VMStrips.iris_pc].mute = True
        self.obsws.switch_to_scene('ONYX SOLO')

    def iris_solo(self):
        self.vm.strip[VMStrips.onyx_pc].mute = True
        self.vm.strip[VMStrips.iris_pc].mute = False
        self.obsws.switch_to_scene('IRIS SOLO')
