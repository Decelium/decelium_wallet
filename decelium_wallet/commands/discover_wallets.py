#contract=Command
#version=0.1

import sys, json
sys.path.append("../../")
from decelium_wallet.wallet import wallet

class Command:    
    def run(self, args):
        root = args[0] if len(args) > 0 else "./"
        password = args[1] if len(args) > 1 else None
        discovered_wallets = wallet.discover(root, password)
        return json.dumps(discovered_wallets)
    
def run(*args):
    c = Command()
    return c.run (args)
