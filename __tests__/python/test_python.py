import uuid
import requests
import sys
import traceback
import subprocess
import os
import json
import sys
import importlib
sys.path.append('../')
sys.path.append('../../')
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

def run_decw_cmd(command, *args):
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

def check_wallet_exists(wallet_path):
    return os.path.isfile(wallet_path)

def check_wallet_balance(wallet_path, user_name, url_version):
    balance = run_command("check_balance", wallet_path, user_name, url_version)
    return balance

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

def get_wallet_info():
    wallet_info = json.loads(run_command("discover_wallets"))
    if wallet_info:
        for info in wallet_info:
            #print(wallet_info)
            if info['wallet'] and 'test_wallet.dec' in info['wallet']:
                return info['wallet'], info['passfile']
    return None, None    
    
    
try:
    original_stdout, original_stderr = capture_output()
    
    wallet_path, password_file = get_wallet_info()
    
    if wallet_path is None or password_file is None:
        wallet_path = "./test_wallet.dec"
        password_file = "./test_wallet.dec.password"
    
    if not check_wallet_exists(wallet_path):
        subprocess.run(f"rm {wallet_path}", shell=True, capture_output=True)
        with open(password_file,'w')as f:
            f.write("unittestpass")
        wallet = run_command("generate_a_wallet", wallet_path)
        assert len(json.loads(wallet)) == 0 and len(wallet) > 0
    #sys.exit(0)
    print("have wallet file,",wallet_path)
    wallet = run_command("generate_user", wallet_path, "test_user", "confirm")
    assert "test_user" in wallet

    test_username = "test_user"+str(uuid.uuid4())
    user_id = run_command("create_user", wallet_path, "test_user", test_username, "test.paxfinancial.ai", "passtest")

    try:
        assert "obj-" in user_id
    except Exception as e:
        print( "user_id error", user_id)
        raise(e)

    balance = check_wallet_balance(wallet_path, "test_user", "test.paxfinancial.ai")
    if balance < 10:
        fund_result = run_command("fund", wallet_path, "test_user", "test.paxfinancial.ai")
        assert fund_result and not 'error' in  fund_result

    balance = run_command("check_balance", wallet_path, "test_user", "test.paxfinancial.ai")
    assert balance > 10    

    website_data = run_command("deploy", wallet_path, "test_user", "test.paxfinancial.ai", "test/example_small_website.ipfs", "./website/")
    website_data = json.loads(website_data)
    url = "https://test.paxfinancial.ai/obj/"+website_data["app_id"]+"/"
    assert "obj-" in website_data["app_id"]
    response = requests.get(url)
    assert response.status_code == 200
    assert '<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>' in response.text
        
    del_result = run_command("delete_user", wallet_path, "test_user", test_username, "test.paxfinancial.ai")
    assert json.loads(del_result) == True
    
    #subprocess.run(f"rm {password_file}", shell=True, capture_output=True)
    #subprocess.run(f"rm {wallet_path}", shell=True, capture_output=True)
    subprocess.run("rm -rf website", shell=True, capture_output=True)
    
    restore_output(original_stdout, original_stderr)
    print("1")
    sys.exit(0)

except Exception as e:
    restore_output(original_stdout, original_stderr)
    traceback.print_exc()
    sys.exit(1)
