#!/usr/bin/env python

import sys
import time
import functools

from fuse import FUSE
from passthroughfs import Passthrough

def report(fn):
    @functools.wraps(fn)
    def wrap(*params,**kwargs):
        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
        ))
        print "%s called" % (fc)
        time.sleep(1)
        ret = fn(*params,**kwargs)
        #print "%s returned" % (fn.__name__)
        print "%s returned %s" % (fn.__name__, ret)
        return ret
    return wrap

def reportall(cls):
    for name, val in vars(cls).items():
        if callable(val) and not name.startswith('_'):
            setattr(cls, name, report(val))
    return cls

Passthrough = reportall(Passthrough)

def main(root, mountpoint):
    FUSE(Passthrough(root), mountpoint, foreground=True)

if __name__ == '__main__':
    main(sys.argv[-2], sys.argv[-1])
