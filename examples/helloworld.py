"""Hello World example."""
# Any changes here must be applied to unit tests as well.

import pycef as cef
from cef.browser import Browser

Browser(url="https://www.google.com/")
cef.run()
