import logging

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

    def onyx_only(self):
        if self._duckypad.streamlabs_controller.switch_scene('onyx_only'):
            self.vm.strip[2].mute = False
            self.vm.strip[3].mute = True
            self.logger.info('Only Onyx Scene enabled, Iris game pc muted')

    def iris_only(self):
        if self._duckypad.streamlabs_controller.switch_scene('iris_only'):
            self.vm.strip[2].mute = True
            self.vm.strip[3].mute = False
            self.logger.info('Only Iris Scene enabled, Onyx game pc muted')

    def dual_scene(self):
        if self._duckypad.streamlabs_controller.switch_scene('dual_scene'):
            self.vm.strip[2].apply({'mute': False, 'gain': 0})
            self.vm.strip[3].apply({'A5': True, 'mute': False, 'gain': 0})
            self.logger.info('Dual Scene enabled')

    def onyx_big(self):
        if self._duckypad.streamlabs_controller.switch_scene('onyx_big'):
            self.vm.strip[2].apply({'mute': False, 'gain': 0})
            self.vm.strip[3].apply({'mute': False, 'gain': -3})
            self.logger.info('Onyx Big scene enabled')

    def iris_big(self):
        if self._duckypad.streamlabs_controller.switch_scene('iris_big'):
            self.vm.strip[2].apply({'mute': False, 'gain': -3})
            self.vm.strip[3].apply({'mute': False, 'gain': 0})
            self.logger.info('Iris Big enabled')

    def start(self):
        if self._duckypad.streamlabs_controller.switch_scene('start'):
            self.vm.strip[2].mute = True
            self.vm.strip[3].mute = True
            self.logger.info('Start scene enabled.. ready to go live!')

    def brb(self):
        if self._duckypad.streamlabs_controller.switch_scene('brb'):
            self.vm.strip[2].mute = True
            self.vm.strip[3].mute = True
            self.logger.info('BRB: game pcs muted')

    def end(self):
        if self._duckypad.streamlabs_controller.switch_scene('end'):
            self.vm.strip[2].mute = True
            self.vm.strip[3].mute = True
            self.logger.info('End scene enabled.')
