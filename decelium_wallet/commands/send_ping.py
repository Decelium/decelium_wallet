#contract=Command
#version=0.1

import sys,json
sys.path.append("../../")
try:
    from decelium_wallet.core import core
except:
    import core
class Command:    

    def run(self,args):
        
        self.core = core()
        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]        
        
        #
        # Get Wallet Bytes
        # (wallets = self.core.discover_wallet())
        with open(wallet_path,'r') as f:
            wallet_data = f.read()
        with open(wallet_path+".password",'r') as f:
            wallet_pass = f.read()
        
        #
        # Load Wallets
        success = self.core.load_wallet(data=wallet_data, password=wallet_pass)
        if success == False:
            return {"error":"can't load wallet"}
        
        success = self.core.initial_connect(target_url="https://"+url_version+"/data/query",target_user=target_user) == True        
        if success == False:
            return {"error":"can't connect to node"}
        
        #
        # Generate Ping
        #def do_echo(args,settings):
        #    return args

        port = 1337
        name = "node-session-file-"+str(target_user)+".node"
        q =self.core.gen_node_ping(port,name,target_user)
        
        #
        # Do Ping
        qSigned = self.core.dw.sign_request(q, [target_user])
        if "error" in qSigned:
            return qSigned
        resp = self.core.net.node_ping(qSigned)
        if "error" in resp:
            resp["error"] = resp["error"] + " with message "+str(qSigned)
            return resp
        try:
            self.core.self_id = resp['self_id']
            return resp
        except:
            return {"error":"gen_node_ping response is invalid: "+ str(resp)}
        
        return json.dumps(resp)
    
def run(*args):
    c = Command()
    return c.run (args)

# python3 ../../decelium_wallet/decelium_wallet/decw.py send_ping ./test_wallet.dec test_user dev.paxfinancial.ai 

# python3 ../../decelium_wallet/decelium_wallet/decw.py check_balance ./test_wallet.dec test_user dev.paxfinancial.ai