# Copyright (c) 2016 The PyCEF Authors. All rights reserved.

"""Test unittest."""

import unittest

# Globals
count = 0


class Test(unittest.TestCase):
    count = 0

    @classmethod
    def setUpClass(cls):
        print("setUpClass: "+str(cls))

    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")

    def test_a1(self):
        global count
        count += 1
        self.count += 1
        print(count)
        print(self.count)

    def test_a2(self):
        global count
        count += 1
        self.count += 1
        print(count)
        print(self.count)


if __name__ == "__main__":
    unittest.main()
