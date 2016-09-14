#!/usr/bin/env python
# -*- coding: utf-8 -*-


import hashlib


def repr_data_size(size_in_bytes, precision=2):
    """Return human readable string represent of a file size. Doesn"t support 
    size greater than 1EB.
    
    For example:
    
    - 100 bytes => 100 B
    - 100,000 bytes => 97.66 KB
    - 100,000,000 bytes => 95.37 MB
    - 100,000,000,000 bytes => 93.13 GB
    - 100,000,000,000,000 bytes => 90.95 TB
    - 100,000,000,000,000,000 bytes => 88.82 PB
    ...
    
    Magnitude of data::
    
        1000         kB    kilobyte
        1000 ** 2    MB    megabyte
        1000 ** 3    GB    gigabyte
        1000 ** 4    TB    terabyte
        1000 ** 5    PB    petabyte
        1000 ** 6    EB    exabyte
        1000 ** 7    ZB    zettabyte
        1000 ** 8    YB    yottabyte
    """
    if size_in_bytes < 1024:
        return "%s B" % size_in_bytes
    
    magnitude_of_data = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    index = 0
    while 1:
        index += 1
        size_in_bytes, mod = divmod(size_in_bytes, 1024)
        if size_in_bytes < 1024:
            break
    template = "{0:.%sf} {1}" % precision
    s = template.format(size_in_bytes + mod/1024.0, magnitude_of_data[index])
    return s


def md5file(abspath, nbytes=0):
    """Return md5 hash value of a piece of a file
    
    Estimate processing time on:
    
    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0, hash all file
    
    CPU = i7-4600U 2.10GHz - 2.70GHz, RAM = 8.00 GB
    1 second can process 0.25GB data
    
    - 0.59G - 2.43 sec
    - 1.3G - 5.68 sec
    - 1.9G - 7.72 sec
    - 2.5G - 10.32 sec
    - 3.9G - 16.0 sec
    """    
    m = hashlib.md5()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(4 * 1 << 16) # only use first 4GB data
                if not data:
                    break
                m.update(data)
    return m.hexdigest()


#--- Unittest ---
if __name__ == "__main__":
    import unittest
    
    class Unittest(unittest.TestCase):
        def test_repr_data_size(self):
            size_list = [100 * 1000 ** i for i in range(9)]
            repr_list = [
                "100 B", "97.66 KB", "95.37 MB", 
                "93.13 GB", "90.95 TB", "88.82 PB", 
                "86.74 EB", "84.70 ZB", "82.72 YB",
            ]
            
            for size, str_repr in zip(size_list, repr_list):
                self.assertEqual(repr_data_size(size, precision=2), str_repr)
        
        def test_md5file(self):
            md5 = md5file("meth.py")
            
    unittest.main()