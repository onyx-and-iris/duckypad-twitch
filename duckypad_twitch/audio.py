import logging

import time
import vban_cmd

from . import configuration
from .layer import ILayer
from .states import AudioState
from .enums import Buttons, Strips
from .util import ensure_mixer_fadeout

logger = logging.getLogger(__name__)


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
                vban.vban.instream[0].on = True
            with vban_cmd.api('potato', outbound=True, **iris_conn) as vban:
                vban.strip[0].apply(params)
                vban.vban.instream[0].on = True

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
            self.vm.strip[Strips.onyx_mic].apply({'A1': True, 'B1': False, 'B3': False, 'mute': False})
            self.vm.strip[Strips.iris_mic].apply({'A1': True, 'B2': False, 'B3': False, 'mute': False})
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
            self.vm.strip[Strips.onyx_mic].apply({'A1': False, 'B1': True, 'B3': True, 'mute': True})
            self.vm.strip[Strips.iris_mic].apply({'A1': False, 'B2': True, 'B3': True, 'mute': True})
            self.logger.info('Sound Test Disabled')

    @ensure_mixer_fadeout
    def stage_onyx_mic(self):
        """Gain stage SE Electronics DCM8 with phantom power"""
        self.mixer.headamp[10].phantom = True
        for i in range(21):
            self.mixer.headamp[10].gain = i
            time.sleep(0.1)
        self.logger.info('Onyx Mic Staged with Phantom Power')

    @ensure_mixer_fadeout
    def stage_iris_mic(self):
        """Gain stage TLM102 with phantom power"""
        self.mixer.headamp[11].phantom = True
        for i in range(31):
            self.mixer.headamp[11].gain = i
            time.sleep(0.1)
        self.logger.info('Iris Mic Staged with Phantom Power')

    def unstage_onyx_mic(self):
        """Unstage SE Electronics DCM8 and disable phantom power"""
        for i in reversed(range(21)):
            self.mixer.headamp[10].gain = i
            time.sleep(0.1)
        self.mixer.headamp[10].phantom = False
        self.logger.info('Onyx Mic Unstaged and Phantom Power Disabled')

    def unstage_iris_mic(self):
        """Unstage TLM102 and disable phantom power"""
        for i in reversed(range(31)):
            self.mixer.headamp[11].gain = i
            time.sleep(0.1)
        self.mixer.headamp[11].phantom = False
        self.logger.info('Iris Mic Unstaged and Phantom Power Disabled')

    def solo_onyx(self):
        """placeholder method"""

    def solo_iris(self):
        """placeholder method"""

    def _fade_mixer(self, target_fader, fade_in=True):
        """Fade the mixer's fader to the target level."""
        current_fader = self.mixer.lr.mix.fader
        step = 1 if fade_in else -1
        while (fade_in and current_fader < target_fader) or (not fade_in and current_fader > target_fader):
            current_fader += step
            self.mixer.lr.mix.fader = current_fader
            time.sleep(0.05)

    def _toggle_workstation_routing(self, state_attr, target_name, vban_config_key):
        """Toggle routing of workstation audio to either Onyx or Iris via VBAN."""

        current_state = getattr(self.state, state_attr)
        new_state = not current_state
        setattr(self.state, state_attr, new_state)

        target_conn = configuration.get(vban_config_key)

        if new_state:
            with vban_cmd.api('potato', outbound=True, **target_conn) as vban:
                vban.vban.instream[1].on = True
            self.vm.strip[5].gain = -6
            self.vm.vban.outstream[2].on = True
            self._fade_mixer(-90, fade_in=False)
            self.logger.info(f'Workstation audio routed to {target_name}')
        else:
            with vban_cmd.api('potato', outbound=True, **target_conn) as vban:
                vban.vban.instream[0].on = False
            self.vm.strip[5].gain = 0
            self.vm.vban.outstream[2].on = False
            self._fade_mixer(-36, fade_in=True)
            self.logger.info('Workstation audio routed back to monitor speakers')

    def toggle_workstation_to_onyx(self):
        self._toggle_workstation_routing('ws_to_onyx', 'Onyx', 'vban_onyx')

    def toggle_workstation_to_iris(self):
        self._toggle_workstation_routing('ws_to_iris', 'Iris', 'vban_iris')

    def _toggle_tv_routing(self, state_attr, target_name, vban_config_key):
        """Toggle routing of TV audio to either Onyx or Iris via VBAN."""
        current_state = getattr(self.state, state_attr)
        new_state = not current_state
        setattr(self.state, state_attr, new_state)

        target_conn = configuration.get(vban_config_key)
        tv_conn = configuration.get('vban_tv')

        if new_state:
            with (
                vban_cmd.api('banana', outbound=True, **tv_conn) as vban_tv,
                vban_cmd.api('potato', outbound=True, **target_conn) as vban_target,
            ):
                vban_tv.strip[3].A1 = False
                vban_tv.strip[3].gain = -6
                vban_tv.vban.outstream[0].on = True
                vban_target.vban.instream[2].on = True
            self.logger.info(f'TV audio routed to {target_name}')
        else:
            with (
                vban_cmd.api('banana', outbound=True, **tv_conn) as vban_tv,
                vban_cmd.api('potato', outbound=True, **target_conn) as vban_target,
            ):
                vban_tv.strip[3].A1 = True
                vban_tv.strip[3].gain = 0
                vban_tv.vban.outstream[0].on = False
                vban_target.vban.instream[2].on = False
            self.logger.info(f'TV audio routing to {target_name} disabled')

    def toggle_tv_audio_to_onyx(self):
        self._toggle_tv_routing('tv_to_onyx', 'Onyx', 'vban_onyx')

    def toggle_tv_audio_to_iris(self):
        self._toggle_tv_routing('tv_to_iris', 'Iris', 'vban_iris')
