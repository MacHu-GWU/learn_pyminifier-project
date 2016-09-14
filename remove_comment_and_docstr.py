#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from dataIO.textfile import read, write
from filetool.files import FileCollection
from pyminifier.minification import remove_comments_and_docstrings


dir_path = "filetool"
for winfile in FileCollection.from_path_by_ext(dir_path, ".py").iterfiles():
    print("Minimize '%s' ..." % winfile)
    before = read(winfile.abspath)
    after = remove_comments_and_docstrings(before)
    after = after.replace("Sanhe Hu", "Lucas")
    write(after, winfile.abspath)
print("Complete!")
    