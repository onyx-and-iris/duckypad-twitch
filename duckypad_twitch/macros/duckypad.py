import logging

import keyboard
import voicemeeterlib
import xair_api

import duckypad_twitch
from duckypad_twitch import configuration

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def register_hotkeys(duckypad):
    def audio_hotkeys():
        keyboard.add_hotkey('F13', duckypad.audio.mute_mics)
        keyboard.add_hotkey('F14', duckypad.audio.only_discord)
        keyboard.add_hotkey('F15', duckypad.audio.only_stream)
        keyboard.add_hotkey('F16', duckypad.audio.sound_test)
        keyboard.add_hotkey('F17', duckypad.audio.stage_onyx_mic)
        keyboard.add_hotkey('F18', duckypad.audio.stage_iris_mic)
        keyboard.add_hotkey('shift+F17', duckypad.audio.unstage_onyx_mic)
        keyboard.add_hotkey('shift+F18', duckypad.audio.unstage_iris_mic)
        keyboard.add_hotkey('F19', duckypad.audio.solo_onyx)
        keyboard.add_hotkey('F20', duckypad.audio.solo_iris)
        keyboard.add_hotkey('F21', duckypad.audio.toggle_workstation_to_onyx)
        keyboard.add_hotkey('F22', duckypad.audio.toggle_workstation_to_iris)
        keyboard.add_hotkey('F23', duckypad.audio.toggle_tv_audio_to_onyx)
        keyboard.add_hotkey('F24', duckypad.audio.toggle_tv_audio_to_iris)

    def scene_hotkeys():
        keyboard.add_hotkey('ctrl+F13', duckypad.scene.start)
        keyboard.add_hotkey('ctrl+F14', duckypad.scene.dual_stream)
        keyboard.add_hotkey('ctrl+F15', duckypad.scene.brb)
        keyboard.add_hotkey('ctrl+F16', duckypad.scene.end)
        keyboard.add_hotkey('ctrl+F17', duckypad.scene.onyx_solo)
        keyboard.add_hotkey('ctrl+F18', duckypad.scene.iris_solo)

    def obsws_hotkeys():
        keyboard.add_hotkey('ctrl+alt+F13', duckypad.obsws.start_stream)
        keyboard.add_hotkey('ctrl+alt+F14', duckypad.obsws.stop_stream)

    def duckypad_hotkeys():
        keyboard.add_hotkey('ctrl+F24', duckypad.reset)

    for step in (
        audio_hotkeys,
        scene_hotkeys,
        obsws_hotkeys,
        duckypad_hotkeys,
    ):
        step()


def run():
    xair_config = configuration.get('xair')

    with (
        voicemeeterlib.api('potato') as vm,
        xair_api.connect('MR18', **xair_config) as mixer,
        duckypad_twitch.connect(vm=vm, mixer=mixer) as duckypad,
    ):
        vm.apply_config('streaming_extender')  # extends the streaming config

        register_hotkeys(duckypad)

        banner_width = 80
        logger.info(
            '\n'.join(
                (
                    '\n' + '#' * banner_width,
                    'Duckypad Twitch is running. ',
                    'Run sound test and gain stage mics to verify audio setup.',
                    'Then start the stream.',
                    "Don't forget Voicemeeter starts in Only Stream mode!",
                    'So first unmute mics, then give stream introduction, then disable Only Stream mode.',
                    'Now you are live with mics unmuted!',
                    '#' * banner_width,
                )
            )
        )

        print('press ctrl+shift+F24 to quit')
        keyboard.wait('ctrl+shift+F24')
