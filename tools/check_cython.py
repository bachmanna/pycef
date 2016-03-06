"""Check Cython code for common mistakes. Exit with code 1 on error.
   This script is called in build.py .

- Move cef3/windows/setup/fix_pyx_files.py > ExceptAllMissing here
- Check all classes/functions exposed to Python whether all
  str parameters to functions are converted using pystring() - this
  function convers user-supplied string to unicode.
    - Or maybe that's an unnecessary overhead? Most of these strings
      will be converted to C/CEF strings when calling CEF API. However
      if we don't convert to unicode then code is more prone to bugs,
      as it needs always to be remembered that this string can either
      be str or unicode.
- Such check should also be made when calling callback functions
  supplied by user via interfaces (LoadHandler etc). 
    - This could be accomplished by wrapping user-supplied callback with our
      own callback and which will check all parameters of type "cdef pystr"
      (or pystring? PyStr? Str? currently using py_string type. Cannot use
      "pystr" as there is already function pystr - see above. Or maybe use 
      basestring for out-to-user-code-strings?)
"""
