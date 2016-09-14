#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
file backup utility method.
"""

from __future__ import print_function

import os
from zipfile import ZipFile
from datetime import datetime

try:
    from .files import WinFile, FileCollection, repr_data_size
except:
    from filetool.files import WinFile, FileCollection, repr_data_size


def backup_dir(filename, root_dir, ignore=None, ignore_ext=None, ignore_pattern=None):
    """The backup utility method. Basically it just add files that need to be
    backupped to zip archives.

    :param filename: the output file name, DO NOT NEED FILE EXTENSION.
    :param root_dir: the directory you want to backup.
    :param ignore: file or directory defined in this list will be ignored.
    :param ignore_ext: file with extensions defined in this list will be ignored.
    :param ignore_pattern: any file or directory that contains this pattern
      will be ignored.
    """
    tab = "    "
    # Step 1, calculate files to backup
    root_dir = os.path.abspath(root_dir)
    print("Perform backup '%s'..." % root_dir)
    print(tab + "1. Calculate files...")

    total_size_in_bytes = 0

    init_mode = WinFile.init_mode
    WinFile.use_regular_init()
    fc = FileCollection.from_path_except(
        root_dir, ignore, ignore_ext, ignore_pattern)
    WinFile.set_initialize_mode(complexity=init_mode)

    for winfile in fc.iterfiles():
        total_size_in_bytes += winfile.size_on_disk

    # Step 2, write files to zip archive
    print(tab * 2 + "Done, got %s files, total size is %s." % (
        len(fc), repr_data_size(total_size_in_bytes)))
    print(tab + "2. Backup files...")

    basename = "%s %s.zip" % (
        filename, datetime.now().strftime("%Y-%m-%d %Hh-%Mm-%Ss"))

    print(tab * 2 + "Write to '%s'..." % basename)
    current_dir = os.getcwd()
    with ZipFile(basename, "w") as f:
        os.chdir(root_dir)
        for winfile in fc.iterfiles():
            relpath = os.path.relpath(winfile.abspath, root_dir)
            f.write(relpath)
    os.chdir(current_dir)

    print(tab + "Complete!")
