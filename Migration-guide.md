# Migration guide - port code from CEF Python

TODO

- In CEF Python there was one big module, in PyCEF there are submodules:
    pycef
    pycef.app
    pycef.browser
    pycef.helpers
    pycef.interfaces

- core functions renamed:
    Initialize -> init
    CreateBrowserSync -> class browser.Browser()
    MessageLoop -> run
    MessageLoopWork -> work
    Shutdown -> quit

- RenderHandler renamed to OffscreenHandler

...
