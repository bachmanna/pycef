"""Tutorial example."""
# Any changes here must be applied to unit tests as well.

import pycef as cef
import pycef.interfaces as cefi
from cef.app import Settings, Switches
from cef.browser import Browser, Embedder, BrowserSettings
from cef.helpers import excepthook, apppath


def main():
    """Main entry point."""
    Browser(url="https://www.google.com/",
            events=[LoadEvents(), KeyboardEvents()])
    cef.run()


class LoadEvents(cefi.LoadEvents):
    """Browser load events."""
    
    def start():
        pass
    
    def end():
        pass
    
    def error():
        pass


class KeyboardEvents(cefi.KeyboardEvents):
    """Browser keyboard events."""
    
    def key():
        pass


if __name__ == "__main__":
    main()
