# Copyright (c) 2016 The PyCEF Authors. All rights reserved.

"""Run unit tests. Without arguments runs all. Read notes below.

Usage:
    _run.py [FILE | PATTERN | TESTCASE]

Options:
    FILE      Run tests from single file.
    PATTERN   Run tests from files matching this pattern.
    TESTCASE  Test cases matching pattern to run eg "file.TestCase"

Notes:
    - Files starting with "_" are ignored.
    - If test case name contains "NewPythonInstance" then for this
      test will be run using a new instance of Python interpreter.
    - Tested with only TestCase being used in tests. TestSuite usage
      is untested.
"""

import unittest
import os
import sys
from os.path import dirname, realpath
import re
import subprocess


def main(pattern=None):
    """Main entry point."""
    # Set working dir
    os.chdir(dirname(realpath(__file__)))

    # Script arguments
    testcasearg = ""
    if not pattern:
        if len(sys.argv) > 1:
            if ".py" in sys.argv[1]:
                # FILE or PATTERN arg
                pattern = sys.argv[1]
            else:
                # TESTCASE arg
                testcasearg = sys.argv[1]
        if not pattern:
            pattern = "[!_]*.py"

    # Auto discovery using glob pattern
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=".", pattern=pattern)
    # all suites except NewPythonInstance
    newsuite = unittest.TestSuite()
    # NewPythonInstance suites
    isolatedsuite = unittest.TestSuite()
    # TESTCASE arg passed, run only that testcase
    singlesuite = unittest.TestSuite()
    counttests = 0
    for subsuite in suite:
        for subsubsuite in subsuite:
            if isinstance(subsubsuite, unittest.TestSuite):
                for _ in subsubsuite:
                    counttests += 1
                for testcase in subsubsuite:
                    if testcasearg:
                        if re.match(re.escape(testcasearg), testcase.id()):
                            singlesuite.addTest(subsubsuite)
                        break
                    elif "NewPythonInstance" in testcase.id():
                        isolatedsuite.addTest(subsubsuite)
                        break
                    else:
                        newsuite.addTest(subsubsuite)
                        break
            elif not testcasearg:
                # unittest.loader.ModuleImportFailure
                newsuite.addTest(subsubsuite)

    # TESTCASE
    if testcasearg:
        if not singlesuite.countTestCases():
            print("[_run.py] ERROR: test case not found")
            sys.exit(1)
        else:
            runner = unittest.TextTestRunner(verbosity=2, descriptions=True)
            result = runner.run(singlesuite)
            if result.errors or result.failures:
                sys.exit(1)
            else:
                sys.exit(0)

    # Step 1: run new suite with NewPythonInstance cases removed
    newsuitecount = 0
    errors = 0
    failures = 0
    for _ in newsuite:
        newsuitecount += 1
    failed = False
    if newsuitecount:
        runner = unittest.TextTestRunner(verbosity=2, descriptions=True)
        result = runner.run(newsuite)
        failed = (result.errors or result.failures)
        errors += len(result.errors)
        failures += len(result.failures)
    
    # Step 2: run suite containing only NewPythonInstance cases
    failed = True if failed else False
    for testsuite in isolatedsuite:
        for testcase in testsuite:
            testcaseid = testcase.id()
            break
        try:
            output = subprocess.check_output(
                    ["python", "_run.py", testcaseid],
                    stderr=subprocess.STDOUT)
            retcode = 0
        except subprocess.CalledProcessError as exc:
            output = exc.output
            retcode = exc.returncode
        sys.stdout.write(output)
        if retcode:
            failed = True
            if output:
                lines = output.splitlines()
                lastline = lines[len(lines)-1]
                match = re.search(r"failures=(\d+)", lastline)
                if match:
                    failures += int(match.group(1))
                match = re.search(r"errors=(\d+)", lastline)
                if match:
                    errors += int(match.group(1))
    
    # Print summary
    print("-"*70)
    print("[_run.py] Ran "+str(counttests)+" tests in total")
    if failed:
        failedstr = "[_run.py] FAILED ("
        if failures:
            failedstr += ("failures="+str(failures))
        if errors:
            if failures:
                failedstr += ", "
            failedstr += ("errors="+str(errors))
        failedstr += ")"
        print(failedstr)
        sys.exit(1)
    else:
        print("[_run.py] OK")


if __name__ == "__main__":
    main()
