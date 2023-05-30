import subprocess
import time

workers = [
    ("./python/worker_http.py", "python"),
    ("./python/worker_http.py", "python"),
    #("./python/worker_http.py", "python"),
    #("./python/worker_http.py", "python"),
    #("./python/worker_http.py", "python"),
    #("./python/worker_http.py", "python")
#    ("worker_ws.py", "python"),
#    ("worker_node_http.js", "node"),
#    ("worker_node_ws.js", "node"),
#    ("worker_js_http.js", "node"),
#    ("worker_js_ws.js", "node")
]

processes = []
for i, (worker_file, interpreter) in enumerate(workers):
    worker_id = f"{worker_file}_{i}"
    cmd = [interpreter, worker_file, str(i)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    processes.append(process)
    print(f"Launched {worker_file} with ID: {worker_id}")

# Wait for all processes to finish and collect their output
#outputs = {}
#for i, process in enumerate(processes):
#    worker_id = f"{workers[i][0]}_{i}"
#    output, _ = process.communicate()
#    outputs[worker_id] = output.decode().strip()

# Wait for all processes to finish and collect their output
outputs = {}
for i, process in enumerate(processes):
    worker_id = f"{workers[i][0]}_{i}"
    output, _ = process.communicate()
    outputs[worker_id] = output.decode().strip()

    # Check the return code of the process
    if process.returncode != 0:
        print(f"Error: {worker_id} exited with code {process.returncode}")
        print(f"Sys Output from {worker_id}:")
        print(output)

# Print the output
for worker_id, output in outputs.items():
    print(f"Output from {worker_id}:")
    print(output)
