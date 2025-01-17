import logging

import obsws_python as obsws

from . import configuration
from .layer import ILayer
from .states import OBSWSState
from .util import ensure_obsws

logger = logging.getLogger(__name__)


class OBSWS(ILayer):
    def __init__(self, duckypad):
        super().__init__(duckypad)
        self.request = self.event = None
        self._state = OBSWSState()

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
        resp = self.request.get_input_mute('Mic/Aux')
        self.state.mute_mic = resp.input_muted
        resp = self.request.get_stream_status()
        self._duckypad.stream.is_live = resp.output_active

    def obs_connect(self):
        try:
            conn = configuration.get('obsws')
            assert conn is not None, 'expected configuration for obs'
            self.request = obsws.ReqClient(**conn)
            self.reset_states()
            self.event = obsws.EventClient(**conn)
            self.event.callback.register(
                [
                    self.on_stream_state_changed,
                    self.on_input_mute_state_changed,
                    self.on_current_program_scene_changed,
                    self.on_exit_started,
                ]
            )
        except (ConnectionRefusedError, TimeoutError) as e:
            self.logger.error(f'{type(e).__name__}: {e}')
            raise

    def disconnect(self):
        for client in (self.request, self.event):
            if client:
                client.disconnect()

    def on_current_program_scene_changed(self, data):
        self._duckypad.stream.current_scene = data.scene_name
        self.logger.info(f'scene switched to {self._duckypad.stream.current_scene}')
        if self._duckypad.stream.current_scene in ('START', 'BRB', 'END'):
            self.mute_mic_state(True)

    def on_input_mute_state_changed(self, data):
        if data.input_name == 'Mic/Aux':
            self.state.mute_mic = data.input_muted
        self.logger.info(f'mic was {"muted" if self.state.mute_mic else "unmuted"}')

    def on_stream_state_changed(self, data):
        self._duckypad.stream.is_live = data.output_active
        self.logger.info(f'stream is {"live" if self._duckypad.stream.is_live else "offline"}')

    def on_exit_started(self, _):
        self.event.unsubscribe()

    @ensure_obsws
    def call(self, fn_name, *args):
        fn = getattr(self.request, fn_name)
        resp = fn(*args)
        return resp

    def start(self):
        self.call('set_current_program_scene', 'START')

    def brb(self):
        self.call('set_current_program_scene', 'BRB')

    def end(self):
        self.call('set_current_program_scene', 'END')

    def live(self):
        self.call('set_current_program_scene', 'LIVE')

    def mute_mic_state(self, val):
        self.call('set_input_mute', 'Mic/Aux', val)

    def toggle_mute_mic(self):
        self.call('toggle_input_mute', 'Mic/Aux')

    def toggle_stream(self):
        self.call('toggle_stream')
