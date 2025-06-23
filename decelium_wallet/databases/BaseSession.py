import os, shutil
import io
from decelium_wallet.commands.BaseData import BaseData

class BaseSession(BaseData):
    required_methods = ["exists", "delete", "open", "listdir","isfile","isfolder"]
    f_root = "root"
    def get_keys(self):
        required = {self.f_root: str}
        optional = {}
        return required, optional

    def __init__(self, in_dict, trim=False):
        #self._check_required_methods(in_dict)
        super().__init__(in_dict, trim=trim)

    def _check_required_methods(self,in_dict):
        available_methods = dir(self)
        for method_name in self.required_methods:
            if method_name not in available_methods:
                raise NotImplementedError(
                    f"The method '{method_name}' must be implemented in '{self.__class__.__name__}: {in_dict}"
                )
class MemorySession(BaseSession):
    """
    A simplified in-memory Session class to provide a basic IO interface for testing.
    Stores file contents in an in-memory dictionary.
    """
    f_storage = 'storage'
    f_root = 'root'  # To specify root for specification reasons, though ignored
    class StringStreamWrapper:
        """A wrapper to manage a stream and store its content as a string."""
        
        def __init__(self, storage, path, mode='r'):
            self.storage = storage
            self.path = path
            self.buffer = io.BytesIO() if 'b' in mode else io.StringIO()

        def __enter__(self):
            return self.buffer

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.buffer.seek(0)
            if isinstance(self.buffer, io.BytesIO):
                # Convert bytes to string before storing
                self.storage[self.path] = self.buffer.read().decode()
            else:
                self.storage[self.path] = self.buffer.getvalue()

    def __init__(self, in_dict, trim=False):
        super().__init__(in_dict, trim=trim)
    
    def do_pre_process(self, in_dict):
        if self.f_storage not in in_dict:
            in_dict[self.f_storage] = {}
        return super().do_pre_process(in_dict)
        
    def get_keys(self):
        required = {self.f_root: str,self.f_storage:dict}
        optional = {}
        return required, optional

    def do_validation(self, key, value):
        if key == self.f_storage:
            if  not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
                raise ValueError(f"All keys and values in storage must be strings {value}")
        return value, ""

    def exists(self, path: str) -> bool:
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        return path in self[self.f_storage]

    def delete(self, path: str) -> bool:
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        if path in self[self.f_storage]:
            del self[self.f_storage][path]
            return True
        return False

    def open(self, path: str, mode: str = 'r'):
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        assert isinstance(mode, str) and mode in ['r', 'rb', 'w', 'wb']

        storage = self[self.f_storage]
        if mode in ['r', 'rb']:
            if path not in storage:
                raise FileNotFoundError(f"No such file or directory: '{path}'")

            # Convert stored content to appropriate stream type
            content = storage[path]
            if mode == 'r':
                stream = io.StringIO(content) if isinstance(content, str) else io.StringIO(content.decode())
            else:  # 'rb'
                stream = io.BytesIO(content.encode()) if isinstance(content, str) else io.BytesIO(content)
            return stream

        if mode in ['w', 'wb']:
            return  self.StringStreamWrapper(storage, path, mode)

    def listdir(self, dir_path: str):
        """Lists the contents of the directory at the given path within the in-memory storage."""
        assert isinstance(dir_path, str) and dir_path, "Must supply a non-empty path"
        
        # Normalize the directory path without leading './'
        norm_dir_path = os.path.normpath(dir_path).lstrip('./')
        norm_dir_path.lstrip('/')
        # Ensure the path ends with a slash for accurate directory matching
        if norm_dir_path and not norm_dir_path.endswith('/'):
            norm_dir_path += '/'

        # To collect directory contents
        listed_items = set()
        for key in self[self.f_storage].keys():
            # Normalize each stored path without leading './'
            norm_key = os.path.normpath(key).lstrip('/')

            # Check if the key starts with the directory path
            if norm_key.startswith(norm_dir_path):
                # Extract the portion of the path after the directory prefix
                rest_of_path = norm_key[len(norm_dir_path):]
                # Split on '/', only the first item after the directory prefix is considered
                parts = rest_of_path.split('/', 1)
                if parts[0]:  # Ensure it is non-empty
                    listed_items.add(parts[0])
        
        return list(listed_items)
          
