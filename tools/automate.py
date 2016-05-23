# Copyright (c) 2016 PyCEF, see the Authors file. All rights reserved.

"""Build PyCEF. Use prebuilt CEF binaries or build CEF from sources.

Usage:
    automate.py (--prebuilt-cef | --build-cef)
                [--cef-branch BRANCH] [--cef-commit COMMIT]
                [--build-dir BUILDDIR] [--cef-build-dir CEFBUILDDIR]
                [--ninja-jobs <2>] [--gyp-generators <ninja,msvs-ninja>]
                [--gyp-msvs-version <2013>]
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
    --gyp-generators    Set GYP_GENERATORS [default: ninja,msvs-ninja].
    --gyp-msvs-version  Set GYP_MSVS_VERSION [default: 2013].

"""

import os
import sys
import shlex
import subprocess
import platform
import docopt
import struct
import re
import shutil
import stat
import glob
import shutil

# CONSTANTS
ARCH32 = (8 * struct.calcsize('P') == 32)
ARCH64 = (8 * struct.calcsize('P') == 64)
OS_POSTFIX = ("win" if platform.system() == "Windows" else
              "linux" if platform.system() == "Linux" else
              "mac" if platform.system() == "Darwin" else "unknown")

CEF_GIT_URL = "https://bitbucket.org/chromiumembedded/cef.git"


class Options(object):
    """Options from command-line and internal options."""

    # From command-line
    prebuilt_cef = False
    build_cef = False
    cef_branch = ""
    cef_commit = ""
    build_dir = ""
    cef_build_dir = ""
    ninja_jobs = "2"
    gyp_generators = "ninja"
    gyp_msvs_version = "2013"

    # Internal options
    depot_tools_dir = ""
    tools_dir = ""
    pycef_dir = ""


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
        print("[automate.py] ERROR: CEF branch is required")
        sys.exit(1)

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


def build_cef():
    """Build CEF from sources."""

    # Step 1: clone cef repository
    cef_dir = os.path.join(Options.cef_build_dir, "cef")
    if os.path.exists(cef_dir):
        delete_directory(cef_dir)
    run_git("clone %s cef" % CEF_GIT_URL, Options.cef_build_dir)
    run_git("checkout %s" % Options.cef_branch, cef_dir)

    # Step 2: update cef patches
    update_cef_patches()

    # Step 3: run automate-git.py
    run_automate_git()

    # Step 4: unpack and copy the libs/binaries
    print("TODO: Step 4: unpack and copy the libs/binaries")

    # Step 5: build the pycef module
    print("TODO: Step 5: build the pycef module")


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
    env["PYCEF_NINJA_JOBS"] = Options.ninja_jobs
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
