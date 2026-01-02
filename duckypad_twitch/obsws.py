import logging

import obsws_python as obsws

from . import configuration
from .layer import ILayer
from .util import ensure_obsws

logger = logging.getLogger(__name__)


class OBSWS(ILayer):
    def __init__(self, duckypad):
        super().__init__(duckypad)
        self.request = self.event = None

    @property
    def identifier(self):
        return type(self).__name__

    ### State Management ###

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val

    def reset_states(self):
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
        self.request = self.event = None

    ### Event Handlers ###

    def on_stream_state_changed(self, data):
        self._duckypad.stream.is_live = data.output_active

    def on_current_program_scene_changed(self, data):
        self._duckypad.stream.current_scene = data.scene_name
        match data.scene_name:
            case 'START':
                self.logger.info('Start scene enabled.. ready to go live!')
            case 'DUAL STREAM':
                self.logger.info('Dual Stream Scene enabled')
            case 'BRB':
                self.logger.info('BRB: game pcs muted')
            case 'END':
                self.logger.info('End Scene enabled.')
            case 'ONYX SOLO':
                self.logger.info('Onyx Solo Scene enabled, Iris game pc muted')
            case 'IRIS SOLO':
                self.logger.info('Iris Solo Scene enabled, Onyx game pc muted')

    def on_exit_started(self, data):
        self.logger.info('OBS is exiting, disconnecting...')
        self.request.disconnect()
        self.request = self.event = None

    ### OBSWS Request Wrappers ###

    @ensure_obsws
    def _call(self, fn_name, *args):
        fn = getattr(self.request, fn_name)
        resp = fn(*args)
        return resp

    def switch_to_scene(self, scene_name):
        self._call('set_current_program_scene', scene_name)

    def start_stream(self):
        resp = self._call('get_stream_status')
        if resp.output_active:
            self.logger.info("stream is already live, can't start stream")
            return

        self._call('start_stream')
        self.logger.info('stream started')

    def stop_stream(self):
        resp = self._call('get_stream_status')
        if not resp.output_active:
            self.logger.info("stream is not live, can't stop stream")
            return

        self._call('stop_stream')
        self.logger.info('stream stopped')
