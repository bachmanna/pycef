# Copyright (c) 2016 PyCEF, see the Authors file. All rights reserved.

"""Build PyCEF. Use prebuilt CEF binaries or build CEF from sources.

Usage:
    automate.py (--prebuilt-cef | --build-cef)
                [--cef-branch BRANCH] [--cef-commit COMMIT]
                [--build-dir BUILDDIR] [--cef-build-dir CEFBUILDDIR]
                [--ninja-jobs JOBS] [--gyp-generators GENERATORS]
                [--gyp-msvs-version MSVS]
    automate.py (-h | --help) [type -h to show full description for options]

Options:
    -h --help           Show this help message.
    --prebuilt-cef      Whether to use prebuilt CEF binaries. Prebuilt
                        binaries for Linux are build on Debian/Ubuntu.
    --build-cef         Whether to build CEF from sources with the pycef
                        patches applied.
    --cef-branch        CEF branch. Defaults to CHROME_VERSION_BUILD from
                        "pycef/version/cef_version_{platform}.h" (TODO).
    --cef-commit        CEF revision. Defaults to CEF_COMMIT_HASH from
                        "pycef/version/cef_version_{platform}.h" (TODO).
    --build-dir         Build directory.
    --cef-build-dir     CEF build directory. By default same as --build-dir.
    --ninja-jobs        How many CEF jobs to run in parallel. To speed up
                        building set it to number of cores in your CPU.
                        By default set to 2.
    --gyp-generators    Set GYP_GENERATORS [default: ninja].
    --gyp-msvs-version  Set GYP_MSVS_VERSION.

"""

import os
import sys
import shlex
import subprocess
import platform
import docopt
import struct
import re
import stat
import glob
import shutil

# CONSTANTS
ARCH32 = (8 * struct.calcsize('P') == 32)
ARCH64 = (8 * struct.calcsize('P') == 64)
OS_POSTFIX = ("win" if platform.system() == "Windows" else
              "linux" if platform.system() == "Linux" else
              "mac" if platform.system() == "Darwin" else "unknown")
OS_POSTFIX2 = "unknown"
if OS_POSTFIX == "win":
    OS_POSTFIX2 = "win32" if ARCH32 else "win64"
elif OS_POSTFIX == "mac":
    OS_POSTFIX2 = "mac32" if ARCH32 else "mac64"
elif OS_POSTFIX == "linux":
    OS_POSTFIX2 = "linux32" if ARCH32 else "linux64"

CEF_GIT_URL = "https://bitbucket.org/chromiumembedded/cef.git"

VS2015_VCVARS = "\"C:\Program Files (x86)\\Microsoft Visual Studio 14.0" \
                "\\VC\\bin\\vcvars32.bat\"" \
                if ARCH32 else \
                "\"C:\Program Files (x86)\\Microsoft Visual Studio 14.0" \
                "\\VC\\bin\\amd64\\vcvars64.bat\""

VS2013_VCVARS = "\"C:\Program Files (x86)\\Microsoft Visual Studio 12.0" \
                "\\VC\\bin\\vcvars32.bat\"" \
                if ARCH32 else \
                "\"C:\Program Files (x86)\\Microsoft Visual Studio 12.0" \
                "\\VC\\bin\\amd64\\vcvars64.bat\""

VS2008_VCVARS = "\"%LocalAppData%\\Programs\\Common\\Microsoft" \
                "\\Visual C++ for Python\\9.0\\vcvarsall.bat\" x86" \
                if ARCH32 else \
                "\"%LocalAppData%\\Programs\\Common\\Microsoft" \
                "\\Visual C++ for Python\\9.0\\vcvarsall.bat\" amd64"


class Options(object):
    """Options from command-line and internal options."""

    # From command-line
    prebuilt_cef = False
    build_cef = False
    cef_branch = ""
    cef_commit = ""
    build_dir = ""
    cef_build_dir = ""
    ninja_jobs = 2
    gyp_generators = "ninja"
    gyp_msvs_version = ""

    # Internal options
    depot_tools_dir = ""
    tools_dir = ""
    pycef_dir = ""
    binary_distrib = ""


