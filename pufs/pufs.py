#!/usr/bin/env python

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations
from multiprocessing.dummy import Pool
import functools
import itertools

from passthroughfs import Passthrough

def mycall(func, *args, **kwargs):
    def f(self):
        return func(self,*args,**kwargs)
    return f

def checkexists(func):
    @functools.wraps(func)
    def f(*args, **kwargs):
        self, path = args[0:2]
        if self.exists(path):
            return func(*args, **kwargs)
        else:
            return None
    return f


def callget(child):
    return child.get()

def mappool(func):
    @functools.wraps(func)
    def f(*args, **kwargs):
        pufs = args[0]
        children = []
        for obj in pufs.subfs:
            newargs = [obj] + list(args[1:])
            children.append(pufs.pool.apply_async(func,newargs,kwargs))
        results = pufs.pool.map(callget,children)
        return results
    return f

def sumresults(callback):
    def mysum(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            results = func(*args, **kwargs)
            return callback([x for x in results if x != None])
        return f
    return mysum

def allorerror(x):
    if not any(x):
        raise FuseOSError(errno.EACCES)
    return None

def first(func):
    def callback(x):
        if len(x) > 0:
            return x[0]
        else:
            raise OSError(2, "No such file or directory")
    return sumresults(callback)(func)

def join(func):
    def callback(x):
        return list(itertools.chain.from_iterable(x))
    return sumresults(callback)(func)

class Pufs(Operations):
    def __init__(self, roots, threadspersource=10):
        self.subfs = []
        for root in roots:
            self.subfs.append(Passthrough(root))
        self.pool = Pool(len(self.subfs) * threadspersource)

    @sumresults(allorerror)
    @mappool
    @checkexists
    def access(self, path, mode):
        return os.access(self._full_path(path), mode)

    # chmod = mappool(checkexists(Passthrough.chmod))
    # chown = mappool(checkexists(Passthrough.chown))
    # create = mappool(checkexists(Passthrough.create))
    destroy = first(mappool(checkexists(Passthrough.destroy)))
    flush = first(mappool(checkexists(Passthrough.flush)))
    fsync = first(mappool(checkexists(Passthrough.fsync)))
    fsyncdir = first(mappool(checkexists(Passthrough.fsyncdir)))
    getattr = first(mappool(checkexists(Passthrough.getattr)))
    getxattr = first(mappool(checkexists(Passthrough.getxattr)))
    init = first(mappool(Passthrough.init))
    # link = mappool(checkexists(Passthrough.link))
    listxattr = first(mappool(checkexists(Passthrough.listxattr)))
    # mkdir = mappool(checkexists(Passthrough.mkdir))
    # mknod = mappool(checkexists(Passthrough.mknod))
    open = first(mappool(checkexists(Passthrough.open)))
    opendir = first(mappool(checkexists(Passthrough.opendir)))
    read = first(mappool(checkexists(Passthrough.read)))
    readdir = join(mappool(checkexists(Passthrough.readdir)))
    readlink = first(mappool(checkexists(Passthrough.readlink)))
    release = first(mappool(checkexists(Passthrough.release)))
    releasedir = first(mappool(checkexists(Passthrough.releasedir)))
    # removexattr = mappool(checkexists(Passthrough.removexattr))
    # rename = mappool(checkexists(Passthrough.rename))
    # rmdir = mappool(checkexists(Passthrough.rmdir))
    # setxattr = mappool(checkexists(Passthrough.setxattr))
    statfs = first(mappool(checkexists(Passthrough.statfs)))
    # symlink = mappool(checkexists(Passthrough.symlink))
    # truncate = mappool(checkexists(Passthrough.truncate))
    # unlink = mappool(checkexists(Passthrough.unlink))
    # utimens = mappool(checkexists(Passthrough.utimens))
    # write = mappool(checkexists(Passthrough.write))

def main(roots, mountpoint):
    FUSE(Pufs(roots), mountpoint, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1:-1], sys.argv[-1])
