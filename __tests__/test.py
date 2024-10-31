## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent 

import subprocess

class SystemTests():
    def __init(self):
        pass
    
    def run_simple_py(self):
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
    
    def run_simple_cli(self):
        try:
            cmd = ['python3','./python/test_python.py','decw','dev.paxfinancial.ai']
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
    
    def run_py_network_alone(self):
        try:
            cmd = ['python3','./python/worker_http.py','1','dev.paxfinancial.ai',"\"[]\""]
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

    def run_js_network_alone(self):
        try:
            cmd = ['node','./nodejs/worker_http.js','3','dev.paxfinancial.ai',"\"[]\""]
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

    def run_py_network_together(self):
        num_jobs = 2
        try:
            # List to store all the subprocesses
            processes = []

            # Create a job for each number from 1 to num_jobs
            for i in range(1, num_jobs + 1):
                # Create list of other jobs
                other_jobs = list(range(1, num_jobs + 1))
                other_jobs.remove(i)
                py_job = ['python3', './python/worker_http.py']
                js_job = ['node', './nodejs/worker_http.js']
                
                cmd = ['python3', './python/worker_http.py', str(i), 'dev.paxfinancial.ai', "\""+str(other_jobs)+"\""]

                # Start the subprocess
                print(' '.join(cmd), end="...")
                proc = subprocess.Popen(cmd, cwd='./', stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

                # Add the subprocess to our list
                processes.append(proc)

            # Wait for all subprocesses to complete and collect their output
            output = ""
            success = True
            for i, process in enumerate(processes):
                out, _ = process.communicate()
                output += out.decode("utf-8") + "\n"  # Add each output to the cumulative output string
                if process.returncode != 0:
                    success = False  # A job failed

            return {"result": success, "output": output}  # All jobs completed, success is True only if all jobs were successful
        except Exception as e:
            return {"result": False, "output": output + "\nException: " + str(e)}

    def run_pyjs_network_together(self):
        num_jobs = 2
        try:
            # List to store all the subprocesses
            processes = []

            # Create a job for each number from 1 to num_jobs
            for i in range(1, num_jobs + 1):
                # Create list of other jobs
                other_jobs = list(range(1, num_jobs + 1))
                other_jobs.remove(i)                
                cmd = ['python3', './python/worker_http.py', str(i), 'dev.paxfinancial.ai', "\""+str(other_jobs)+"\""]
                print(' '.join(cmd), end="...")
                proc = subprocess.Popen(cmd, cwd='./', stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                processes.append(proc)
            
            cmd = ['node', './nodejs/worker_http.js', str(i+3), 'dev.paxfinancial.ai', "\""+str( list(range(1, num_jobs + 1)))+"\""]
            print(' '.join(cmd), end="...")
            proc = subprocess.Popen(cmd, cwd='./', stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            processes.append(proc)

            # Wait for all subprocesses to complete and collect their output
            output = ""
            success = True
            for i, process in enumerate(processes):
                out, _ = process.communicate()
                output += out.decode("utf-8") + "\n"  # Add each output to the cumulative output string
                if process.returncode != 0:
                    success = False  # A job failed

            return {"result": success, "output": output}  # All jobs completed, success is True only if all jobs were successful
        except Exception as e:
            return {"result": False, "output": output + "\nException: " + str(e)}
        
        
# node ./nodejs/worker_http.js 3 dev.paxfinancial.ai "[1,2]"

if __name__=="__main__":
    st = SystemTests()
    meths = [st.run_simple_py,
             st.run_simple_cli,
             st.run_py_network_alone,
             st.run_js_network_alone,
             st.run_py_network_together,
             st.run_pyjs_network_together]
    for m in meths:
        res = m()
        if res["result"]==True:
            print(" success")
        else:
            print(" FAILED")
            print(res['output'])
    #print(st.run_simple())
    #print(st.run_py_network())