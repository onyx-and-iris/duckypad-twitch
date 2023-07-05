import logging
import subprocess as sp
import time
import winreg
from asyncio.subprocess import DEVNULL
from pathlib import Path

import slobs_websocket

from . import configuration
from .util import ensure_sl

logger = logging.getLogger(__name__)


class StreamlabsController:
    SL_FULLPATH = ""

    def __init__(self, duckypad, **kwargs):
        self.logger = logger.getChild(__class__.__name__)
        self._duckypad = duckypad
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.proc = None

    ####################################################################################
    #   CONNECT/DISCONNECT from the API
    ####################################################################################

    def connect(self):
        try:
            conn = configuration.get("streamlabs")
            assert conn is not None, "expected configuration for streamlabs"
            self.conn.connect(**conn)
        except slobs_websocket.exceptions.ConnectionFailure as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise

        self._duckypad.scene.scenes = {
            scene.name: scene.id for scene in self.conn.ScenesService.getScenes()
        }
        self.logger.debug(f"registered scenes: {self._duckypad.scene.scenes}")
        self.conn.ScenesService.sceneSwitched += self.on_scene_switched
        self.conn.StreamingService.streamingStatusChange += (
            self.on_streaming_status_change
        )

    def disconnect(self):
        self.conn.disconnect()

    ####################################################################################
    #   EVENTS
    ####################################################################################

    def on_streaming_status_change(self, data):
        self.logger.debug(f"streaming status changed, now: {data}")
        if data in ("live", "starting"):
            self._duckypad.stream.is_live = True
        else:
            self._duckypad.stream.is_live = False

    def on_scene_switched(self, data):
        self._duckypad.stream.current_scene = data.name
        self.logger.debug(
            f"stream.current_scene updated to {self._duckypad.stream.current_scene}"
        )

    ####################################################################################
    #   START/STOP the stream
    ####################################################################################

    @ensure_sl
    def begin_stream(self):
        if self._duckypad.stream.is_live:
            self.logger.info("Stream is already online")
            return
        self.conn.StreamingService.toggleStreaming()

    @ensure_sl
    def end_stream(self):
        if not self._duckypad.stream.is_live:
            self.logger.info("Stream is already offline")
            return
        self.conn.StreamingService.toggleStreaming()

    ####################################################################################
    #   CONTROL the stream
    ####################################################################################

    @ensure_sl
    def switch_scene(self, name):
        return self.conn.ScenesService.makeSceneActive(
            self._duckypad.scene.scenes[name.upper()]
        )

    ####################################################################################
    #   LAUNCH/SHUTDOWN the streamlabs process
    ####################################################################################

    def launch(self, delay=5):
        def get_slpath():
            SL_KEY = "029c4619-0385-5543-9426-46f9987161d9"

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"{}".format("SOFTWARE" + "\\" + SL_KEY)
            ) as regpath:
                return winreg.QueryValueEx(regpath, r"InstallLocation")[0]

        try:
            if not self.SL_FULLPATH:  # so we only read from registry once.
                self.SL_FULLPATH = Path(get_slpath()) / "Streamlabs OBS.exe"
        except FileNotFoundError as e:
            self.logger.exception(f"{type(e).__name__}: {e}")
            raise

        if self.proc is None:
            self.proc = sp.Popen(self.SL_FULLPATH, shell=False, stdout=DEVNULL)
            time.sleep(delay)
            self.connect()

    def shutdown(self):
        self.disconnect()
        time.sleep(1)
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
