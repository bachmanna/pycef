# Knowledge base


Table of contents:
* [CEF architecture](#cef-architecture)
* [Windows XP support](#windows-xp-support)
* [Mac 32-bit support](#mac-32-bit-support)
* [Flash works in Google Chrome, but doesn't work in CEF Python](#flash-works-in-google-chrome-but-doesnt-work-in-cef-python)
* [Black/White browser screen](#blackwhite-browser-screen)
* [Feature X works in Google Chrome, but doesn't work in CEF Python](#feature-x-works-in-google-chrome-but-doesnt-work-in-cef-python)
* [How to capture Audio and Video in HTML5?](#how-to-capture-audio-and-video-in-html5)
* [Touch and Multi-touch support](#touch-and-multi-touch-support)
* [Security](#security)


## CEF architecture

See the [Architecture](https://bitbucket.org/chromiumembedded/cef/wiki/Architecture.md#markdown-header-cef3) CEF wiki page (upstream).


## Windows XP support

CEF Python 49.0 will be the last version to support Windows XP. This is due to Chromium/CEF dropping XP support.

On XP you should disable GPU acceleration by using the --disable-gpu and --disable-gpu-compositing switches. See the [Command line switches](CommandLineSwitches) wiki page.


## Mac 32-bit support

Since version 39, Chromium and Google Chrome are not available in 32-bit version for MAC OS X.

Download cefpython 31.2 for Mac 32-bit from [Google Drive archive](https://drive.google.com/folderview?id=0B1di2XiBBfacOEM0aUFJZFU0R3c&usp=drive_web&tid=0B1di2XiBBfacOFpJb1dERGZSRnc#list). This release includes both 32-bit and 64-bit binaries.


## Flash works in Google Chrome, but doesn't work in CEF Python

Google Chrome bundles a proprietary version of Flash called Pepper Flash. CEF Python does not include Flash out of the box. You need to install Flash Plugin (PPAPI version) in your OS:

1. Go to http://get.adobe.com/flashplayer/otherversions/
2. Select an operating system
3. Select PPAPI version of plugin (for Opera and Chromium)

NOTE: in old CEF you had to download NPAPI plugin, in newer CEF (Chrome 47 release) you need to download PPAPI plugin.


## Black/White browser screen

If you get a black or white screen then this may be caused by incompatible GPU (video card) drivers. There are following solutions to this:

1. When CEF Python is updated to a newer Chrome version then the problem may be fixed. Check with current Google Chrome if this is the case.

2. Try updating your video card drivers to the latest version available.

3. You can disable GPU hardware acceleration by adding the "disable-gpu" and "disable-gpu-compositing" command line switches. See the CommandLineSwitches wiki page. Note that this will degrade performance if you're using any advanced 3D features. It will affect 2d accelerated content as well.

Note that when web page uses WebGL then the black screen may still appear even after disabling GPU hardware acceleration. However that shouldn't be a concern as it's not supposed to work anyway. Though you may not see a nice message about WebGL not being supported. All other websites that do not use webgl will work fine.


## Feature X works in Google Chrome, but doesn't work in CEF Python

CEF Python embeds Chromium Embedded Framework which is based on Chromium browser. Functionality may differ a bit from Google Chrome. The browser from Google is a proprietary software that for example includes MPEG-4/H.264 codecs that aren't included in the open source Chromium. CEF also doesn't support Chrome Extensions.

To see if some feature is working or a bug is fixed in newer CEF release perform the following steps:

1. Go to http://www.cefbuilds.com/
2. Choose a branch
3. Download TestApp binaries
4. Run the cefclient executable


## How to capture Audio and Video in HTML5?

To be able to use the getUserMedia() function you need to set the "enable-media-stream" switch. See the [Command line switches](CommandLineSwitches) wiki page.


## Touch and Multi-touch support

In CEF 47 or later touch device is auto-detected and everything should
work out of the box. If that's not the case try setting the following
switches (see the CommandLineSwitches wiki page):
* --touch-events=enabled
* --enable-pinch


## Security

Quote by Marshall Greenblatt:

> CEF offers significant integration capabilities beyond what
> is offered by a standard Google Chrome browser installation.
> The trade off for these additional capabilities is that
> organizations using CEF must take responsibility for their own
> application security. CEF and the underlying open source projects
> (Chromium, WebKit, etc) involve a significant amount of code and
> offer no warranties. Organizations should document and follow best
> practices to minimize potential security risks. Here are some
> recommended best practices that organizations can consider:
> - Only load known/trusted content. This is by far the best way
>   to avoid potential security issues.
> - Disable plugins. This will avoid a large category of security
>   issues caused by buggy versions of Flash, Java, etc.
> - Do not explicitly disable or bypass security features in your
>   application. For example, do not enable CefBrowserSettings that
>   bypass security features or add fake headers to bypass HTTP
>   access control.
> - Keep your application up to date with the newest CEF release
>   branch. You may want to update the underlying Chromium release
>   version and perform your own builds to take immediate advantage
>   of any bug fixes.
> - Enforce good programming practices. Every organization should
>   have best practices for design, testing and verification.
> - Audit your application for potential security issues. Every
>   decision that may have security consequences should be evaluated
>   by people who are knowledgeable about security considerations.

Reference: [Question on browser security]
(http://magpcss.org/ceforum/viewtopic.php?f=10&t=10222)
from the CEF Forum.
