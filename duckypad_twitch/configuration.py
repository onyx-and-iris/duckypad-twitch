from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

configuration = {}

configpath = Path.cwd() / 'configs' / 'duckypad.toml'
if not configpath.exists():
    raise OSError(f'unable to locate {configpath}')

with open(configpath, 'rb') as f:
    configuration = tomllib.load(f)


def get(name):
    if name in configuration:
        return configuration[name]


def mic(name):
    assert 'microphones' in configuration, 'No microphones defined in configuration'

    try:
        mic_key = configuration['microphones'][name]
        mic_cfg = configuration['microphone'][mic_key]
        return mic_cfg
    except KeyError as e:
        raise KeyError(f'Microphone configuration for "{name}" not found') from e
