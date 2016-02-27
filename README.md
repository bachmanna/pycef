# PyCEF

PyCEF is a CEF Python clone that is more Pythonic.

New changes coming:
* Python 3.5, 3.4 and 2.7 support
* Updated to the latest Chromium
* Unicode strings in both Python 2 and Python 3. In CEF Python byte
  strings were used in Python 2.
* API cleanup. Better structure with submodules like helpers, thread etc.
* Will follow the [PEP8](https://www.python.org/dev/peps/pep-0008/)
  style guide. For example method CreateBrowserSync() will become
  create_browser_sync(). Uppercase constants will become class types.
* Better examples
* Tutorial with many topics explained
* New great API docs, easy to navigate, up-to-date and easily searchable
* New tools that fully automate building on all platforms using CMake.
  Also build automation of CEF from sources.
* Unit tests
* Lots of new CEF API exposed
* Improvements to Core - in source docs, modular code with better
  structure will be easier to work with for contributors
* CI builds with Travis and AppVeyor
