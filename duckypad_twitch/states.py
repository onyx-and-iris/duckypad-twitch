from dataclasses import dataclass


@dataclass
class StreamState:
    is_live: bool = False
    current_scene: str = ""


@dataclass
class AudioState:
    mute_mics: bool = True
    only_discord: bool = False
    only_stream: bool = True
    sound_test: bool = False
    solo_onyx: bool = False
    solo_iris: bool = False

    ws_to_onyx: bool = False


@dataclass
class SceneState:
    onyx_only: bool = False
    iris_only: bool = False
    dual_scene: bool = False
    onyx_big: bool = False
    iris_big: bool = False
    start: bool = False
    brb: bool = False
    end: bool = False


@dataclass
class OBSWSState:
    mute_mic: bool = True
