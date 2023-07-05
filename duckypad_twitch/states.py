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
    sound_test: bool = True
    solo_onyx: bool = True
    solo_iris: bool = True

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
