#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a programmatic windows explorer behaviors implementation. A lots of
useful recipe help you easily control file, directory, file name, select,
rename, etc...

``file``, ``directory``, ``collection of files`` class
"""

from __future__ import print_function

import os
import copy
from datetime import datetime
from collections import OrderedDict

try:
    from .py23 import str_type
    from .printer import prt
    from .meth import repr_data_size, md5file
except:
    from filetool.py23 import str_type
    from filetool.printer import prt
    from filetool.meth import repr_data_size, md5file


class WinFile(object):
    """Represent a file.

    attributes includes:

    - self.abspath        absolute path (绝对路径)
    - self.dirname        parents directory name (父目录路径)
    - self.basename       complete file name (文件全名)
    - self.fname          the first part of file name (纯文件名)
    - self.ext            file extension (文件扩展名)
    - self.atime          last access time (文件最后一次被触碰的时间)
    - self.ctime          create time (文件被创建的时间)
    - self.mtime          last modify time (文件最后一次被修改的时间)
    - self.size_on_disk   file size in bytes (文件在硬盘上的大小, 单位bytes)
    - self.md5            md5 value (文件的md5值)

    Appendix, The difference of (atime, ctime, mtime):

    - access time (os.path.getatime)
    - create time (os.path.getctime)
    - modify time (os.path.getmtime)

    - When rename, cut-and-paste, all 3 time stays.
    - When edit the content, atime and mtime change, ctime stays.
    - When copy the file to a new place, atime and ctime change, mtime stays.

    **中文文档**

    Windows文件对象, 可以通过 .属性名的方式访问 绝对路径, 文件夹路径,
    文件名, 扩展名, 大小。免去了使用 ``os.path.split`` 等方法的麻烦。

    附录, atime, ctime, mtime的区别

    - 当文件被改名, 和剪切(剪切跟改名是一个操作), 所有3个时间都不变
    - 当文件内容被修改, atime, mtime变化, ctime不变
    - 当文件被复制到新位置时, atime, ctime变化, mtime不变
    """
    __slots__ = [
        "abspath", "dirname", "basename", "fname", "ext",
        "atime", "ctime", "mtime", "size_on_disk", "md5",
    ]
    init_mode = 2

    def __init__(self, abspath):
        if os.path.isfile(abspath):  # 确保这是一个文件而不是目录
            self.abspath = os.path.abspath(abspath)
            self.initialize()
        else:
            raise EnvironmentError(
                "%s is not a file or it doesn't exist." % abspath)

    def initialize(self):
        """Internal method. Initialize the value of some attributes.
        """
        self.level2_initialize()

    @staticmethod
    def use_fast_init():
        """Set initialization mode to level1_initialize
        """
        WinFile.initialize = WinFile.level1_initialize
        WinFile.init_mode = 1

    @staticmethod
    def use_regular_init():
        """Set initialization mode to level2_initialize
        """
        WinFile.initialize = WinFile.level2_initialize
        WinFile.init_mode = 2

    @staticmethod
    def use_slow_init():
        """Set initialization mode to level3_initialize
        """
        WinFile.initialize = WinFile.level3_initialize
        WinFile.init_mode = 3

    @staticmethod
    def set_initialize_mode(complexity=2):
        """Set initialization mode. Default is slow mode.

        - 1: fast mode, only file name relative
        - 2: regular mode, atime, ctime, mtime, size_on_disk
        - 3: slow mode, md5 checksum

        **中文文档**

        设置WinFile类的全局变量, 指定WinFile.initialize方法所绑定的初始化方式。
        """
        if complexity == 3:
            WinFile.initialize = WinFile.level3_initialize
            WinFile.init_mode = 3
        elif complexity == 2:
            WinFile.initialize = WinFile.level2_initialize
            WinFile.init_mode = 2
        elif complexity == 1:
            WinFile.initialize = WinFile.level1_initialize
            WinFile.init_mode = 1
        else:
            raise ValueError("complexity has to be 3, 2 or 1.")

    def level3_initialize(self):
        """Load abspath, dirname, basename, fname, ext, atime, ctime, mtime,
        size_on_disk attributes in initialization.

        **中文文档**

        比较全面但稍慢的WinFile对象初始化方法, 从绝对路径中取得:

        - 绝对路径
        - 父目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        - access time
        - create time
        - modify time
        - 文件占据磁盘大小
        - 文件的哈希值
        """
        self.dirname, self.basename = os.path.split(self.abspath)  # 目录名, 文件名
        self.fname, self.ext = os.path.splitext(self.basename)  # 纯文件名, 文件扩展名
        self.ext = self.ext.lower()

        self.size_on_disk = os.path.getsize(self.abspath)

        # 最后一次接触(打开, 调用)的时间
        self.atime = datetime.fromtimestamp(os.path.getatime(self.abspath))

        # 创建时间, 当文件被修改后不变
        self.ctime = datetime.fromtimestamp(os.path.getctime(self.abspath))

        # 最后一次修改的时间
        self.mtime = datetime.fromtimestamp(os.path.getmtime(self.abspath))
        self.md5 = md5file(self.abspath)  # 文件的哈希值

    def level2_initialize(self):
        """Load abspath, dirname, basename, fname, ext, atime, ctime, mtime,
        size_on_disk attributes in initialization.

        **中文文档**

        比较全面但稍慢的WinFile对象初始化方法, 从绝对路径中取得:

        - 绝对路径
        - 父目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        - access time
        - create time
        - modify time
        - 文件占据磁盘大小
        """
        self.dirname, self.basename = os.path.split(self.abspath)  # 目录名, 文件名
        self.fname, self.ext = os.path.splitext(self.basename)  # 纯文件名, 文件扩展名
        self.ext = self.ext.lower()

        self.size_on_disk = os.path.getsize(self.abspath)

        # 最后一次接触(打开, 调用)的时间
        self.atime = datetime.fromtimestamp(os.path.getatime(self.abspath))

        # 创建时间, 当文件被修改后不变
        self.ctime = datetime.fromtimestamp(os.path.getctime(self.abspath))

        # 最后一次修改的时间
        self.mtime = datetime.fromtimestamp(os.path.getmtime(self.abspath))

    def level1_initialize(self):
        """Load abspath, dirname, basename, fname, ext
        attributes in initialization.

        **中文文档**

        快速的WinFile对象初始化方法, 只从绝对路径中取得:

        - 绝对路径
        - 目录路径
        - 文件全名
        - 纯文件名
        - 文件扩展名
        """
        self.dirname, self.basename = os.path.split(self.abspath)
        self.fname, self.ext = os.path.splitext(self.basename)
        self.ext = self.ext.lower()

    def __str__(self):
        return self.abspath

    def __repr__(self):
        lines = list()

        attr_name_length = list()
        for attr in self.__slots__:
            if hasattr(self, attr):
                attr_name_length.append(len(attr))

        template = "{0: <%s}= " % (max(attr_name_length) + 1, )
        for attr in self.__slots__:
            try:
                line = "%s%r" % (template.format(attr), getattr(self, attr))
                lines.append(line)
            except:
                pass
        info = ",\n    ".join(lines)
        return "WinFile(\n    %s,\n)" % info

    def __hash__(self):
        return hash(self.abspath)

    def to_dict(self):
        """Convert :class:`WinFile` to dictionary.
        """
        d = dict()
        for attr in self.__slots__:
            try:
                d[attr] = self.__getattribute__(attr)
            except AttributeError:
                pass
        return d

    def update(self, new_dirname=None, new_fname=None, new_ext=None):
        """Update property, automatically update relative property.

        :param new_dirname: new dirname
        :param new_fname: new fname
        :param new_ext: new ext

        **中文文档**

        更新WinFile的属性。更新一个, 也同时更新其他相关的属性。例如更新
        extension时, 也自动更新basename和abspath。
        """
        if new_dirname:
            self.dirname = new_dirname

        if new_fname:
            self.fname = new_fname

        if new_ext:
            self.ext = new_ext

        self.basename = self.fname + self.ext
        self.abspath = os.path.join(self.dirname, self.basename)

    def copy(self):
        """Create a copy of this :class:`WinFile` instance.
        """
        return copy.deepcopy(self)

    def copy_to(self, dst, overwrite=False):
        """Copy this file to another place.

        :param dst: copy-to destination
        :param overwrite: if True, silently overwrite output file
        """
        if os.path.exists(dst):
            if not overwrite:
                raise FileExistsError("%s" % dst)
        with open(self.abspath, "rb") as f_in, open(dst, "wb") as f_out:
            f_out.write(f_in.read())

    def delete(self):
        """Delete this winfile.
        """
        os.remove(self.abspath)

    def rename(self, new_dirname=None, new_fname=None, new_ext=None):
        """Rename the dirname, fname, extension or their combinations.

        :param new_dirname: new dirname
        :param new_fname: new fname
        :param new_ext: new ext

        **中文文档**

        对文件的父目录名, 纯文件名, 扩展名, 或它们的组合进行修改。
        """
        if not new_dirname:
            new_dirname = self.dirname
        else:
            new_dirname = os.path.abspath(new_dirname)
        if not new_fname:
            new_fname = self.fname
        if new_ext:  # 检查新文件名的扩展名格式是否
            if not new_ext.startswith("."):
                raise ValueError("File extension must in format .ext, "
                                 "for example: .jpg, .mp3")
        else:
            new_ext = self.ext
        new_basename = new_fname + new_ext
        new_abspath = os.path.join(new_dirname, new_basename)

        os.rename(self.abspath, new_abspath)

        # 如果成功重命名, 则更新文件信息
        self.abspath = new_abspath
        self.dirname = new_dirname
        self.basename = new_basename
        self.fname = new_fname
        self.ext = new_ext

    #--- Boolean method ---
    def isfile(self):
        return os.path.isfile(self.abspath)

    def exists(self):
        return os.path.exists(self.abspath)


class WinDir(object):
    """Represent a directory.

    - self.size_total: total size of all files
    - self.size_current_total: total size of all files, not include file in
      subfolder

    - self.num_folder_total: number of all directory
    - self.num_folder_current: number of all directory, not include subfolder

    - self.num_file_total: number of all file
    - self.num_file_current: number of all file, not include file in subfolder

    **中文文档**

    Windows目录对象, 可以通过 .属性名来访问 绝对路径, 目录总大小, 子目录数量,
    子文件数量。免去了使用os.path.function的麻烦。

    WinDir的属性:

    - self.size_total: 文件夹总大小
    - self.size_current_total: 文件夹一级子文件总大小

    - self.num_folder_total: 子文件夹数量
    - self.num_folder_current: 一级子文件夹数量

    - self.num_file_total: 子文件数量
    - self.num_file_current: 一级子文件数量
    """
    __slots__ = [
        "abspath", "dirname", "basename",
        "size_total", "num_folder_total", "num_file_total",
        "size_current", "num_folder_current", "num_file_current",
    ]

    def __init__(self, abspath):
        if os.path.isdir(abspath):  # 确保这是一个目录而不是文件
            self.abspath = os.path.abspath(abspath)
            self.dirname, self.basename = os.path.split(self.abspath)
            self.get_detail()
        else:
            raise ValueError("'%s' is not a file." % abspath)

    def get_detail(self):
        """Get general stats information.

        Includes:

        - size_total: total size on disk
        - num_folder_total: how many subfolders
        - num_file_total: how many files
        - size_current: total size of files on this folder. file in subfolders
            doesn't count
        - num_folder_current: how many files, subfolders doens't count
        - num_file_current: how many files, file in subfolders doens't count
        """
        self.size_total = 0
        self.num_folder_total = 0
        self.num_file_total = 0

        self.size_current = 0
        self.num_folder_current = 0
        self.num_file_current = 0

        for current_dir, folderlist, fnamelist in os.walk(self.abspath):
            self.num_folder_total += len(folderlist)
            self.num_file_total += len(fnamelist)
            for fname in fnamelist:
                self.size_total += os.path.getsize(
                    os.path.join(current_dir, fname))

        current_dir, folderlist, fnamelist = next(os.walk(self.abspath))
        self.num_folder_current = len(folderlist)
        self.num_file_current = len(fnamelist)
        for fname in fnamelist:
            self.size_current += os.path.getsize(
                os.path.join(current_dir, fname))

    def __str__(self):
        return self.abspath

    def __repr__(self):
        lines = list()

        attr_name_length = list()
        for attr in self.__slots__:
            if hasattr(self, attr):
                attr_name_length.append(len(attr))

        template = "{0: <%s}= " % (max(attr_name_length) + 1, )
        for attr in self.__slots__:
            try:
                line = "%s%r" % (template.format(attr), getattr(self, attr))
                lines.append(line)
            except:
                pass
        info = ",\n    ".join(lines)
        return "WinDir(\n    %s,\n)" % info

    def to_dict(self):
        d = dict()
        for attr in self.__slots__:
            try:
                d[attr] = self.__getattribute__(attr)
            except AttributeError:
                pass
        return d

    def rename(self, new_dirname=None, new_basename=None):
        """Rename the dirname, basename or their combinations.

        **中文文档**

        对文件的目录名, 文件夹名, 或它们的组合进行修改。
        """
        if not new_basename:
            new_basename = self.basename
        if not new_dirname:
            new_dirname = self.dirname
        else:
            new_dirname = os.path.abspath(new_dirname)
        new_abspath = os.path.join(new_dirname, new_basename)
        os.rename(self.abspath, new_abspath)

        # 如果成功重命名, 则更新文件信息
        self.abspath = new_abspath
        self.dirname = new_dirname
        self.basename = new_basename


class FileCollection(object):
    """A container class of WinFile.

    Simplify file selection, removing, filtering, sorting operations.

    **中文文档**

    WinFile的专用容器, 主要用于方便的从文件夹中选取文件, 筛选文件, 并对指定文件集排序。
    当然, 可以以迭代器的方式对容器内的文件对象进行访问。
    """

    def __init__(self, path_or_path_list=list()):
        self.files = OrderedDict()  # {文件绝对路径: 包含各种详细信息的WinFile对象}

        path_or_path_list = self._preprocess(path_or_path_list)

        for abspath in path_or_path_list:
            winfile = WinFile(abspath)
            self.files[winfile.abspath] = winfile

    @staticmethod
    def _preprocess(path_or_path_list):
        """Preprocess input argument, whether if it is:

        1. abspath
        2. WinFile instance
        3. WinDir instance
        4. list or set of any of them

        It returns list of path.

        :return path_or_path_list: always return list of path

        **中文文档**

        预处理输入参数, 使得无论是绝对路径, WinFile, WinDir 或是他们的列表, 都
        能被FileCollection的方法所接受。
        """
        if not isinstance(path_or_path_list, (list, set)):
            path_or_path_list = [path_or_path_list, ]
        else:
            path_or_path_list = set(path_or_path_list)

        path_or_path_list = [str(path) for path in path_or_path_list]
        return path_or_path_list

    def __str__(self):
        if len(self.files) == 0:
            return "*** Empty FileCollection ***"
        try:
            return "\n".join(
                ["*** File Collection ***", ] + list(self.order))
        except:
            return "\n".join(
                ["*** File Collection ***", ] + list(self.files.keys()))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        """Get the ``index``th winfile.
        """
        try:
            return self.files[self.order[index]]
        except:
            index += 1
            for winfile in self.iterfiles():
                index -= 1
                if not index:
                    return winfile

    def __contains__(self, item):
        """Test if winfile in this file collection.
        """
        if isinstance(item, str):  # abspath
            abspath = os.path.abspath(item)
        elif isinstance(item, WinFile):  # WinFile
            abspath = item.abspath
        else:  # invalid type
            raise TypeError

        if abspath in self.files:
            return True
        else:
            return False

    def add(self, abspath_or_winfile, enable_verbose=True):
        """Add absolute path or WinFile to FileCollection.
        """
        if isinstance(abspath_or_winfile, str_type):
            winfile = WinFile(abspath_or_winfile)
        elif isinstance(abspath_or_winfile, WinFile):
            winfile = abspath_or_winfile
        else:
            raise TypeError

        if winfile.abspath in self.files:
            prt("'%s' already in this collections" % winfile, enable_verbose)
        else:
            self.files.setdefault(winfile.abspath, winfile)

    def remove(self, abspath_or_winfile, enable_verbose=True):
        """Remove absolute path or WinFile from FileCollection.
        """
        if isinstance(abspath_or_winfile, str_type):
            winfile = WinFile(abspath_or_winfile)
        elif isinstance(abspath_or_winfile, WinFile):
            winfile = abspath_or_winfile
        else:
            raise TypeError

        try:
            del self.files[winfile.abspath]
        except KeyError:
            if enable_verbose:
                prt("'%s' are not in this file collections" % winfile,
                    enable_verbose)

    @property
    def howmany(self):
        """An alias of __len__() method.
        """
        return len(self.files)

    def iterfiles(self):
        """Yield all WinFile object.
        """
        try:
            for path in self.order:
                yield self.files[path]
        except:
            for winfile in self.files.values():
                yield winfile

    def iterpaths(self):
        """Yield all WinFile's absolute path.
        """
        try:
            for path in self.order:
                yield path
        except:
            for path in self.files:
                yield path

    def __iter__(self):
        """Default iterator is to yield absolute paht only.
        """
        return self.iterpaths()

    @staticmethod
    def yield_all_file_path(dir_abspath):
        """File path iterator.

        **中文文档**

        遍历path目录下的所有文件, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            dir_abspath = os.path.abspath(dir_abspath)
            for current_folder, _, fnamelist in os.walk(dir_abspath):
                for fname in fnamelist:
                    yield os.path.join(current_folder, fname)
        else:
            raise EnvironmentError(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_winfile(dir_abspath):
        """WinFile instance iterator.

        **中文文档**

        遍历path目录下的所有文件, 返回WinFile。
        """
        for abspath in FileCollection.yield_all_file_path(dir_abspath):
            yield WinFile(abspath)

    @staticmethod
    def yield_all_top_file_path(dir_abspath):
        """File path iterator, except file in subfolder.

        **中文文档**

        遍历path目录下的所有文件, 不包括子文件夹中的文件, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            dir_abspath = os.path.abspath(dir_abspath)
            for current_folder, _, fnamelist in os.walk(dir_abspath):
                for fname in fnamelist:
                    yield os.path.join(current_folder, fname)
                break
        else:
            raise EnvironmentError(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_top_winfile(dir_abspath):
        """WinFile instance iterator, except file in subfolder.

        **中文文档**

        遍历path目录下的所有文件, 不包括子文件夹中的文件, 返回WinFile。
        """
        for abspath in FileCollection.yield_all_top_file_path(dir_abspath):
            yield WinFile(abspath)

    @staticmethod
    def yield_all_dir_path(dir_abspath):
        """Directory path iterator.

        **中文文档**

        遍历dir_abspath目录下的所有子目录, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            for current_folder, folderlist, _ in os.walk(dir_abspath):
                for folder in folderlist:
                    yield os.path.join(current_folder, folder)
        else:
            raise Exception(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_windir(dir_abspath):
        """WinDir instance iterator.

        **中文文档**

        遍历dir_abspath目录下的所有子目录, 返回绝对WinDir。
        """
        for abspath in FileCollection.yield_all_dir_path(dir_abspath):
            yield WinDir(abspath)

    @staticmethod
    def yield_all_top_dir_path(dir_abspath):
        """Directory path iterator, except directory in subfolder.

        **中文文档**

        遍历dir_abspath目录下的所有子目录, 不包括子目录中的子目录, 返回绝对路径。
        """
        if os.path.isdir(dir_abspath):
            for current_folder, folderlist, _ in os.walk(dir_abspath):
                for folder in folderlist:
                    yield os.path.join(current_folder, folder)
                break
        else:
            raise Exception(
                "'%s' may not exists or is not a directory!" % dir_abspath)

    @staticmethod
    def yield_all_top_windir(dir_abspath):
        """Directory instance iterator, except directory in subfolder.

        **中文文档**

        遍历dir_abspath目录下的所有子目录, 不包括子目录中的子目录, 返回绝对WinDir。
        """
        for abspath in FileCollection.yield_all_top_dir_path(dir_abspath):
            yield WinDir(abspath)

    @staticmethod
    def from_path(path_or_path_list):
        """Create a new FileCollection and add all files from ``dir_path``.

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.

        **中文文档**

        添加dir_path目录下的所有文件到一个新的FileCollection中.
        """
        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        fc = FileCollection()
        for dir_path in path_or_path_list:
            for winfile in FileCollection.yield_all_winfile(dir_path):
                fc.files.setdefault(winfile.abspath, winfile)
        return fc

    @staticmethod
    def from_path_by_criterion(path_or_path_list, criterion, keepboth=False):
        """Create a new FileCollection, and select some files from ``dir_path``.

        How to construct your own criterion function::

            def filter_image(winfile):
                if winfile.ext in [".jpg", ".png", ".bmp"]:
                    return True
                else:
                    return False

            fc = FileCollection.from_path_by_criterion(dir_path, filter_image)

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.
        :param criterion: customize filter function
        :type criterion: function
        :param keepboth: if True, returns two file collections, one is files
            with criterion=True, another is False.
        :type keepboth: boolean

        **中文文档**

        直接选取dir_path目录下所有文件, 根据criterion中的规则, 生成
        FileCollection。
        """
        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        if keepboth:
            fc_yes, fc_no = FileCollection(), FileCollection()
            for dir_path in path_or_path_list:
                for winfile in FileCollection.yield_all_winfile(dir_path):
                    if criterion(winfile):
                        fc_yes.files.setdefault(winfile.abspath, winfile)
                    else:
                        fc_no.files.setdefault(winfile.abspath, winfile)
            return fc_yes, fc_no
        else:
            fc = FileCollection()
            for dir_path in path_or_path_list:
                for winfile in FileCollection.yield_all_winfile(dir_path):
                    if criterion(winfile):
                        fc.files.setdefault(winfile.abspath, winfile)
            return fc

    @staticmethod
    def from_path_except(path_or_path_list,
                         ignore=None, ignore_ext=None, ignore_pattern=None):
        """Create a new FileCollection, and select all files except file
        matching ignore-rule::

            dir_path = "your/path"
            fc = FileCollection.from_path_except(
                dir_path, ignore=["test"], ignore_ext=[".log", ".tmp"]
                ignore_pattern=["some_pattern"])

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.
        :param ignore: file or directory defined in this list will be ignored.
        :param ignore_ext: file with extensions defined in this list will be ignored.
        :param ignore_pattern: any file or directory that contains this pattern
          will be ignored.

        **中文文档**

        选择dir_path下的所有文件, 在ignore, ignore_ext, ignore_pattern中所定义
        的文件将被排除在外。
        """
        if ignore is None:
            ignore = list()
        elif isinstance(ignore, str_type):
            ignore = [ignore, ]

        if ignore_ext is None:
            ignore_ext = list()
        elif isinstance(ignore_ext, str_type):
            ignore_ext = [ignore_ext, ]

        if ignore_pattern is None:
            ignore_pattern = list()
        elif isinstance(ignore_pattern, str_type):
            ignore_pattern = [ignore_pattern, ]

        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        ignore = [i.lower() for i in ignore]
        ignore_ext = [i.lower() for i in ignore_ext]
        ignore_pattern = [i.lower() for i in ignore_pattern]

        fc = FileCollection()
        for dir_path in path_or_path_list:
            def filter(winfile):
                relpath = os.path.relpath(winfile.abspath, dir_path).lower()

                # exclude ignore
                for path in ignore:
                    if relpath.startswith(path):
                        return False

                # exclude ignore extension
                if winfile.ext in ignore_ext:
                    return False

                # exclude ignore pattern
                for pattern in ignore_pattern:
                    if pattern in relpath:
                        return False

                return True

            for winfile in FileCollection.yield_all_winfile(dir_path):
                if filter(winfile):
                    fc.files.setdefault(winfile.abspath, winfile)

        return fc

    @staticmethod
    def from_path_by_pattern(path_or_path_list, pattern=None):
        """Create a new FileCollection, and select all files except file
        matching ignore-rule::

            dir_path = "your/path"
            fc = FileCollection.from_path_by_pattern(
                dir_path, pattern=["log"])

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.
        :param pattern: any file or directory that contains this pattern
          will be selected.

        **中文文档**

        选择dir_path下的所有文件的相对路径中包含有pattern的文件。
        """
        if pattern is None:
            pattern = list()
        elif isinstance(pattern, str_type):
            pattern = [pattern, ]

        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        pattern = [i.lower() for i in pattern]

        fc = FileCollection()
        for dir_path in path_or_path_list:
            def filter(winfile):
                relpath = os.path.relpath(winfile.abspath, dir_path).lower()
                for p in pattern:
                    if p in relpath:
                        return True
                return False

            for winfile in FileCollection.yield_all_winfile(dir_path):
                if filter(winfile):
                    fc.files.setdefault(winfile.abspath, winfile)
        return fc

    @staticmethod
    def from_path_by_size(path_or_path_list, min_size=0, max_size=1 << 40):
        """Create a new FileCollection, and select all files that size in
        a range::

            dir_path = "your/path"

            # select by file size larger than 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, min_size=100*1024*1024)

            # select by file size smaller than 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, max_size=100*1024*1024)

            # select by file size from 1MB to 100MB
            fc = FileCollection.from_path_by_size(
                dir_path, min_size=1024*1024, max_size=100*1024*1024)

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.
        :param min_size: any file size greater than this value will return
        :param max_size: any file size less than this value will return
        """
        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        def filter(winfile):
            if (winfile.size_on_disk >= min_size) and \
                    (winfile.size_on_disk <= max_size):
                return True
            else:
                return False

        return FileCollection.from_path_by_criterion(
            path_or_path_list, filter, keepboth=False)

    @staticmethod
    def from_path_by_ext(path_or_path_list, ext):
        """Create a new FileCollection, and select all files that extension
        matching ``ext``::

            dir_path = "your/path"

            fc = FileCollection.from_path_by_ext(dir_path, ext=[".jpg", ".png"])

        :param path_or_path_list: absolute dir path, WinDir instance, list of
          absolute dir path or list of WinDir instance.
        :param ext: select file by extension
        """
        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        if isinstance(ext, (list, set, dict)):  # collection of extension
            def filter(winfile):
                if winfile.ext in ext:
                    return True
                else:
                    return False
        else:  # str
            def filter(winfile):
                if winfile.ext == ext:
                    return True
                else:
                    return False

        return FileCollection.from_path_by_criterion(
            path_or_path_list, filter, keepboth=False)

    @staticmethod
    def from_path_by_md5(path_or_path_list, md5_value):
        """Create a new FileCollection, and select all files' that md5 is
        matching.

        **中文文档**

        给定一个文件使用WinFile模块获得的md5值, 在list_of_dir中的文件里,
        找到与之相同的文件。
        """
        path_or_path_list = FileCollection._preprocess(path_or_path_list)

        def filter(winfile):
            if winfile.md5 == md5_value:
                return True
            else:
                return False

        init_mode = WinFile.init_mode
        WinFile.use_slow_init()
        fc = FileCollection.from_path_by_criterion(
            path_or_path_list, filter, keepboth=False)

        WinFile.set_initialize_mode(complexity=init_mode)

        return fc

    def sort_by(self, attr_name, reverse=False):
        """Sort files by one of it's attributes.

        **中文文档**

        对容器内的WinFile根据其某一个属性升序或者降序排序。
        """
        try:
            d = dict()
            for abspath, winfile in self.files.items():
                d[abspath] = getattr(winfile, attr_name)
            self.order = [item[0] for item in sorted(
                list(d.items()), key=lambda t: t[1], reverse=reverse)]
        except AttributeError:
            raise ValueError("valid sortable attributes are: "
                             "abspath, dirname, basename, fname, ext, "
                             "size_on_disk, atime, ctime, mtime;")

    def sort_by_abspath(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **绝对路径** 进行排序。
        """
        self.sort_by("abspath", reverse=reverse)

    def sort_by_dirname(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **父目录路径** 进行排序。
        """
        self.sort_by("dirname", reverse=reverse)

    def sort_by_fname(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **纯文件名** 进行排序。
        """
        self.sort_by("fname", reverse=reverse)

    def sort_by_ext(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **文件扩展名** 进行排序。
        """
        self.sort_by("ext", reverse=reverse)

    def sort_by_atime(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **文件最后一次被触碰的时间** 进行排序。
        """
        self.sort_by("atime", reverse=reverse)

    def sort_by_ctime(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **文件被创建的时间** 进行排序。
        """
        self.sort_by("ctime", reverse=reverse)

    def sort_by_mtime(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **文件最后一次被修改的时间** 进行排序。
        """
        self.sort_by("mtime", reverse=reverse)

    def sort_by_size(self, reverse=False):
        """

        **中文文档**

        对WinFile根据 **文件在硬盘上的大小** 进行排序。
        """
        self.sort_by("size_on_disk", reverse=reverse)

    def select(self, criterion, keepboth=False):
        """Filter current file collections, create another file collections
        contains all winfile with criterion=True.

        How to construct your own criterion function, see
        :meth:`FileCollection.from_path_by_criterion`.

        :param criterion: customize filter function
        :type criterion: function
        :param keepboth: if True, returns two file collections, one is files
            with criterion=True, another is False.
        :type keepboth: boolean

        **中文文档**

        在当前的文件集合中, 根据criterion中的规则, 选择需要的生成
        FileCollection。当keepboth参数=True时, 返回两个FileCollection, 一个
        是符合条件的文件集合, 一个是不符合条件的。
        """
        if keepboth:
            fcs_yes, fcs_no = FileCollection(), FileCollection()
            for winfile in self.files.values():
                if criterion(winfile):
                    fcs_yes.files[winfile.abspath] = winfile
                else:
                    fcs_no.files[winfile.abspath] = winfile
            return fcs_yes, fcs_no
        else:
            fcs = FileCollection()
            for winfile in self.files.values():
                if criterion(winfile):
                    fcs.files[winfile.abspath] = winfile

            return fcs

    def __add__(self, other_fc):
        if not isinstance(other_fc, FileCollection):
            raise TypeError(
                "A FileCollection has to add with another FileCollection")

        fc = copy.deepcopy(self)
        for winfile in other_fc.iterfiles():
            fc.files.setdefault(winfile.abspath, winfile)
        return fc

    @staticmethod
    def sum(list_of_fc):
        for fc in list_of_fc:
            if not isinstance(fc, FileCollection):
                raise TypeError("FileCollection.sum(list_of_fc) only take "
                                "list of FileCollection")

        _fc = FileCollection()
        for fc in list_of_fc:
            for winfile in fc.iterfiles():
                _fc.files.setdefault(winfile.abspath, winfile)
        return _fc

    def __sub__(self, other_fc):
        if not isinstance(other_fc, FileCollection):
            raise TypeError(
                "A FileCollection has to add with another FileCollection")

        fc = copy.deepcopy(self)
        for abspath in other_fc.iterpaths():
            try:
                del fc.files[abspath]
            except:
                pass
        return fc

    #--- Useful recipe ---
    @staticmethod
    def show_big_file(dir_path, threshold):
        """Print all file path that file size greater and equal than
        ``#threshold``.
        """
        fc = FileCollection.from_path_by_size(dir_path, min_size=threshold)
        fc.sort_by("size_on_disk")

        lines = list()
        lines.append("Results:")
        for winfile in fc.iterfiles():
            lines.append("  %s - %s" %
                         (repr_data_size(winfile.size_on_disk), winfile))
        lines.append("Above are files' size greater than %s." %
                     repr_data_size(threshold))
        text = "\n".join(lines)
        print(text)
        with open("__show_big_file__.log", "wb") as f:
            f.write(text.encode("utf-8"))

    @staticmethod
    def show_patterned_file(dir_path, pattern=list(), filename_only=True):
        """Print all file that file name contains ``pattern``.
        """
        pattern = [i.lower() for i in pattern]
        if filename_only:
            def filter(winfile):
                for p in pattern:
                    if p in winfile.fname.lower():
                        return True
                return False
        else:
            def filter(winfile):
                for p in pattern:
                    if p in winfile.abspath.lower():
                        return True
                return False

        fc = FileCollection.from_path_by_criterion(
            dir_path, filter, keepboth=False)
        if filename_only:
            fc.sort_by("fname")
        else:
            fc.sort_by("abspath")

        table = {p: "<%s>" % p for p in pattern}
        lines = list()
        lines.append("Results:")
        for winfile in fc.iterfiles():
            lines.append("  %s" % winfile)

        if filename_only:
            lines.append(
                "Above are all files that file name contains %s" % pattern)
        else:
            lines.append(
                "Above are all files that abspath contains %s" % pattern)

        text = "\n".join(lines)
        print(text)
        with open("__show_patterned_file__.log", "wb") as f:
            f.write(text.encode("utf-8"))

    @staticmethod
    def create_fake_mirror(src, dst):
        """Copy all dir, files from ``src`` to ``dst``. But only create a empty file
        with same file name. Of course, the tree structure doesn't change.

        A recipe gadget to create some test data set.

        Make sure to use absolute path.

        **中文文档**

        复制整个src目录下的文件树结构到dst目录。但实际上并不复制内容, 只复制
        文件名。即, 全是空文件, 但目录结构一致。
        """
        src = os.path.abspath(src)
        if not (os.path.exists(src) and (not os.path.exists(dst))):
            raise Exception("source not exist or distination already exist")

        folder_to_create = list()
        file_to_create = list()

        for current_folder, _, file_list in os.walk(src):
            relpath = os.path.relpath(current_folder, src)
            if relpath == ".":
                new_folder = dst
            else:
                new_folder = os.path.join(dst, relpath)
            folder_to_create.append(new_folder)
            for basename in file_list:
                file_to_create.append(os.path.join(new_folder, basename))

        for abspath in folder_to_create:
            os.mkdir(abspath)

        for abspath in file_to_create:
            with open(abspath, "w") as _:
                pass


class FileFilter(object):
    """File filter container class.
    """
    @staticmethod
    def image(winfile):
        """Image file filter.
        """
        if winfile.ext in [".jpg", ".jpeg", ".png", ".gif", ".tiff",
                           ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg"]:
            return True
        else:
            return False

    @staticmethod
    def audio(winfile):
        """Audio file filter.
        """
        if winfile.ext in [".mp3", ".mp4", ".aac", ".m4a", ".wma",
                           ".wav", ".ape", ".tak", ".tta",
                           ".3gp", ".webm", ".ogg", ]:
            return True
        else:
            return False

    @staticmethod
    def video(winfile):
        """Video file filter.
        """
        if winfile.ext in [".avi", ".wmv", ".mkv", ".mp4", ".flv",
                           ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
                           ".mpg", ".mpeg", ".m4v", ".iso", ]:
            return True
        else:
            return False

    @staticmethod
    def pdf(winfile):
        """Pdf file filter.
        """
        if winfile.ext == ".pdf":
            return True
        else:
            return False

    @staticmethod
    def word(winfile):
        """Microsoft Word file filter.
        """
        if winfile.ext in [".doc", ".docx", ".docm", ".dotx", ".dotm", ".docb"]:
            return True
        else:
            return False

    @staticmethod
    def excel(winfile):
        """Microsoft Excel file filter.
        """
        if winfile.ext in [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm"]:
            return True
        else:
            return False

    @staticmethod
    def ppt(winfile):
        """Microsoft Power Point file filter.
        """
        if winfile.ext == ".ppt":
            return True
        else:
            return False

    @staticmethod
    def archive(winfile):
        """Compressed archive file filter.
        """
        if winfile.ext in [".zip", ".rar", ".gz", ".tar.gz", ".tgz", ".7z"]:
            return True
        else:
            return False