class DataSession(BaseSession):
    """
    A simplified Session class to provide a basic IO interface for testing with the file system.
    Robust -- will not allow out-of-session file ops. (however it can easily be hacked -- not a security barrier)
    """
    f_root = 'root'
    f_verbose = 'verbose'
    f_unlocked = 'unlocked'
    #f_storage = '__storage'
    
    def list_recursively(self): #TODO Refactor this out
        """A generator function to yield files in the directory recursively."""
        session = self
        queue = ["./"]
        while queue:
            current_path = queue.pop()
            print(current_path)
            for filename in session.listdir(current_path):
                full_path = f"{current_path}/{filename}"
                if session.isfile(full_path):
                    yield current_path, filename
                elif session.isfolder(full_path):
                    queue.append(full_path)
    def from_session_path(self, path):
        doc_root = self[DataSession.f_root]
        return os.path.relpath(path, doc_root)

    def to_local_path(self, path):
        doc_root = self[DataSession.f_root]
        return os.path.abspath(os.path.join(doc_root, path))


    def __init__(self, in_dict, trim=False):
        if self.f_verbose not in in_dict:
            in_dict[self.f_verbose] = False
        if self.f_unlocked not in in_dict:
            in_dict[self.f_unlocked] = False

        super().__init__(in_dict, trim=trim)

    def is_contained_path(self, path: str) -> bool:
        if (self[self.f_unlocked] == True):
            return True
        norm = os.path.normpath(path)
        return not norm.startswith('..') and  not norm.startswith('/')

    def get_keys(self):
        required = {self.f_root: str}
        optional = {self.f_unlocked:bool, self.f_verbose:bool}
        return required, optional

    def exists(self, path: str) -> bool:
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        full_path = os.path.join(self[self.f_root], path)
        return os.path.exists(full_path)

    def delete(self, path: str) -> bool:
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        full_path = os.path.join(self[self.f_root], path)
        if os.path.isdir(full_path):
            try:
                os.rmdir(full_path)
            except OSError:
                shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return True

    def open(self, path: str, mode: str = 'r'):
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")

        assert isinstance(path, str) and len(path) > 0
        assert isinstance(mode, str) and mode in ['r', 'rb', 'w', 'wb']
        full_path = os.path.join(self[self.f_root], path)
        if mode in ['w', 'wb']:        
            directory = os.path.dirname(full_path)
            os.makedirs(directory, exist_ok=True)      
        # print(full_path)  
        if ( self[self.f_verbose] == True):
            if mode in ['r', 'rb']:
                print("ds loading ..."+full_path)
            if mode in [ 'w', 'wb']:
                print("ds writing ..."+full_path)
        return open(full_path, mode)

    def listdir(self, path: str):
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")

        """Lists the contents of the directory at the given path."""
        assert isinstance(path, str) and path, "Must supply a non-empty path"
        full_path = os.path.join(self[self.f_root], path)
        #print(f"Attempting to access: {full_path}")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"No such directory: '{path}' in { os.getcwd()}")

        if not os.path.isdir(full_path):
            raise NotADirectoryError(f"Path is not a directory: '{path}'")
        return os.listdir(full_path)

    def isfile(self, path: str) -> bool:
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")

        full_path = os.path.join(self[self.f_root], path)
        return os.path.isfile(full_path)

    def isfolder(self, path: str) -> bool:
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")

        full_path = os.path.join(self[self.f_root], path)
        return os.path.isdir(full_path)
    
    def mkdir(self, path: str, exist_ok: bool = True) -> None:
        if not self.is_contained_path(path):
            raise Exception(f"Not a contained path {path}")

        assert isinstance(path, str) and path, "Must supply a non-empty path"
        full_path = os.path.join(self[self.f_root], path)
        os.makedirs(full_path, exist_ok=exist_ok)

    def get_root(self):
        return self[self.f_root]
'''
TODO -- upgrade to sit on top of fsspec!

    # --- fsspec compatibility layer ---
    protocol = "file"

    def _open(self, path, mode='rb', **kwargs):
        """
        fsspec calls _open; we delegate to our open().
        """
        return self.open(path, mode)

    def ls(self, path, detail=False):
        """
        List files under `path`.  If detail=True, return list of dicts
        with at least name/type/size.
        """
        try:
            entries = self.listdir(path)
        except FileNotFoundError:
            # if it's a file, return [path]
            if self.isfile(path):
                entries = [path]
            else:
                raise
        if detail:
            out = []
            for name in entries:
                # build full logical path
                p = path.rstrip("/") + "/" + name if self.isdir(path) else name
                out.append({
                    "name": p,
                    "type": "directory" if self.isdir(p) else "file",
                    "size": None,  # you could stat(p) here if you want
                })
            return out
        return entries

    def info(self, path):
        """
        Return a single-entry detailed dict for `path`.
        """
        lst = self.ls(path, detail=True)
        if not lst:
            raise FileNotFoundError(path)
        return lst[0]

    # aliases for fsspec
    isdir    = isfolder
    rm_file  = delete
    makedirs = mkdir

    def rmdir(self, path, recursive=False):
        """
        Remove a (possibly non-empty) directory.  
        """
        full = os.path.join(self[self.f_root], path)
        if recursive:
            shutil.rmtree(full)
        else:
            os.rmdir(full)



'''