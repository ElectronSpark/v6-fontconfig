#!/usr/bin/env python3

import os
import sys
import argparse
import platform
from pathlib import PurePath

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('availpath')
    parser.add_argument('confpath')
    parser.add_argument('links', nargs='+')
    args = parser.parse_args()

    if os.path.isabs(args.availpath):
        destdir = os.environ.get('DESTDIR')
        if destdir:
            availpath = str(PurePath(destdir, *PurePath(args.availpath).parts[1:]))
        else:
            availpath = args.availpath
    else:
        availpath = os.path.join(os.environ['MESON_INSTALL_DESTDIR_PREFIX'], args.availpath)

    if os.path.isabs(args.confpath):
        destdir = os.environ.get('DESTDIR')
        if destdir:
            # c:\destdir + c:\prefix must produce c:\destdir\prefix
            confpath = str(PurePath(destdir, *PurePath(args.confpath).parts[1:]))
        else:
            confpath = args.confpath
    else:
        confpath = os.path.join(os.environ['MESON_INSTALL_DESTDIR_PREFIX'], args.confpath)

    if not os.path.exists(confpath):
        os.makedirs(confpath)

    # xv6's currently staged fontconfig/libxml path cannot parse these newer
    # snippets cleanly, and stale incremental installs leave them reachable via
    # XDG_DATA_DIRS even when they are no longer active conf.d links.
    for name in ('48-guessfamily.conf', '49-sansserif.conf'):
        try:
            os.remove(os.path.join(availpath, name))
        except FileNotFoundError:
            pass

    for name in os.listdir(confpath):
        path = os.path.join(confpath, name)
        if name.endswith('.conf') and os.path.islink(path):
            os.remove(path)

    for link in args.links:
        src = os.path.join(availpath, link)
        dst = os.path.join(confpath, link)
        try:
            os.remove(dst)
        except FileNotFoundError:
            pass
        try:
            os.symlink(os.path.relpath(src, start=args.confpath), dst)
        except NotImplementedError:
            # Not supported on this version of Windows
            break
        except OSError as e:
            # Symlink privileges are not available
            if platform.system().lower() == 'windows' and e.winerror == 1314:
                break
            raise
