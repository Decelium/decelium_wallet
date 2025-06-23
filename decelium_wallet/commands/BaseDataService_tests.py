# test_base_data_service.py

import os
import sys
import unittest
import subprocess
import json
from decelium_wallet.commands.BaseData import BaseData
from BaseDataService import BaseDataService  # adjust import as needed

class HelloWorld(BaseData):
    message: str
    def SayHello(self, added_message: str, inner: dict) -> str:
        return self.message + added_message + inner["second_added"]

class TestBaseDataService(unittest.TestCase):

    def test_invoke_hello_world(self):
        # Path to this test file (contains HelloWorld & CLI entrypoint)
        file_path = os.path.abspath(__file__)
        service_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "BaseDataService.py")
        )
        # 1) Direct Python invocation of static_invoke
        result_json = BaseDataService.static_invoke(
            class_path=file_path,
            cwd="",
            class_name="HelloWorld",
            class_data=json.dumps({"message": "Hello"}),
            method_name="SayHello",
            method_args=json.dumps({
                "added_message": " world",
                "inner": {"second_added": "!"}
            })
        )
        result = json.loads(result_json)
        self.assertEqual(result["result"], "Hello world!")
        
        
        print ("\n\n\n\n-------\n")

    def test_invoke_hello_world_cli(self):
        file_path = os.path.abspath(__file__)
        service_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "BaseDataService.py")
        )

        cmd = [
            "python3",
            service_path,
            "invoke",
            "class_path='"+file_path+"'",
            "cwd=''", 
            "class_name=HelloWorld",
            "class_data.message=Hello",
            "method_name=SayHello",
            "method_args.added_message=' world'",
            "method_args.inner.second_added=!"
        ]

        print(" ".join(cmd))
        
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = proc.stdout.strip()
        result2 = json.loads(output)
        self.assertEqual(result2["result"], "Hello world!")

    def test_invoke_hello_world_json(self):
        import shutil, os
        pth = "./test_json_delete_me.json"

        file_path = os.path.abspath(__file__)
        service_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "BaseDataService.py")
        )

        with open(pth,'w') as f:
            invoke_kwargs = {
                "class_path": file_path,
                "cwd": "",
                "class_name": "HelloWorld",
                "class_data": {"message": "Hello"},
                "method_name": "SayHello",
                "method_args": {
                    "added_message": " world",
                    "inner": {"second_added": "!"}
                }
            }
            f.write(json.dumps(invoke_kwargs,indent=3))
        with open(pth,'r') as f:
            assert len (f.read()) > 0, "File should not be empty..."

        cmd = f'python3 {service_path} invoke "[[in_message={pth}]]"'
        print(cmd)
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        print("-----------------------------")
        print(proc.stdout)
        print("-----------------------------")

        print(proc.stderr)
        print("-----------------------------")
        #return
        output = proc.stdout.strip()
        result2 = json.loads(output)
        self.assertEqual(result2["result"], "Hello world!")
        #try:
        print(f"REMOVING {pth}")
        os.remove(pth)
        #except:
        #    pass            

if __name__ == "__main__":
    unittest.main()
    #unittest.main(defaultTest="TestBaseDataService.test_invoke_hello_world_json")
# USAGE EXAMPLES
#  python3 BaseDataService_tests.py

#  Args can be passed in using dot notation
#  python3 /Users/computercomputer/justinops/decelium_wallet/decelium_wallet/commands/BaseDataService.py invoke class_path='/Users/computercomputer/justinops/decelium_wallet/decelium_wallet/commands/BaseDataService_tests.py' cwd='' class_name=HelloWorld class_data.message=Hello method_name=SayHello method_args.added_message=' world' method_args.inner.second_added=!

# Or via a tagged file

####
# python3 /Users/computercomputer/justinops/decelium_wallet/decelium_wallet/commands/BaseDataService.py invoke "[[in_message=./test_json_delete_me.json]]"
