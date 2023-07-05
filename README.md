# duckypad twitch

[![PyPI - Version](https://img.shields.io/pypi/v/duckypad-twitch.svg)](https://pypi.org/project/duckypad-twitch)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckypad-twitch.svg)](https://pypi.org/project/duckypad-twitch)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install duckypad-twitch
```

## About

This respository holds the source code for the [Duckypad][duckypad] driver we use when Twitch streaming.

Packages used in this codebase:

- [`keyboard`][keyboard]
- [`voicemeeter-api`][voicemeeter-api]
- [`vban-cmd`][vban-cmd]
- [`xair-api`][xair-api]
- [`obsws-python`][obsws-python]
- [`slobs-websocket`][slobs-websocket]

## Need for a custom driver

We use a three pc streaming setup, one gaming pc for each of us and a third pc that handles the stream. Both of our microphones, as well as both gaming pc are wired into an [MR18 mixer](https://www.midasconsoles.com/product.html?modelCode=P0C8H) which itself is connected to the streaming pc. Then we vban our microphones from the workstation off to each of our pcs in order to talk in-game. All audio is routed through [Voicemeeter][voicemeeter], which itself is connected to Studio ONE daw for background noise removal. Any voice communication software (such as Discord) is therefore installed onto the workstation, separate of our gaming pcs.

If you've ever attempted to setup a dual pc streaming setup, you may appreciate the audio challenges of a three pc setup.

## Details about the code

This is a tightly coupled implementation meaning it is not designed for public use, it is purely a demonstration.

- All keybindings are defined in `__main__.py`.
- A base DuckyPad class in duckypad.py is used to connect the various layers of the driver.
- Most of the audio routing for the dual stream is handled in the `Audio class` in audio.py with the aid of Voicemeeter's Remote API.
  - Some communication with the Xair mixer and the vban protocol can also be found in this class.
- Scene switching and some audio routing are handled in the `Scene class` in scene.py.
  - A `StreamlabsController` class is used to communicate with the Streamlabs API.
- Dataclasses are used to hold internal states and states are updated using event callbacks.
- Decorators are used to confirm websocket connections.
- A separate OBSWS class is used to handle scenes and mic muting (for a single pc stream).
- Logging is included to help with debugging but also to provide stream information in real time.

## License

`duckypad-twitch` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

[duckypad]: https://github.com/dekuNukem/duckyPad
[keyboard]: https://github.com/boppreh/keyboard
[voicemeeter-api]: https://github.com/onyx-and-iris/voicemeeter-api-python
[vban-cmd]: https://github.com/onyx-and-iris/vban-cmd-python
[xair-api]: https://github.com/onyx-and-iris/xair-api-python
[obsws-python]: https://github.com/aatikturk/obsws-python
[slobs-websocket]: https://github.com/onyx-and-iris/slobs_websocket
[voicemeeter]: https://voicemeeter.com/
