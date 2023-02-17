import sys
sys.path.append("../../")
from decelium_wallet.crypto import crypto
from decelium_wallet import decelium

def load_pq(path,password,url_version,target_user):
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

def run(*args):

    wallet_path = args[0]
    target_user = args[1]
    url_version = args[2]
    password = crypto.getpass()
    
    [pq,api_key,wallet] = load_pq(wallet_path,password,url_version,target_user)
    
    print(api_key)
    
    cpu_contract_id = "obj-e46fff82-e1a5-4a0b-b4e2-32dece7f3270"
    cpu_symbol = "CPU"

    mbalance  = pq.balance({'api_key':api_key ,'self_id':api_key,'symbol':cpu_symbol ,'contract_id':cpu_contract_id},remote=True)
    print(mbalance)   
    
    
if __name__ == "__main__":

    run(*sys.argv[1:])