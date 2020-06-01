# MIT License

# Copyright (c) 2018 Jaden Geller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import inspect
import platform

def _default_args(func):
    if platform.python_version().startswith("2."):
        return inspect.getargspec(func).defaults
    else:
        return [
            name 
            for name, parameter in inspect.signature(func).parameters.items()
            if parameter.default is not inspect.Parameter.empty
        ]

def implicits(*implicit_arg_names):
    def decorator(func):
        defaults = _default_args(func)
        def wrapper(*args, **kwargs):
            caller = inspect.currentframe().f_back
            caller_locals = caller.f_locals
            caller_globals = caller.f_globals
            for name in implicit_arg_names:
                if name in kwargs:
                    continue
                elif name in caller_locals:
                    kwargs[name] = caller_locals[name]
                elif name in caller_globals:
                    kwargs[name] = caller_globals[name]
                elif name not in defaults:
                    raise NameError(f"implicit name '{name}' is not defined in caller's locals or globals")
            return func(*args, **kwargs)
        return wrapper
    return decorator