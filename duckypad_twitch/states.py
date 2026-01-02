from dataclasses import dataclass


@dataclass
class StreamState:
    is_live: bool = False
    current_scene: str = ''


@dataclass
class AudioState:
    mute_mics: bool = True
    only_discord: bool = False
    only_stream: bool = True
    sound_test: bool = False
    patch_onyx: bool = True
    patch_iris: bool = True
    mute_game_pcs: bool = False

    ws_to_onyx: bool = False
    ws_to_iris: bool = False
    tv_to_onyx: bool = False
    tv_to_iris: bool = False


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
