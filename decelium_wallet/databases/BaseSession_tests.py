import io, os
import unittest
from decelium_wallet.databases.BaseSession import MemorySession, DataSession
import json
class SessionTests(unittest.TestCase):

    def setUp(self):
        # Define a default root for DataSession and a method to validate storage
        default_root = "./test_root"
        self.sessions = {
            'MemorySession': MemorySession(in_dict={'root': default_root}),
            #'DataSession': DataSession(in_dict={'root': default_root})
        }

    def validate_storage(self, session, expected_filename, expected_payload):

        if isinstance(session, MemorySession):
            storage = session[session.f_storage]

            if expected_filename not in storage:
                raise FileNotFoundError(f"File {expected_filename} not found in storage.")
            if not isinstance(expected_filename, str):
                raise TypeError(f"Invalid key type: {expected_filename} is not a string.")
            data = storage[expected_filename]
            if not isinstance(data, str):
                raise TypeError(f"Invalid value type for key {expected_filename}: Not an str instance in MemorySession.")
            assert data == expected_payload

        elif isinstance(session, DataSession):
            path = os.path.join(session[session.f_root], expected_filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"File {expected_filename} not found at path {path}.")
            with open(path, 'r') as file:
                data = file.read()
            if not isinstance(data, str):
                raise TypeError(f"Invalid value read from file {expected_filename}: Not an str instance.")
            #print(data)
            #print(path)
            assert data == expected_payload

        return True

    def test_basic_file_operations(self):
        for session_name, session in self.sessions.items():
            with self.subTest(session=session_name):
                # Write a file
                with session.open("testfile.txt", "wb") as f:
                    f.write(b"Hello, world!")

                # Check that the file exists
                self.assertTrue(session.exists("testfile.txt"))
                print(json.dumps(session,indent=2))
                ## Read the file
                with session.open("testfile.txt", "rb") as f:
                    contents = f.read()
                self.assertEqual(contents, b"Hello, world!")

                # Validate internal storage
                self.assertTrue(self.validate_storage(session,"testfile.txt","Hello, world!"))

                # Delete the file
                session.delete("testfile.txt")
                self.assertFalse(session.exists("testfile.txt"))
    
    def test_list_dir(self):
            expected_structure = {
                './': ['first_file.txt','inner'],
                './inner': ['inner2', 'inner2peer', 'second_file.txt'],
                './inner/inner2': ['third_file.txt'],
                './inner/inner2peer': ['fourth_file.txt']
            }

            for session_name, session in self.sessions.items():
                with self.subTest(session=session_name):
                    # Create required directory structure and files
                    file_content_pairs = {
                        "first_file.txt": b"Hello, world!",
                        "inner/second_file.txt": b"Second file.",
                        "inner/inner2/third_file.txt": b"Third file.",
                        "inner/inner2peer/fourth_file.txt": b"Fourth file."
                    }

                    for file_path, content in file_content_pairs.items():
                        with session.open(file_path, "wb") as file:
                            file.write(content)

                    # Validate directory content
                    for directory, expected_files in expected_structure.items():
                        print(expected_files)
                        actual_files = sorted(session.listdir(directory))
                        self.assertEqual(
                            actual_files, 
                            sorted(expected_files),
                            msg=f"Mismatch in directory '{directory}': expected {sorted(expected_files)}, got {actual_files}"
                        )

                    # Cleanup files and directories
                    session.delete("first_file.txt")
                    session.delete("inner/second_file.txt")
                    session.delete("inner/inner2/third_file.txt")
                    session.delete("inner/inner2peer/fourth_file.txt")
            
    def tearDown(self):
        pass
        # Cleanup session storage if necessary
        #for session in self.sessions.values():
        #    if session.exists("testfile.txt"):
        #        session.delete("testfile.txt")

if __name__ == "__main__":
    unittest.main()
    #unittest.main(defaultTest='SessionTests.test_list_dir')