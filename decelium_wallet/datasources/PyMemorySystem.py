import os
'''
class PyMemoryFile:
    def __init__(self, path, fs):
        self.path = path
        self.fs = fs
        self.mode = 'r'  # Default mode

    def open(self, mode='r'):
        self.mode = mode
        if self.mode not in ['r', 'w']:
            raise ValueError(f"Unsupported mode: {self.mode}")
        return self

    def close(self):
        pass  # No action necessary for in-memory file system

    def read(self):
        if 'r' not in self.mode:
            raise IOError("File not open for reading")
        data_dict = self.fs.get_data(self.path)
        if data_dict:
            return data_dict['data']
        else:
            raise IOError(f"No such file: {self.path}")

    def write(self, data):
        if 'w' not in self.mode:
            raise IOError("File not open for writing")
        self.fs.set_data(self.path, data)

    def delete(self):
        self.fs.delete(self.path)

    def exists(self):
        return self.fs.exists(self.path)

    def __enter__(self):
        return self.open(self.mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''
class PyMemory:
    def __init__(self, path, fs):
        self.path = path
        self.fs = fs
        self.mode = 'r'  # Default mode

    def open(self, mode='r'):
        self.mode = mode
        if self.mode not in ['r', 'w', 'a']:
            raise ValueError(f"Unsupported mode: {self.mode}")
        return self

    def close(self):
        pass  # No action necessary for in-memory file system

    def read(self):
        if 'r' not in self.mode:
            raise IOError("File not open for reading")
        data_dict = self.fs.get_data(self.path)
        if data_dict:
            return data_dict['data']
        else:
            raise IOError(f"No such file: {self.path}")

    def write(self, data):
        if 'w' not in self.mode and 'a' not in self.mode:
            raise IOError("File not open for writing")
        if self.mode == 'w':
            self.fs.set_data(self.path, data)
        elif self.mode == 'a':
            existing_data = self.fs.get_data(self.path)
            if existing_data is not None:
                self.fs.set_data(self.path, existing_data['data'] + data)
            else:
                self.fs.set_data(self.path, data)

    def delete(self):
        self.fs.delete(self.path)

    def exists(self):
        return self.fs.exists(self.path)

    def __enter__(self):
        return self.open(self.mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



import os

class PyMemorySystem:
    all_paths = {}  # Shared among all instances

    def __init__(self, root):
        self.root = os.path.normpath(root)

    def file(self, path):
        return PyMemory(os.path.join(self.root, path), self)

    def open(self, path, mode='r'):
        return self.file(path).open(mode)

    def exists(self, path):
        return self.get_data(os.path.join(self.root, path)) is not None

    def delete(self, path):
        self.delete_data(os.path.join(self.root, path))

    def get_data(self, path):
        path_list = os.path.normpath(path).split(os.sep)
        d = self.all_paths
        for key in path_list:
            if key in d:
                d = d[key]
            else:
                return None  # path does not exist
        return d.get('data', None)

    def delete_data(self, path):
        path_list = os.path.normpath(path).split(os.sep)
        d = self.all_paths
        for key in path_list[:-1]:
            if key in d:
                d = d[key]
            else:
                return  # path does not exist
        if path_list[-1] in d:
            del d[path_list[-1]]

    def set_data(self, path, data):
        path_list = os.path.normpath(path).split(os.sep)
        d = self.all_paths
        for key in path_list[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        if 'data' not in d:
            d[path_list[-1]] = {'data': {}}
        d[path_list[-1]]['data'] = {'attr': {}, 'data': data}

        
        
    
        
if __name__ == "__main__":
    root = "test_folder/inner"
    fs = PyMemorySystem(root)

    file_path = "test.txt"

    if not fs.exists(file_path):
        with fs.open(file_path, 'w') as f:
            f.write("Hello, World!")
            print(f"'{file_path}' created and written to.")

    with fs.open(file_path, 'r') as f:
        contents = f.read()
        print(f"Contents of '{file_path}': {contents}")

    # Create a new file system object with root = "test_folder"
    root = "test_folder"
    fs2 = PyMemorySystem(root)

    # Read "./inner/test.txt"
    file_path = "inner/test.txt"
    with fs2.open(file_path, 'r') as f:
        contents = f.read()
        print(f"Contents of '{file_path}': {contents}")

    # Delete "inner/test.txt" at the end
    fs2.delete(file_path)
    print(f"Deleted '{file_path}'.")

    if not fs2.exists(file_path):
        print(f"'{file_path}' no longer exists.")

    # Test creating and reading files in separate file systems
    fs1 = PyMemorySystem("/test_folder/inner/")
    fs2 = PyMemorySystem("/test_folder/")

    # create and write a file in fs1
    with fs1.open("test1.txt", 'w') as f:
        f.write("Hello, World!")

    # check if file exists and read content in fs1
    assert fs1.exists("test1.txt")
    with fs1.open("test1.txt", 'r') as f:
        assert f.read() == "Hello, World!"

    # check if file exists and read content in fs2
    assert fs2.exists("inner/test1.txt")
    with fs2.open("inner/test1.txt", 'r') as f:
        assert f.read() == "Hello, World!"

    # create and write a file in fs2
    with fs2.open("test2.txt", 'w') as f:
        f.write("Another file.")

    # check if file exists and read content in fs2
    assert fs2.exists("test2.txt")
    with fs2.open("test2.txt", 'r') as f:
        assert f.read() == "Another file."

    # check if file doesn't exist in fs1
    assert not fs1.exists("test2.txt")

    # append to file in fs1
    with fs1.open("test1.txt", 'a') as f:
        f.write(" More content.")

    # check if appended content is there in fs1
    with fs1.open("test1.txt", 'r') as f:
        assert f.read() == "Hello, World! More content."

    # check if appended content is there in fs2
    with fs2.open("inner/test1.txt", 'r') as f:
        assert f.read() == "Hello, World! More content."

    # delete file in fs1
    fs1.delete("test1.txt")

    # check if file is deleted in fs1
    assert not fs1.exists("test1.txt")

    # check if file is deleted in fs2
    assert not fs2.exists("inner/test1.txt")

    print("All tests passed.")