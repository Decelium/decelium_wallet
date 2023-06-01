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
        pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
        pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
        return pq, user['api_key'], dw

    def run(self,args):
        #print("Check balance args ",args)
        wallet_path = args[0]
        target_user = args[1]
        url_version = args[2]
        password = crypto.getpass(wallet_path)

        [pq,api_key,wallet] = self.load_pq(wallet_path,password,url_version,target_user)

        #print(api_key)

        cpu_contract_id = "obj-e46fff82-e1a5-4a0b-b4e2-32dece7f3270"
        cpu_symbol = "CPU"

        mbalance  = pq.balance({'api_key':api_key ,'self_id':api_key,'symbol':cpu_symbol ,'contract_id':cpu_contract_id},remote=True)
        #print(mbalance)
        return mbalance
    
def run(*args):
    c = Command()
    return c.run (args)