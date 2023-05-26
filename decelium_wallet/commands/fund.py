#contract=Command
#version=0.1

import sys
sys.path.append("../../")
try:
    from decelium_wallet.crypto import crypto
except:
    from crypto import crypto
try:
    from decelium_wallet import decelium
except:
    import decelium
class Command:    
    def load_pq(self,path,password,url_version,target_user):
        dw = decelium.SimpleWallet()
        dw.load(path,password)
        accts = dw.list_accounts()

        #print(accts)
        #print(target_user)
        #print(dw.get_user(target_user))

        assert target_user in accts
        user = dw.get_user(target_user)
        pq_raw = decelium.Decelium(self,url_version=url_version,api_key=user['api_key'])
        pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        return pq, user['api_key'], dw

    def run(self,args):

        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]
        password = crypto.getpass()

        [pq,api_key,wallet] = self.load_pq(wallet_path,password,url_version,target_user)

        print(api_key)

        faucet_contract_id = "obj-24f598c9-71a8-4038-88f4-4fedac22acc1"
        cpu_symbol = "CPU"

        response  = pq.execute_entity({'api_key':api_key ,'self_id':faucet_contract_id,'func':'send','args':{'dst_id': api_key}},remote=True)
        print("FUNDING RESPONSE",response)   
        return response
    
def run(*args):
    c = Command()
    return c.run (args)