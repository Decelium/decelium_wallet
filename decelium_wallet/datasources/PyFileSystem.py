import os
import shutil
'''
class PyFile:
    def __init__(self, path):
        self.path = path

    def open(self, mode='r'):
        self.file = open(self.path, mode)
        return self

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def read(self):
        return self.file.read()

    def write(self, data):
        self.file.write(data)

    def delete(self):
        if self.exists():
            os.remove(self.path)

    def exists(self):
        return os.path.isfile(self.path)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
'''
class PyFile:
    def __init__(self, path):
        self.path = path
        self.mode = 'r'  # Default mode
        self.file = None

    def open(self, mode='r'):
        self.mode = mode
        if mode in ['w', 'a']:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)  # Ensure directory exists
        
        self.file = open(self.path, mode)
        return self

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def read(self):
        return self.file.read()

    def write(self, data):
        self.file.write(data)

    def delete(self):
        if self.exists():
            os.remove(self.path)

    def exists(self):
        return os.path.isfile(self.path)

    def __enter__(self):
        return self.open(self.mode)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



class PyFileSystem:
    def __init__(self, root):
        self.root = root
        if not os.path.exists(root):
            os.makedirs(root)

    def file(self, path):
        full_path = os.path.join(self.root, path)
        return PyFile(full_path)

    def open(self, path, mode='r'):
        return self.file(path).open(mode)

    def exists(self, path):
        full_path = os.path.join(self.root, path)
        return os.path.exists(full_path)

    def delete(self, path):
        full_path = os.path.join(self.root, path)
        if self.exists(full_path):
            if os.path.isfile(full_path):
                os.remove(full_path)
            else:
                shutil.rmtree(full_path)
                

if __name__ == "__main__":
    root = "test_folder"
    fs = PyFileSystem(root)

    file_path = "test.txt"

    #if not fs.exists(file_path):
    with fs.open(file_path, 'w') as f:
        f.write("Hello, World!")
        print(f"'{file_path}' created and written to.")

    with fs.open(file_path, 'r') as f:
        contents = f.read()
        print(f"Contents of '{file_path}': {contents}")

    fs.delete(file_path)
    print(f"Deleted '{file_path}'.")

    if not fs.exists(file_path):
        print(f"'{file_path}' no longer exists.")