def main():
    """Main entry point."""
    setup_options(docopt.docopt(__doc__))

    if Options.build_cef:
        build_cef()
    elif Options.prebuilt_cef:
        prebuilt_cef()


def setup_options(docopt_args):
    """Setup options from cmd-line and internal options."""

    # Populate Options using command line arguments
    usage = __doc__
    for key in docopt_args:
        value = docopt_args[key]
        if key.startswith("--"):
            match = re.search(r"\[%s\s+([^\]]+)\]" % (re.escape(key),),
                              usage)
            if match:
                arg_key = match.group(1)
                value = docopt_args[arg_key]
        key2 = key.replace("--", "").replace("-", "_")
        if hasattr(Options, key2) and value is not None:
            setattr(Options, key2, value)

    Options.tools_dir = os.path.dirname(os.path.realpath(__file__))
    Options.pycef_dir = os.path.dirname(Options.tools_dir)

    # --cef-branch
    # TODO: by default use branch by calling pycef_version()
    if not Options.cef_branch:
        print("[automate.py] ERROR: --cef-branch flag is required")
        sys.exit(1)

    # --gyp-msvs-version
    if not Options.gyp_msvs_version:
        if int(Options.cef_branch) >= 2704:
            Options.gyp_msvs_version = "2015"
        else:
            Options.gyp_msvs_version = "2013"

    # --build-dir
    if Options.build_dir:
        Options.build_dir = os.path.realpath(Options.build_dir)
    else:
        Options.build_dir = os.path.join(Options.pycef_dir, "build")
    if " " in Options.build_dir:
        print("[automate.py] ERROR: Build dir cannot contain spaces")
        print(">> " + Options.build_dir)
        sys.exit(1)

    # --cef-build-dir
    if Options.cef_build_dir:
        Options.cef_build_dir = os.path.realpath(Options.cef_build_dir)
    else:
        Options.cef_build_dir = Options.build_dir
    if " " in Options.cef_build_dir:
        print("[automate.py] ERROR: CEF build dir cannot contain spaces")
        print(">> " + Options.cef_build_dir)
        sys.exit(1)

    # --depot-tools-dir
    Options.depot_tools_dir = os.path.join(Options.cef_build_dir,
                                           "depot_tools")
    # binary_distrib
    Options.binary_distrib = os.path.join(Options.cef_build_dir, "chromium",
                                          "src", "cef", "binary_distrib")


def build_cef():
    """Build CEF from sources."""

    # Clone cef repo
    cef_dir = os.path.join(Options.cef_build_dir, "cef")
    if not os.path.exists(cef_dir):
        # Step 1a: clone cef repo and checkout branch
        run_git("clone %s cef" % CEF_GIT_URL, Options.cef_build_dir)
        run_git("checkout %s" % Options.cef_branch, cef_dir)
        # Step 1b: update cef patches
        update_cef_patches()
        # Make sure the cef_build_dir/chromium/cef/ directory
        # does not exist - it's a copy of the cef_build_dir/cef/ dir.
        cef_dir2 = os.path.join(Options.cef_build_dir, "chromium", "cef")
        assert not os.path.exists(cef_dir2)

    # Delete binary_distrib
    if os.path.exists(Options.binary_distrib):
        delete_directory(Options.binary_distrib)

    # Run automate-git.py
    run_automate_git()

    # Build cefclient, cefsimple, libcef_dll_wrapper
    build_cef_projects()

    # Copy bin/lib (eg cef_2526.gb660893_win32) to build/cef32/

    # Build the pycef module
    print("TODO: Build the pycef module")


