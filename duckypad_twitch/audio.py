import logging
from enum import IntEnum

import time
import vban_cmd

from . import configuration
from .layer import ILayer
from .states import AudioState

logger = logging.getLogger(__name__)


Buttons = IntEnum('Buttons', 'mute_mics only_discord only_stream', start=0)


class Audio(ILayer):
    """Audio concrete class"""

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
        self.state = AudioState()
        for button in Buttons:
            self.vm.button[button].stateonly = getattr(AudioState, button.name)

    def mute_mics(self):
        self.state.mute_mics = not self.state.mute_mics
        if self.state.mute_mics:
            self.vm.strip[0].mute = True
            self.vm.strip[1].mute = True
            self.vm.strip[4].mute = True
            self.logger.info('Mics Muted')
        else:
            self.vm.strip[0].mute = False
            self.vm.strip[1].mute = False
            self.vm.strip[4].mute = False
            self.logger.info('Mics Unmuted')
        self.vm.button[Buttons.mute_mics].stateonly = self.state.mute_mics

    def only_discord(self):
        self.state.only_discord = not self.state.only_discord
        if self.state.only_discord:
            self.mixer.dca[0].on = False
            self.vm.strip[4].mute = True
            self.logger.info('Only Discord Enabled')
        else:
            self.vm.strip[4].mute = False
            self.mixer.dca[0].on = True
            self.logger.info('Only Discord Disabled')
        self.vm.button[Buttons.only_discord].stateonly = self.state.only_discord

    def only_stream(self):
        self.state.only_stream = not self.state.only_stream
        if self.state.only_stream:
            self.vm.bus[5].mute = True
            self.vm.bus[6].mute = True
            self.vm.strip[2].gain = -3
            self.vm.strip[3].gain = -3
            self.vm.strip[6].gain = -3
            self.logger.info('Only Stream Enabled')
        else:
            self.vm.strip[2].gain = 0
            self.vm.strip[3].gain = 0
            self.vm.strip[6].gain = 0
            self.vm.bus[5].mute = False
            self.vm.bus[6].mute = False
            self.logger.info('Only Stream Disabled')
        self.vm.button[Buttons.only_stream].stateonly = self.state.only_stream

    def sound_test(self):
        def toggle_soundtest(params):
            onyx_conn = configuration.get('vban_onyx')
            iris_conn = configuration.get('vban_iris')
            assert all([onyx_conn, iris_conn]), 'expected configurations for onyx_conn, iris_conn'

            with vban_cmd.api('potato', outbound=True, **onyx_conn) as vban:
                vban.strip[0].apply(params)
            with vban_cmd.api('potato', outbound=True, **iris_conn) as vban:
                vban.strip[0].apply(params)

        ENABLE_SOUNDTEST = {
            'A1': True,
            'A2': True,
            'B1': False,
            'B2': False,
            'mono': True,
        }
        DISABLE_SOUNDTEST = {
            'A1': False,
            'A2': False,
            'B1': True,
            'B2': True,
            'mono': False,
        }

        self.state.sound_test = not self.state.sound_test
        if self.state.sound_test:
            self.vm.strip[4].apply({'B3': False, 'A1': True, 'mute': False})
            self.vm.vban.outstream[0].on = True
            self.vm.vban.outstream[1].on = True
            self.vm.vban.outstream[0].route = 0
            self.vm.vban.outstream[1].route = 0
            toggle_soundtest(ENABLE_SOUNDTEST)
            self.logger.info('Sound Test Enabled')
        else:
            toggle_soundtest(DISABLE_SOUNDTEST)
            self.vm.vban.outstream[0].route = 5
            self.vm.vban.outstream[1].route = 6
            self.vm.strip[4].apply({'B3': True, 'A1': False, 'mute': True})
            self.logger.info('Sound Test Disabled')

    def solo_onyx(self):
        """placeholder method."""

    def solo_iris(self):
        """placeholder method."""

    def toggle_workstation_to_onyx(self):
        self.state.ws_to_onyx = not self.state.ws_to_onyx
        onyx_conn = configuration.get('vban_onyx')
        if self.state.ws_to_onyx:
            with vban_cmd.api('potato', outbound=True, **onyx_conn) as vban:
                vban.vban.instream[0].on = True
            self.vm.strip[5].gain = -6
            self.vm.vban.outstream[2].on = True

            # Fade out the workstation
            current_fader = self.mixer.lr.mix.fader
            while current_fader > -90:
                current_fader -= 1
                self.mixer.lr.mix.fader = current_fader
                time.sleep(0.05)
        else:
            with vban_cmd.api('potato', outbound=True, **onyx_conn) as vban:
                vban.vban.instream[0].on = False
            self.vm.strip[5].gain = 0
            self.vm.vban.outstream[2].on = False

            # Fade in the workstation
            current_fader = self.mixer.lr.mix.fader
            while current_fader < -36:
                current_fader += 1
                self.mixer.lr.mix.fader = current_fader
                time.sleep(0.05)
