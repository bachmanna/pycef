# Build instructions

There are two types of builds you can perform. You can build
PyCEF using the prebuilt CEF binaries. Or you can build both
PyCEF and CEF from sources. Building CEF is a long process that
can take hours. In the tools/ directory there is the automate.py
script that automates building. However before you can run it
you must satisfy some requirements.


Table of contents:
* [Requirements](#requirements)
* [Build PyCEF using prebuilt CEF binaries](#build-pycef-using-prebuilt-cef-binaries)
* [Build both PyCEF and CEF from sources](#build-both-pycef-and-cef-from-sources)
* [Build CEF manually](#build-cef-manually)
* [How to patch](#how-to-patch)
* [Ninja build slows down computer](#ninja-build-slows-down-computer)


## Requirements

Below are platform specific requirements. Do these first before
following instructions in the "All platforms" section that lists
requirements common for all platforms.

__Windows__

* For Python 2.7 - VS2008 compiler is required:
  http://www.microsoft.com/en-us/download/details.aspx?id=44266
* For Python 3.4 - VS2010 compiler is required:
  https://docs.python.org/3.4/using/windows.html#compiling-python-on-windows
* For Python 3.5 - VS2015 compiler is required:
  https://docs.python.org/3.5/using/windows.html#compiling-python-on-windows
* To build CEF from sources you must install VS2013 Update 4 or later
  and use Win7 x64 or later. 32-bit OS'es are not supported. For more
  details see [here]
  (https://www.chromium.org/developers/how-tos/build-instructions-windows).

__All platforms__

* Install dependencies for the automate.py tool by executing:
  `cd tools/ && pip install -r requirements.txt`. This will install
  some PyPI packages including Cython. On Windows installing Cython
  requires a VS compiler - see instructions above for Windows.


## Build PyCEF using prebuilt CEF binaries

Run the automate.py tool using the --prebuilt-cef flag:
```
cd tools/
python automate.py --prebuilt-cef
```

You should be fine by running it with the default options, but if you
need to customize the build then use the --help flag to see more.


## Build both PyCEF and CEF from sources

Run the automate.py tool using the --build-cef flag:
```
cd tools/
python automate.py --build-cef
```

You should be fine by running it with the default options, but if you
need to customize the build then use the --help flag to see more.


## Build CEF manually

CEF Python official binaries come with custom CEF binaries with
a few patches applied for our use case. These patches are in the
patches/ directory.

On Linux before running any of CEF tools apply the issue73 patch
first.

To build CEF follow the instructions on the Branches and
Building CEF wiki page:
https://bitbucket.org/chromiumembedded/cef/wiki/BranchesAndBuilding

After it is successfully built - apply patches, rebuild and remake
distribs.

Note that CEF patches must be applied in the "download_dir/chromium/src/cef/"
directory, not in the "download_dir/cef/" directory.


## How to patch

Apply a patch in current directory:
```
cd chromium/src/cef/
git apply cef.gyp.patch
```

Create a patch from unstaged changes in current directory:
```
cd chromium/src/cef/
git diff --relative > cef.gyp.patch
```


## Ninja build slows down computer

If ninja slows down your computer too much (6 parallel jobs by default),
build manually with this command (where -j2 means to run 2 jobs in parallel):
```
cd chromium/src
ninja -v -j2 -Cout\Release cefclient
```
