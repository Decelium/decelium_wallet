import sys
sys.path.append("../../")
sys.path.append("../../../")
from decelium.crypto import crypto
from decelium import decelium

def load_pq(path,password,url_version,target_user):
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
    
    [pq,api_key,wallet] = load_pq(wallet_path,password,sys.argv[4],sys.argv[2])
    
    print(api_key)
        
    result = pq.delete_entity({'api_key':api_key,'path':'system_users','name':sys.argv[3],},remote=True)
    print(result)
    
if __name__ == "__main__":

    main()