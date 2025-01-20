import slobs_websocket


def ensure_sl(func):
    """ensure a streamlabs websocket connection has been established"""

    def wrapper(self, *args):
        if self._duckypad.streamlabs.conn.ws is None:
            try:
                try:
                    self.connect()
                except AttributeError:
                    self._duckypad.streamlabs.connect()
            except slobs_websocket.exceptions.ConnectionFailure:
                self._duckypad.streamlabs.conn.ws = None
                return
        return func(self, *args)

    return wrapper


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
