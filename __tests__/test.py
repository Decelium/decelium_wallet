# This is the main test driver. It sets up the whole suite, runs tests, and reports results, including how to do a deeper dive.
# Key Tasks
# [X] Unit Test core single user wallet commands
# ---- Look for a wallet
# ---- if wallet exists
# [] Unit Test Py Network Commands (Single-py)
# [] Unit Test Py Network Commands (Single-js)
# [] Unit Test Py Network Commands (Group-hetero)
# [] target the tests at a specific node based on config
# [] Derive or require some 

import subprocess

class SystemTests():
    def __init(self):
        pass
    
    def run_simple(self):
        try:
            cmd = ['python3','./python/test_python.py','python']
            print(' '.join(cmd ))
            output = subprocess.check_output(
                cmd,
                #shell=True,
                cwd='./',
                stderr=subprocess.STDOUT,
                text=True
            )
            return {"result": True, "output": output}
        except subprocess.CalledProcessError as e:
            return {"result": False, "output": e.output}
    
    def run_py_network(self):
        try:
            cmd = ['python3','./python/test_python.py','python']
            print(' '.join(cmd ))
            output = subprocess.check_output(
                cmd,
                #shell=True,
                cwd='./',
                stderr=subprocess.STDOUT,
                text=True
            )
            return {"result": True, "output": output}
        except subprocess.CalledProcessError as e:
            return {"result": False, "output": e.output}
    
if __name__=="__main__":
    st = SystemTests()
    print(st.run_simple())