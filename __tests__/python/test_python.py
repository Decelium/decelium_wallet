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

try:
    generate_a_wallet.run("./test_wallet.dec")
    generate_user.run("./test_wallet.dec","test_user","confirm")
    test_username="test_user"+str(uuid.uuid4())
    create_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai","passtest")
    fund.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
    check_balance.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
    website_id = deploy.run("./test_wallet.dec","test_user","test.paxfinancial.ai","test/example_small_website.ipfs","./website/")
    url = "https://test.paxfinancial.ai/obj/"+website_id+"/"
    response = requests.get(url)
    assert response.status_code==200
    assert response.content==b'<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>\n'
    del_result=delete_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai")
    assert del_result==True
except:
    print("Exiting with status 1")
    sys.exit(1)
print("Exiting with status 0")
sys.exit(0)