import uuid
import requests
import sys
import traceback
import subprocess
import os
import json
import sys
import importlib

mode = 'python'  # Switch between 'decw' and 'python'
try:
    mode = sys.argv[1]
except IndexError:
    print("Please provide a mode ('decw' or 'python') as an argument when running this script.")
    sys.exit(1)

def run_command(command, *args):
    if mode == 'decw':
        return run_decw_cmd(command, *args)
    elif mode == 'python':
        return run_py_cmd(command, *args)
    else:
        raise Exception(f"Invalid mode: {mode}")
#/app/projects/jgops/projects/portfolio/src/decelium_wallet/__tests__/python/../../decelium_wallet/
def run_decw_cmd(command, *args):
    #cmd = ["decw", command] + list(args)
    cmd = ["python3", "../../decelium_wallet/decw.py", command] + list(args)
    print(' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Command {cmd} failed with error: {result.stderr}")
    try:
        return json.loads(result.stdout)
    except:
        print ("COULD NOT DECODE")
        print(result.stdout)

def run_py_cmd(command, *args):
    command_module_path = f'decelium_wallet.commands.{command}'
    command_module = importlib.import_module(command_module_path)
    return command_module.run(*args)

def capture_output():
    sys.stdout.flush()
    sys.stderr.flush()

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    return original_stdout, original_stderr

def restore_output(original_stdout, original_stderr):
    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdout = original_stdout
    sys.stderr = original_stderr

try:
    original_stdout, original_stderr = capture_output()
    
    subprocess.run("rm .password", shell=True, capture_output=True)
    subprocess.run("rm test_wallet.dec", shell=True, capture_output=True)
    subprocess.run("rm -rf website", shell=True, capture_output=True)
    subprocess.run("mkdir website", shell=True, capture_output=True)
    
    with open("website/index.html", "w") as f:
        f.write(
'''<!DOCTYPE html>
<html>
<body>

<p>This text is normal.</p>

<p><em>This text is emphasized.</em></p>

</body>
</html>                
''')
    
    sys.path.append("../../")
    
    with open(".password","w") as f:
        f.write("passtest")
    
    wallet = run_command("generate_a_wallet", "./test_wallet.dec")
    assert len(wallet) == 0
    
    wallet = run_command("generate_user", "./test_wallet.dec", "test_user", "confirm")
    assert "test_user" in wallet
    
    test_username = "test_user"+str(uuid.uuid4())
    user_id = run_command("create_user", "./test_wallet.dec", "test_user", test_username, "test.paxfinancial.ai", "passtest")
    
    try:
        assert "obj-" in user_id
    except Exception as e:
        print( "user_id error", user_id)
        raise(e)
    fund_result = run_command("fund", "./test_wallet.dec", "test_user", "test.paxfinancial.ai")
    #print("fund_result", fund_result)
    assert fund_result and not 'error' in  fund_result
        
    balance = run_command("check_balance", "./test_wallet.dec", "test_user", "test.paxfinancial.ai")
    assert balance == 200    
    
    website_data = run_command("deploy", "./test_wallet.dec", "test_user", "test.paxfinancial.ai", "test/example_small_website.ipfs", "./website/")
    url = "https://test.paxfinancial.ai/obj/"+website_data["app_id"]+"/"
    assert "obj-" in website_data["app_id"]
    response = requests.get(url)
    #print(website_data["app_id"])
    #print(url)
    #print(response)
    assert response.status_code == 200
    assert '<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>' in response.text
        
    del_result = run_command("delete_user", "./test_wallet.dec", "test_user", test_username, "test.paxfinancial.ai")
    assert del_result == True
    
    subprocess.run("rm .password", shell=True, capture_output=True)
    subprocess.run("rm test_wallet.dec", shell=True, capture_output=True)
    subprocess.run("rm -rf website", shell=True, capture_output=True)
    
    restore_output(original_stdout, original_stderr)

    print("1")
    sys.exit(0)   

except Exception as e:
    restore_output(original_stdout, original_stderr)
    traceback.print_exc()
    sys.exit(1)
