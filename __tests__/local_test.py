import json
import subprocess
import traceback
from pathlib import Path
## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent
## TODO - Move / re-write these tests into SecretAgent

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
    except Exception as e:
        return {"result": False, "output": e.output}

def main():
    tests = [
        {
            "name": "cli",
            "directory": "python",
            "command": "python3 test_python.py decw",
        },
        {
            "name": "python",
            "directory": "python",
            "command": "python3 test_python.py python",
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
