#!/usr/bin/env python

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations

class Passthrough(Operations):
    def __init__(self, root):
        self.root = root

    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def destroy(self,path):
        return super(Passthrough,self).destroy(path)

    def exists(self, path):
        return os.path.exists(self._full_path(path))

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

    def fsyncdir(self,path, datasync, fh):
        return super(Passthrough,self).fsyncdir(path, datasync, fh)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def getxattr(self, path, name, position=0):
        return super(Passthrough,self).getxattr(path, name, position=0)

    def init(self, path):
        return super(Passthrough,self).init(path)

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def listxattr(self, path):
        return super(Passthrough,self).listxattr(path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def opendir(self, path):
        return super(Passthrough,self).opendir(path)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def release(self, path, fh):
        return os.close(fh)

    def releasedir(self, path, fh):
        return super(Passthrough,self).releasedir(path, fh)

    def removexattr(self, path, name):
        return super(Passthrough,self).removexattr(path, name)

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def setxattr(self, path, name, value, options, position=0):
        return super(Passthrough,self).setxattr(path, name, value, options, position=0)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))

    def symlink(self, target, name):
        return os.symlink(self._full_path(target), self._full_path(name))

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

def main(root, mountpoint):
    FUSE(Passthrough(root), mountpoint, foreground=True)

if __name__ == '__main__':
    main(sys.argv[-2], sys.argv[-1])
