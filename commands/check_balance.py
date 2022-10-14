import sys
sys.path.append("../../")
from decelium.crypto import crypto
from decelium import decelium

def _load_pq(path,password,url_version,target_user):
    dw = decelium.SimpleWallet()
    dw.load(path,password)
    accts = dw.list_accounts()

    #print(accts)
    #print(dw.get_user('admin'))

    assert target_user in accts
    user = dw.get_user(target_user)
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
    return pq, user['api_key'], dw

def main():

    wallet_path = sys.argv[1]
    password = crypto.getpass()
    
    [pq,api_key,wallet] = _load_pq(wallet_path,password,sys.argv[3],sys.argv[2])
    
    print(api_key)
    
    cpu_contract_id = "obj-e46fff82-e1a5-4a0b-b4e2-32dece7f3270"
    cpu_symbol = "CPU"

    mbalance  = pq.balance({'api_key':api_key ,'self_id':api_key,'symbol':cpu_symbol ,'contract_id':cpu_contract_id},remote=True)
    print(mbalance)   
    
    
if __name__ == "__main__":

    main()