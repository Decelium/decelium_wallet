#contract=CreateUser
#version=0.1

import sys,json
sys.path.append("../../")
sys.path.append("../../../")
try:
    from decelium_wallet.crypto import crypto
except:
    from crypto import crypto
try:     
    from decelium_wallet import decelium
except:
    import decelium


class CreateUser: 
    def load_pq(self,path,password,url_version,target_user):
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

    def run(self,args):
        #return "TEST RETURN"
        wallet_path = args[0]
        password = decelium.getpass(wallet_path)
        wallet_user = args[1]
        dec_username = args[2]
        url_version = args[3]
        online_password = args[4]

        [pq,api_key,wallet] = self.load_pq(wallet_path,password,url_version,wallet_user)

        #print(api_key)

        #dw = decelium.SimpleWallet()
        #dw.load(path=wallet_path,password=password)
        wallet_contents = wallet.get_raw()

        access_keys = wallet_contents[wallet_user]['user'].copy()
        access_keys['private_key'] = "destroy it"


        if len(password) == 0:
            return json.dumps({"error":"empty password"})
        feature = {'username': dec_username,
                   'api_key': api_key,
                   'access_key':access_keys,
                   'password': online_password,
                   'password2': online_password,}
        result = pq.delete_entity({'api_key':api_key,'path':'system_users','name':dec_username,},remote=True)   
        obj_id = pq.user_register(feature,remote=True)
        #print(obj_id) 
        return json.dumps(obj_id)
    
def run(*args):
    c = CreateUser()
    return c.run (args)