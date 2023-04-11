import uuid
import requests
import sys
import pprint
import traceback
import subprocess
import os

def capture_output():
    sys.stdout.flush()
    sys.stderr.flush()

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    #sys.stdout = open("data.out", "w")
    #sys.stderr = sys.stdout

    return original_stdout, original_stderr

def restore_output(original_stdout, original_stderr):
    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdout = original_stdout
    sys.stderr = original_stderr

try:
    original_stdout, original_stderr = capture_output()
    
    cmdStr = "rm .password"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = "rm test_wallet.dec"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = "rm -rf website"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = "mkdir website"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    with open("website/index.html","w") as f:
        f.write(
'''<!DOCTYPE html>
<html>
<body>

<p>This text is normal.</p>

<p><em>This text is emphasized.</em></p>

</body>
</html>                
''')
    
    cmdStr="yes | pip uninstall decelium_wallet"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = 'pip install "git+https://github.com/Decelium/decelium_wallet.git"'
    subprocess.run(cmdStr,shell=True,capture_output=True)
    #sys.path.append("../../")
    
    import decelium_wallet.decelium as Decelium
    import decelium_wallet.wallet as Wallet
    import decelium_wallet.commands.generate_a_wallet as generate_a_wallet
    import decelium_wallet.commands.generate_user as generate_user
    import decelium_wallet.commands.create_user as create_user
    import decelium_wallet.commands.fund as fund
    import decelium_wallet.commands.check_balance as check_balance
    import decelium_wallet.commands.deploy as deploy
    import decelium_wallet.commands.delete_user as delete_user    
        
    with open(".password","w") as f:
        f.write("passtest")
    
    wallet=generate_a_wallet.run("./test_wallet.dec")
    assert len(wallet)==0
    
    
    
    
    
    wallet=generate_user.run("./test_wallet.dec","test_user","confirm")
    assert "test_user" in wallet
    assert "description" in wallet["test_user"]
    assert "image" in wallet["test_user"]
    assert "secrets" in wallet["test_user"]
    assert "title" in wallet["test_user"]
    assert "user" in wallet["test_user"]
    assert "api_key" in wallet["test_user"]["user"]
    assert "private_key" in wallet["test_user"]["user"]
    assert "version" in wallet["test_user"]["user"]
    
    test_username="test_user"+str(uuid.uuid4())
    user_id=create_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai","passtest")
    assert "obj-" in user_id
    
    fund_result=fund.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
    assert fund_result
    
    balance=check_balance.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
    assert balance==200    
    
    # Test Manual Query
    # We load a wallet class, and manually sign a transaction.
    # This is more secure, as it can control signatures on a message by message basis.
    dw = Wallet.wallet()
    dw.load(path="./test_wallet.dec",password="passtest")
    print(dir(dw))
    pq = Decelium.Decelium(url_version="test.paxfinancial.ai",api_key=dw.pubk("test_user"))
    
    
    qUnsigned = {
        'api_key':dw.pubk("test_user"),
        'path':"/",
        'name':"test_dict.json",
        'file_type':'dict',
        'payload':{"test":"val"}}
    qSigned = dw.sign_request(qUnsigned, ["test_user"])    
    assert "__sigs" in qSigned
    fil  = pq.create_entity(qSigned)
    assert "obj-" in fil
    result  = pq.delete_entity(dw.sr({'api_key':dw.pubk("test_user"),
                                      'self_id':fil},
                                      ["test_user"]))
    assert result == True
    

    
    
    website_id = deploy.run("./test_wallet.dec","test_user","test.paxfinancial.ai","test/example_small_website.ipfs","./website/")
    url = "https://test.paxfinancial.ai/obj/"+website_id+"/"
    assert "obj-" in website_id
    response = requests.get(url)
    print(website_id)
    print(url)
    print(response)
    assert response.status_code==200
    assert '<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>' in response.text
        
    del_result=delete_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai")
    assert del_result==True
    
    cmdStr = "rm .password"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = "rm test_wallet.dec"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    cmdStr = "rm -rf website"
    subprocess.run(cmdStr,shell=True,capture_output=True)
    
    restore_output(original_stdout, original_stderr)

    print("1")
    sys.exit(0)   

except Exception as e:
    restore_output(original_stdout, original_stderr)
    traceback.print_exc()
    sys.exit(1)