def build_cef_projects():
    """Build cefclient, cefsimple, libcef_dll_wrapper."""
    print("[automate.py] Binary distrib created in %s"
          % Options.binary_distrib)
    print("[automate.py] Building cef projects...")

    # Find cef_binary directories and create the cef_binary/build/ dir
    files = glob.glob(os.path.join(Options.binary_distrib,
                                   "*_release_symbols"))
    assert len(files) == 1, "More than one dir with release symbols found"
    release_symbols = files[0]
    cef_binary = release_symbols.replace("_release_symbols", "")
    build_cefclient = os.path.join(cef_binary, "build_cefclient")
    build_wrapper_mt = os.path.join(cef_binary, "build_wrapper_mt")
    build_wrapper_md = os.path.join(cef_binary, "build_wrapper_md")
    os.makedirs(build_cefclient)
    os.makedirs(build_wrapper_mt)
    os.makedirs(build_wrapper_md)

    # Build cefclient and cefsimple
    print("[automate.py] Building cefclient and cefsimple...")
    command = ""
    if platform.system() == "Windows":
        if int(Options.cef_branch) >= 2704:
            command += VS2015_VCVARS + " && "
        else:
            command += VS2013_VCVARS + " && "
    command += "cmake -G \"Ninja\" -DCMAKE_BUILD_TYPE=Release .. && "
    command += "ninja cefclient cefsimple"
    run_command(command, build_cefclient)

    # Command to build libcef_dll_wrapper
    wrapper_command = ""
    if platform.system() == "Windows":
        wrapper_command += VS2008_VCVARS + " && "
    wrapper_command += "cmake -G \"Ninja\" -DCMAKE_BUILD_TYPE=Release .. && "
    wrapper_command += "ninja libcef_dll_wrapper"

    # Build libcef_dll_wrapper_mt.lib
    print("[automate.py] Building libcef_dll_wrapper /MT")
    if sys.version_info[:2] == (2, 7):
        old_gyp_msvs_version = Options.gyp_msvs_version
        Options.gyp_msvs_version = "2008"
        run_command(wrapper_command, build_wrapper_mt)
        Options.gyp_msvs_version = old_gyp_msvs_version
    else:
        print("ERROR: This python version is not yet supported")
        sys.exit(1)

    # Build libcef_dll_wrapper_md.lib
    print("[automate.py] Building libcef_dll_wrapper /MD")
    if sys.version_info[:2] == (2, 7):
        old_gyp_msvs_version = Options.gyp_msvs_version
        Options.gyp_msvs_version = "2008"
        # Replace /MT with /MD /wd\"4275\" in CMakeLists.txt
        # Warnings are treated as errors so this needs to be ignored:
        # >> warning C4275: non dll-interface class 'stdext::exception'
        # >> used as base for dll-interface class 'std::bad_cast'
        cmakelists = os.path.join(cef_binary, "CMakeLists.txt")
        with open(cmakelists, "rb") as fp:
            contents = fp.read()
        contents = contents.replace(r"/MT ", r"/MD /wd\"4275\" ")
        contents = contents.replace(r"/MTd ", r"/MDd /wd\"4275\" ")
        with open(cmakelists, "wb") as fp:
            fp.write(contents)
        run_command(wrapper_command, build_wrapper_md)
        Options.gyp_msvs_version = old_gyp_msvs_version
    else:
        print("ERROR: This python version is not yet supported")
        sys.exit(1)


def update_cef_patches():
    """Update cef/patch/ directory with PyCEF patches.
    Issue73 is applied in getenv() by setting appropriate env var.

    Note that this modifies only cef_build_dir/cef/ directory. If the
    build was run previously then there is a copy of the cef/ directory
    in the cef_build_dir/chromium/ directory which is not being updated.
    """
    print("[automate.py] Updating CEF patches with PyCEF patches")
    cef_dir = os.path.join(Options.cef_build_dir, "cef")
    cef_patch_dir = os.path.join(cef_dir, "patch")
    cef_patches_dir = os.path.join(cef_patch_dir, "patches")

    # Copy pycef/patches/*.patch to cef/patch/patches/
    pycef_patches_dir = os.path.join(Options.pycef_dir, "patches")
    pycef_patches = glob.glob(os.path.join(pycef_patches_dir, "*.patch"))
    for file_ in pycef_patches:
        print("[automate.py] Copying %s to %s"
              % (os.path.basename(file_), cef_patches_dir))
        shutil.copy(file_, cef_patches_dir)

    # Append pycef/patches/patch.py to cef/patch/patch.cfg
    cef_patch_cfg = os.path.join(cef_patch_dir, "patch.cfg")
    print("[automate.py] Overwriting %s" % cef_patch_cfg)
    with open(cef_patch_cfg, "rb") as fp:
        cef_patch_cfg_contents = fp.read()
        cef_patch_cfg_contents += "\n"
    pycef_patch_cfg = os.path.join(pycef_patches_dir, "patch.py")
    with open(pycef_patch_cfg, "rb") as fp:
        pycef_patch_cfg_contents = fp.read()
    with open(cef_patch_cfg, "wb") as fp:
        cef_patch_cfg_contents = cef_patch_cfg_contents.replace("\r\n", "\n")
        pycef_patch_cfg_contents = pycef_patch_cfg_contents.replace(
                                                                "\r\n", "\n")
        new_contents = cef_patch_cfg_contents + pycef_patch_cfg_contents
        fp.write(new_contents)


