# duckypad twitch

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

**Table of Contents**

- [Installation](#installation)
- [License](#license)


## About

This respository holds the source code for the [Duckypad][duckypad] driver we use when Twitch streaming.

Packages used in this codebase:

- [`keyboard`][keyboard]
- [`voicemeeter-api`][voicemeeter-api]
- [`vban-cmd`][vban-cmd]
- [`xair-api`][xair-api]
- [`obsws-python`][obsws-python]

## Need for a custom driver

We use a triple pc streaming setup, one gaming pc for each of us and a third pc that handles the stream.

- Both of our microphones, as well as both gaming pc are wired into an [MR18 mixer][mr18] which itself is connected to the streaming pc.
- Then we vban our microphones from the workstation off to each of our pcs in order to talk in-game. All audio is routed through [Voicemeeter][voicemeeter].
- Voicemeeter is connected to Studio ONE daw for background noise removal. Any voice communication software (such as Discord) is therefore installed onto the workstation, separate of our gaming pcs.

If you've ever attempted to setup a dual pc streaming setup, you may appreciate the challenges of a triple pc setup.

## Details about the code

This package is for demonstration purposes only. Several of the interfaces on which it depends have been tightly coupled into a duckypad macros program.

- The package entry point can be found at `duckypad_twitch.macros.duckypad`.
- A base DuckyPad class in duckypad.py is used to connect the various layers of the driver.
- Most of the audio routing for the dual stream is handled in the `Audio class` in audio.py with the aid of Voicemeeter's Remote API.
  - Some communication with the Xair mixer and the vban protocol can also be found in this class.
- Scene switching and some audio routing are handled in the `Scene class` in scene.py.
  - A `OBSWS` class is used to communicate with OBS websocket.
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
[voicemeeter]: https://voicemeeter.com/
[mr18]: https://www.midasconsoles.com/product.html?modelCode=P0C8H
