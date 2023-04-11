import json
import subprocess
import traceback
from pathlib import Path

def run_test(test_dir, test_command):
    try:
        output = subprocess.check_output(
            test_command,
            shell=True,
            cwd=test_dir,
            stderr=subprocess.STDOUT,
            text=True
        )
        return {"result": True, "output": output}
    except subprocess.CalledProcessError as e:
        return {"result": False, "output": e.output}

def main():
    tests = [
        {
            "name": "js",
            "directory": "js",
            "command": "python3 test_js.py",
        },
        {
            "name": "nodejs",
            "directory": "nodejs",
            "command": "node test_nodejs.js",
        },
        {
            "name": "reactjs",
            "directory": "reactjs",
            "command": "nodejs test_reactjs.js",
        },
        {
            "name": "cli",
            "directory": "cli",
            "command": "python3 test_cli.py",
        },
        {
            "name": "python",
            "directory": "python",
            "command": "python3 test_python.py",
        },
    ]

    results = []
    
    for test in tests:
        try:
            print(f"testing {test['name']}")
            print("*****")
            result = run_test(test['directory'], test['command'])
            results.append({"name": test["name"], **result})
        except Exception as e:
            traceback.print_exc()
            results.append({"name": test["name"], "result": False, "output": str(e)})
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
