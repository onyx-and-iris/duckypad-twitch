import logging
import time

import vban_cmd

from . import configuration
from .enums import Buttons, VBANChannels, VMBuses, VMStrips, XAirBuses, XAirStrips
from .layer import ILayer
from .states import AudioState
from .util import ensure_mixer_fadeout

logger = logging.getLogger(__name__)


class Audio(ILayer):
    """Audio concrete class"""

    def __init__(self, duckypad, **kwargs):
        super().__init__(duckypad)
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        self.vm.observer.add(self.on_mdirty)

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

    def on_mdirty(self):
        """Callback for Voicemeeter mdirty events.


        This method keeps the DuckyPad state in sync with changes made from the Stream Deck"""
        self.logger.debug('Voicemeeter state changed (mdirty event)')
        for button in Buttons:
            current_value = self.vm.button[button].stateonly
            if getattr(self.state, button.name) != current_value:
                match button.name:
                    case 'mute_mics':
                        if current_value:
                            self.logger.info('Mics Muted')
                        else:
                            self.logger.info('Mics Unmuted')
                    case 'only_discord':
                        if current_value:
                            self.mixer.strip[XAirStrips.comms].send[XAirBuses.stream_mix].level = -90
                            self.logger.info('Only Discord Enabled')
                        else:
                            self.mixer.strip[XAirStrips.comms].send[XAirBuses.stream_mix].level = -24
                            self.logger.info('Only Discord Disabled')
                    case 'only_stream':
                        if current_value:
                            self.logger.info('Only Stream Enabled')
                        else:
                            self.logger.info('Only Stream Disabled')
                    case 'sound_test':
                        if current_value:
                            self.logger.info('Sound Test Enabled')
                        else:
                            self.logger.info('Sound Test Disabled')
                    case 'patch_onyx':
                        if current_value:
                            self.logger.info('Onyx mic has been patched')
                        else:
                            self.logger.info('Onyx mic has been unpatched')
                    case 'patch_iris':
                        if current_value:
                            self.logger.info('Iris mic has been patched')
                        else:
                            self.logger.info('Iris mic has been unpatched')
                    case 'mute_game_pcs':
                        if current_value:
                            self.logger.info('Game PCs Muted')
                        else:
                            self.logger.info('Game PCs Unmuted')

            setattr(self.state, button.name, current_value)

    def mute_mics(self):
        self.state.mute_mics = not self.state.mute_mics
        if self.state.mute_mics:
            self.vm.strip[VMStrips.onyx_mic].mute = True
            self.vm.strip[VMStrips.iris_mic].mute = True
            self.logger.info('Mics Muted')
        else:
            self.vm.strip[VMStrips.onyx_mic].mute = False
            self.vm.strip[VMStrips.iris_mic].mute = False
            self.logger.info('Mics Unmuted')
        self.vm.button[Buttons.mute_mics].stateonly = self.state.mute_mics

    def only_discord(self):
        self.state.only_discord = not self.state.only_discord
        if self.state.only_discord:
            self.vm.bus[VMBuses.both_mics].mute = True
            self.mixer.strip[XAirStrips.comms].send[XAirBuses.stream_mix].level = -90
            self.logger.info('Only Discord Enabled')
        else:
            self.mixer.strip[XAirStrips.comms].send[XAirBuses.stream_mix].level = -24
            self.vm.bus[VMBuses.both_mics].mute = False
            self.logger.info('Only Discord Disabled')
        self.vm.button[Buttons.only_discord].stateonly = self.state.only_discord

    def only_stream(self):
        self.state.only_stream = not self.state.only_stream
        if self.state.only_stream:
            self.vm.bus[VMBuses.onyx_mic].mute = True
            self.vm.bus[VMBuses.iris_mic].mute = True
            self.vm.strip[VMStrips.onyx_pc].gain = -3
            self.vm.strip[VMStrips.iris_pc].gain = -3
            self.vm.strip[VMStrips.comms].gain = -6
            self.vm.strip[VMStrips.pretzel].gain = -3
            self.logger.info('Only Stream Enabled')
        else:
            self.vm.strip[VMStrips.onyx_pc].gain = 0
            self.vm.strip[VMStrips.iris_pc].gain = 0
            self.vm.strip[VMStrips.comms].gain = 0
            self.vm.strip[VMStrips.pretzel].gain = 0
            self.vm.bus[VMBuses.onyx_mic].mute = False
            self.vm.bus[VMBuses.iris_mic].mute = False
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
            self.vm.strip[VMStrips.onyx_mic].apply({'A1': True, 'B1': False, 'B3': False, 'mute': False})
            self.vm.strip[VMStrips.iris_mic].apply({'A1': True, 'B2': False, 'B3': False, 'mute': False})
            self.vm.vban.outstream[VBANChannels.onyx_mic].on = True
            self.vm.vban.outstream[VBANChannels.iris_mic].on = True
            self.vm.vban.outstream[VBANChannels.onyx_mic].route = 0
            self.vm.vban.outstream[VBANChannels.iris_mic].route = 0
            toggle_soundtest(ENABLE_SOUNDTEST)
            self.logger.info('Sound Test Enabled')
        else:
            toggle_soundtest(DISABLE_SOUNDTEST)
            self.vm.vban.outstream[VBANChannels.onyx_mic].route = 5
            self.vm.vban.outstream[VBANChannels.iris_mic].route = 6
            self.vm.strip[VMStrips.onyx_mic].apply({'A1': False, 'B1': True, 'B3': True, 'mute': True})
            self.vm.strip[VMStrips.iris_mic].apply({'A1': False, 'B2': True, 'B3': True, 'mute': True})
            self.logger.info('Sound Test Disabled')
        self.vm.button[Buttons.sound_test].stateonly = self.state.sound_test

    @ensure_mixer_fadeout
    def stage_onyx_mic(self):
        """Gain stage onyx mic"""
        config = configuration.mic('onyx')

        self.mixer.headamp[XAirStrips.onyx_mic].phantom = config['phantom']
        for i in range(config['gain'] + 1):
            self.mixer.headamp[XAirStrips.onyx_mic].gain = i
            time.sleep(0.1)
        self.logger.info('Onyx Mic Staged with Phantom Power')

    @ensure_mixer_fadeout
    def stage_iris_mic(self):
        """Gain stage iris mic"""
        config = configuration.mic('iris')

        self.mixer.headamp[XAirStrips.iris_mic].phantom = config['phantom']
        for i in range(config['gain'] + 1):
            self.mixer.headamp[XAirStrips.iris_mic].gain = i
            time.sleep(0.1)
        self.logger.info('Iris Mic Staged with Phantom Power')

    def unstage_onyx_mic(self):
        """Unstage onyx mic, if phantom power was enabled, disable it"""
        config = configuration.mic('onyx')

        for i in reversed(range(config['gain'] + 1)):
            self.mixer.headamp[XAirStrips.onyx_mic].gain = i
            time.sleep(0.1)
        if config['phantom']:
            self.mixer.headamp[XAirStrips.onyx_mic].phantom = False
            self.logger.info('Onyx Mic Unstaged and Phantom Power Disabled')
        else:
            self.logger.info('Onyx Mic Unstaged')

    def unstage_iris_mic(self):
        """Unstage iris mic, if phantom power was enabled, disable it"""
        config = configuration.mic('iris')

        for i in reversed(range(config['gain'] + 1)):
            self.mixer.headamp[XAirStrips.iris_mic].gain = i
            time.sleep(0.1)
        if config['phantom']:
            self.mixer.headamp[XAirStrips.iris_mic].phantom = False
            self.logger.info('Iris Mic Unstaged and Phantom Power Disabled')
        else:
            self.logger.info('Iris Mic Unstaged')

    def patch_onyx(self):
        self.state.patch_onyx = not self.state.patch_onyx
        if self.state.patch_onyx:
            self.vm.patch.asio[0].set(11)
            self.logger.info('Onyx mic has been patched')
        else:
            self.vm.patch.asio[0].set(0)
            self.logger.info('Onyx mic has been unpatched')
        self.vm.button[Buttons.patch_onyx].stateonly = self.state.patch_onyx

    def patch_iris(self):
        self.state.patch_iris = not self.state.patch_iris
        if self.state.patch_iris:
            self.vm.patch.asio[2].set(12)
            self.logger.info('Iris mic has been patched')
        else:
            self.vm.patch.asio[2].set(0)
            self.logger.info('Iris mic has been unpatched')
        self.vm.button[Buttons.patch_iris].stateonly = self.state.patch_iris

    def mute_game_pcs(self):
        self.state.mute_game_pcs = not self.state.mute_game_pcs
        if self.state.mute_game_pcs:
            self.vm.bus[VMBuses.game_pcs].mute = True
            self.logger.info('Game PCs Muted')
        else:
            self.vm.bus[VMBuses.game_pcs].mute = False
            self.logger.info('Game PCs Unmuted')
        self.vm.button[Buttons.mute_game_pcs].stateonly = self.state.mute_game_pcs

    ### Workstation and TV Audio Routing via VBAN ###

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
                vban.vban.instream[2].on = True
            self.vm.strip[5].gain = -6
            self.vm.vban.outstream[3].on = True
            self._fade_mixer(-90, fade_in=False)
            self.logger.info(f'Workstation audio routed to {target_name}')
        else:
            with vban_cmd.api('potato', outbound=True, **target_conn) as vban:
                vban.vban.instream[2].on = False
            self.vm.strip[5].gain = 0
            self.vm.vban.outstream[3].on = False
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
                vban_target.vban.instream[3].on = True
            self.logger.info(f'TV audio routed to {target_name}')
        else:
            with (
                vban_cmd.api('banana', outbound=True, **tv_conn) as vban_tv,
                vban_cmd.api('potato', outbound=True, **target_conn) as vban_target,
            ):
                vban_tv.strip[3].A1 = True
                vban_tv.strip[3].gain = 0
                vban_tv.vban.outstream[0].on = False
                vban_target.vban.instream[3].on = False
            self.logger.info(f'TV audio routing to {target_name} disabled')

    def toggle_tv_audio_to_onyx(self):
        self._toggle_tv_routing('tv_to_onyx', 'Onyx', 'vban_onyx')

    def toggle_tv_audio_to_iris(self):
        self._toggle_tv_routing('tv_to_iris', 'Iris', 'vban_iris')
