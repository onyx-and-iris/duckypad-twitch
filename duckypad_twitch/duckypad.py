import logging

from .audio import Audio
from .obsws import OBSWS
from .scene import Scene
from .states import StreamState
from .streamlabs import StreamlabsController

logger = logging.getLogger(__name__)


class DuckyPad:
    """base DuckyPad class"""

    def __init__(self, **kwargs):
        self.logger = logger.getChild(__class__.__name__)
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.stream = StreamState()
        self.audio = Audio(self, vm=self.vm, mixer=self.mixer)
        self.scene = Scene(self, vm=self.vm)
        self.obsws = OBSWS(self)
        self.streamlabs_controller = StreamlabsController(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_value, exc_type, traceback):
        self.streamlabs_controller.conn.disconnect()
        self.obsws.disconnect()

    def reset(self):
        """
        apply streaming config,
        then apply current scene settings
        if stream is live enable both mics over vban
        """
        self.vm.apply_config('streaming')
        self.audio.reset_states()
        if self.stream.current_scene:
            self.logger.debug(f'Running function for current scene {self.stream.current_scene}')
            fn = getattr(
                self.scene,
                '_'.join([word.lower() for word in self.stream.current_scene.split()]),
            )
            fn()
        if self.stream.is_live:
            self.logger.debug('stream is live, enabling both mics over vban')
            self.vm.vban.outstream[0].on = True
            self.vm.vban.outstream[1].on = True
        else:
            self.logger.debug('stream is not live. Leaving both vban outstreams disabled')


def connect(*args, **kwargs):
    DuckyPad_cls = DuckyPad
    return DuckyPad_cls(*args, **kwargs)
