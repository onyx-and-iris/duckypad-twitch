import logging

from .audio import Audio
from .obsws import OBSWS
from .scene import Scene
from .states import StreamState
from .util import to_snakecase

logger = logging.getLogger(__name__)


class DuckyPad:
    """base DuckyPad class"""

    def __init__(self, **kwargs):
        self.logger = logger.getChild(__class__.__name__)
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.stream = StreamState()
        self.obsws = OBSWS(self)
        self.audio = Audio(self, vm=self.vm, mixer=self.mixer)
        self.scene = Scene(self, vm=self.vm, obsws=self.obsws)

    def __enter__(self):
        return self

    def __exit__(self, exc_value, exc_type, exc_tb):
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
            try:
                fn = getattr(
                    self.scene,
                    to_snakecase(self.stream.current_scene),
                )
                fn()
            except AttributeError:
                self.logger.warning(f'No function found for scene {self.stream.current_scene}')
        if self.stream.is_live:
            self.logger.debug('stream is live, enabling both mics over vban')
            self.vm.vban.outstream[0].on = True
            self.vm.vban.outstream[1].on = True
        else:
            self.logger.debug('stream is not live. Leaving both vban outstreams disabled')


def connect(*args, **kwargs):
    DuckyPad_cls = DuckyPad
    return DuckyPad_cls(*args, **kwargs)