def prebuilt_cef():
    """Download CEF prebuilt binaries from GitHub Releases,
    eg tag 'upstream-cef47'."""
    pass


def getenv():
    """Env variables passed to shell when running commands."""
    env = os.environ
    env["PATH"] = Options.depot_tools_dir + os.pathsep + env["PATH"]
    env["GYP_GENERATORS"] = Options.gyp_generators
    env["GYP_MSVS_VERSION"] = Options.gyp_msvs_version
    # Issue73 patch applied here.
    env["GYP_DEFINES"] = "use_allocator=none"
    # Modifications to automate-git.py
    env["PYCEF_NINJA_JOBS"] = str(Options.ninja_jobs)
    return env


def run_command(command_line, working_dir):
    """Run command in a given directory with env variables set."""
    print("[automate.py] Running '"+command_line+"' in '" +
          working_dir+"'...")
    args = shlex.split(command_line.replace("\\", "\\\\"))
    return subprocess.check_call(args, cwd=working_dir, env=getenv(),
                                 shell=(platform.system() == "Windows"))


def run_python(command_line, working_dir):
    """Run python script using depot_tools."""
    python = "python"
    return run_command("%s %s" % (python, command_line), working_dir)


def run_git(command_line, working_dir):
    """Run git command using depot_tools."""
    return run_command("git %s" % command_line, working_dir)


def run_automate_git():
    """Run CEF automate-git.py."""
    # TODO: run automate-git.py using Python 2.7 from depot_tools
    script = os.path.join(Options.pycef_dir, "tools", "automate-git.py")
    """
    Example automate-git.py command:
        C:\chromium>call python automate-git.py --download-dir=./test/
        --branch=2526 --no-debug-build --verbose-build
    Run ninja build manually:
        cd chromium/src
        ninja -v -j2 -Cout\Release cefclient
    """
    args = []
    if ARCH64:
        args.append("--x64-build")
    args.append("--download-dir=" + Options.cef_build_dir)
    args.append("--branch=" + Options.cef_branch)
    args.append("--no-debug-build")
    args.append("--verbose-build")
    # --force-build sets --force-distrib by default
    # ninja will only recompile files that changed
    args.append("--force-build")
    # We clone cef repository ourselves and update cef patches with ours,
    # so don't fetch/update CEF repo.
    args.append("--no-cef-update")
    args.append("--no-distrib-archive")

    args = " ".join(args)
    return run_python(script+" "+args, Options.cef_build_dir)


def delete_directory(path):
    """Delete directory recursively."""
    if os.path.exists(path):
        print("[automate.py] Deleting directory %s" % path)
        shutil.rmtree(path, onerror=onerror)


def onerror(func, path, _):
    """Fix file permission on error and retry operation."""
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def pycef_version():
    """Get CEF version from the 'pycef/version/' directory."""
    header_file = os.path.join(Options.pycef_dir, "src", "version",
                               "cef_version_"+OS_POSTFIX+".h")
    with open(header_file, "rU") as fp:
        contents = fp.read()
    ret = dict()

    # cef_branch
    match = re.match(r"#define CHROME_VERSION_BUILD (\d+)", contents)
    if not match:
        print("[automate.py] CHROME_VERSION_BUILD not found in "+header_file)
        sys.exit(1)
    ret["cef_branch"] = match.group(1)

    # cef_commit
    match = re.match(r"#define CEF_COMMIT_HASH \"(\w+)\"", contents)
    if not match:
        print("[automate.py] CEF_COMMIT_HASH not found in "+header_file)
        sys.exit(1)
    ret["cef_commit"] = match.group(1)

    return ret


if __name__ == "__main__":
    main()
