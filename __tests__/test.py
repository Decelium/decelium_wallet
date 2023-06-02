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
            cmd = ['python3','./python/test_python.py','python','dev.paxfinancial.ai']
            print(' '.join(cmd ),end="...")
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
            cmd = ['python3','./python/worker_http.py','1','dev.paxfinancial.ai',"\"[2,3]\""]
            print(' '.join(cmd ),end="...")
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
    meths = [st.run_simple,st.run_py_network]
    for m in meths:
        res = m()
        if res["result"]==True:
            print(" success")
        else:
            print(" FAILED")
            print(res['output'])
    #print(st.run_simple())
    #print(st.run_py_network())