# A Data class that absctracts file operations on disk, in memory, and on decelium

from datasources.PyFileSystem import PyFileSystem
from datasources.PyMemorySystem import PyMemorySystem

def get_fs(fstype,path):
    if fstype == "py-file":
        return PyFileSystem(path)
    if fstype == "py-memory":
        return PyMemorySystem(path)