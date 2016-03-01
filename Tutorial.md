# Tutorial

This is just a draft that outlines topics yet to be written.
TODO: see the CEF Tutorial wiki
TODO: see the CEF General Usage and Javascript Integration wikis.

Table of contents:
* [Installation](#installation)
* [Example](#example)
* [Settings](#settings)
* [Architecture](#architecture)
* [Handlers](#handlers)
* [Javascript integration](#javascript-integration)
* [Plugins](#plugins)
* [Build executable](#build-executable)
* [What next?](#what-next)


## Installation

* download from Releases/
* types of packages for each platform
* install from PyPI using pip (Win/Mac)


## Example

* paste code, most simple example loading www.google.com,
  shouldn't be more than 20 lines.

* Explain all functions from the example:
    - initialize()
        you can call initialize and shutdown only once
    - shutdown()
        - to exit cleanly
        - cookies or other storage might not be saved (flushed every 30 secs)
          process might freeze (XP experienced)
    - messageloop
    - messageloopwork
        - messageloop faster, but this one allows integration into
          existing message loop

* ExceptHook in examples so that all processes are closed in
  case of a python error

* there are more examples in the examples/ directory.


## Settings

* Describe a few most commonly used settings.
* Command-line switches from Chromium.
* Disable developer-tools or context menu
    - application settings context menu dict.


## Architecture

* subprocess.exe
* browser process
* renderer process
* gpu process
* zygote on linux
* Describe browser process threads


## Helpers

* excepthook()
* appppath()


## Handlers

* What are handlers.
* Handler callbacks may be called either on UI thread or IO thread.
  Use functions for posting tasks when need to access UI thread from IO thread.
* Example code how to use handlers - use base code from Tutorial-beginner.
    - keyboard handler F12 devtools and F5
    - loadhandler onloadstart to insert js to all pages
    - loadhandler onloadingstatechange when page completed loading
    - onloaderror


## Javascript integration

* how to expose function to js
* how to communicate two-way js<>python
* callbacks
* js errors handling
* example code how to use - use base code from Tutorial-beginner.


## Plugins

* Load PPAPI flash plugin
    - console window issue on Windows in CEF 47, possible solutions


## Build executable

* See the examples/installers/ directory. On Win use py2exe. On Linux
  use cxfreeze. On Mac use py2app.


## What next?

* See more examples in the examples/ directory
* See API docs in the api/ directory
* Example usage of most of API is available in the unittests/ directory
* See the Knowledge base document
* Ask questions and report problems on the Forum
