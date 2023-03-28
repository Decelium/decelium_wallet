import decelium_wallet
import decelium_wallet.commands.generate_a_wallet as generate_a_wallet
import decelium_wallet.commands.generate_user as generate_user
import decelium_wallet.commands.create_user as create_user
import decelium_wallet.commands.fund as fund
import decelium_wallet.commands.check_balance as check_balance
import decelium_wallet.commands.deploy as deploy
import decelium_wallet.commands.delete_user as delete_user
import uuid
import requests
import sys
import pprint
import traceback

try:
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
    
    website_id = deploy.run("./test_wallet.dec","test_user","test.paxfinancial.ai","test/example_small_website.ipfs","./website/")
    url = "https://test.paxfinancial.ai/obj/"+website_id+"/"
    assert "obj-" in website_id
    response = requests.get(url)
    assert response.status_code==200
    assert response.content==b'<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>\n'
    
    del_result=delete_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai")
    assert del_result==True

except Exception as e:
    traceback.print_exc()
    print("Exiting with status 1")
    sys.exit(1)

print("Exiting with status 0")
sys.exit(0)