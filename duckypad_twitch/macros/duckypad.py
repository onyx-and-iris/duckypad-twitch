import logging

import keyboard
import voicemeeterlib
import xair_api

import duckypad_twitch
from duckypad_twitch import configuration

logging.basicConfig(level=logging.INFO)


def register_hotkeys(duckypad):
    def audio_hotkeys():
        keyboard.add_hotkey('F13', duckypad.audio.mute_mics)
        keyboard.add_hotkey('F14', duckypad.audio.only_discord)
        keyboard.add_hotkey('F15', duckypad.audio.only_stream)
        keyboard.add_hotkey('F16', duckypad.audio.sound_test)
        keyboard.add_hotkey('F17', duckypad.audio.solo_onyx)
        keyboard.add_hotkey('F18', duckypad.audio.solo_iris)
        keyboard.add_hotkey('F19', duckypad.audio.toggle_workstation_to_onyx)

    def scene_hotkeys():
        keyboard.add_hotkey('ctrl+F13', duckypad.scene.onyx_only)
        keyboard.add_hotkey('ctrl+F14', duckypad.scene.iris_only)
        keyboard.add_hotkey('ctrl+F15', duckypad.scene.dual_scene)
        keyboard.add_hotkey('ctrl+F16', duckypad.scene.onyx_big)
        keyboard.add_hotkey('ctrl+F17', duckypad.scene.iris_big)
        keyboard.add_hotkey('ctrl+F18', duckypad.scene.start)
        keyboard.add_hotkey('ctrl+F19', duckypad.scene.brb)
        keyboard.add_hotkey('ctrl+F20', duckypad.scene.end)

    def obsws_hotkeys():
        keyboard.add_hotkey('ctrl+alt+F13', duckypad.obsws.start)
        keyboard.add_hotkey('ctrl+alt+F14', duckypad.obsws.brb)
        keyboard.add_hotkey('ctrl+alt+F15', duckypad.obsws.end)
        keyboard.add_hotkey('ctrl+alt+F16', duckypad.obsws.live)
        keyboard.add_hotkey('ctrl+alt+F17', duckypad.obsws.toggle_mute_mic)
        keyboard.add_hotkey('ctrl+alt+F18', duckypad.obsws.toggle_stream)

    def streamlabs_controller_hotkeys():
        keyboard.add_hotkey('ctrl+F22', duckypad.streamlabs.begin_stream)
        keyboard.add_hotkey('ctrl+F23', duckypad.streamlabs.end_stream)
        keyboard.add_hotkey('ctrl+alt+F23', duckypad.streamlabs.launch, args=(10,))
        keyboard.add_hotkey('ctrl+alt+F24', duckypad.streamlabs.shutdown)

    def duckypad_hotkeys():
        keyboard.add_hotkey('ctrl+F21', duckypad.reset)

    for step in (
        audio_hotkeys,
        scene_hotkeys,
        obsws_hotkeys,
        streamlabs_controller_hotkeys,
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

        print('press ctrl+m to quit')
        keyboard.wait('ctrl+m')
