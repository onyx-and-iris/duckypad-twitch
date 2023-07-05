from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

configuration = {}

configpath = Path.cwd() / "configs" / "duckypad.toml"
if not configpath.exists():
    raise OSError(f"unable to locate {configpath}")

with open(configpath, "rb") as f:
    configuration = tomllib.load(f)


def get(name):
    if name in configuration:
        return configuration[name]
