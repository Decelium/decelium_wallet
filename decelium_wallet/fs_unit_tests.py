#from PyFileSystem import PyFileSystem
#from PyMemorySystem import PyMemorySystem

from data import get_fs

def run_tests(fs):
    print(f"\nRunning tests on {fs.__class__.__name__}")

    print("\nCreating and writing to 'test.txt'")
    with fs.open("test.txt", 'w') as f:
        f.write("Hello, World!")
    print("'test.txt' created and written to.")

    print("\nReading 'test.txt'")
    with fs.open("test.txt", 'r') as f:
        print(f"Contents of 'test.txt': {f.read()}")

    print("\nCreating and writing to 'inner/test.txt'")
    with fs.open("inner/test.txt", 'w') as f:
        f.write("Hello, World!")
    print("'inner/test.txt' created and written to.")

    print("\nReading 'inner/test.txt'")
    with fs.open("inner/test.txt", 'r') as f:
        print(f"Contents of 'inner/test.txt': {f.read()}")

    print("\nDeleting 'inner/test.txt'")
    fs.file("inner/test.txt").delete()
    print("'inner/test.txt' deleted.")

    print("\nChecking if 'inner/test.txt' exists")
    print(f"'inner/test.txt' exists: {fs.file('inner/test.txt').exists()}")

    print("\nAppending to 'test.txt'")
    with fs.open("test.txt", 'a') as f:
        f.write(" Append successful!")
    print("'test.txt' appended to.")

    print("\nReading 'test.txt'")
    with fs.open("test.txt", 'r') as f:
        print(f"Contents of 'test.txt': {f.read()}")

    print("\nDeleting 'test.txt'")
    fs.file("test.txt").delete()
    print("'test.txt' deleted.")

    print("\nChecking if 'test.txt' exists")
    print(f"'test.txt' exists: {fs.file('test.txt').exists()}")

#fs1 = PyFileSystem("test_folder/")
#fs2 = PyMemorySystem("test_folder/")
fs1 = get_fs('py-file',"test_folder/")
fs2 = get_fs('py-memory',"test_folder/")
run_tests(fs1)
run_tests(fs2)
