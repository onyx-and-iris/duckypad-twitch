def ensure_obsws(func):
    """ensure an obs websocket connection has been established"""

    def wrapper(self, *args):
        if self.request is None:
            try:
                self.obs_connect()
            except (ConnectionRefusedError, TimeoutError):
                return
        return func(self, *args)

    return wrapper

def ensure_mixer_fadeout(func):
    """ensure mixer fadeout is stopped before proceeding"""

    def wrapper(self, *args):
        if self.mixer.lr.mix.fader > -90:
            self._fade_mixer(-90, fade_in=False)
        return func(self, *args)

    return wrapper

def to_snakecase(scene_name: str) -> str:
    """Convert caplitalized words to lowercase snake_case"""
    return '_'.join(word.lower() for word in scene_name.split())
