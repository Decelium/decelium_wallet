> Experimental: This code will change in the future, including function names. Please keep up to date with the repository!
# Decelium Protocol
### Decentralizing web hosting and containers

The decentralization community needs tools to host websites, run multiplayer games and stream video. The Decelium protocol allows people to host websites and run Docker containers with few limitations. We are technology-decentralized from day one, and you too can apply to host a community miner! We have plans to become legally decentralized after a series of stable releases, until then the project is run by volunteers.

Every modern computer has four properties: Network, Memory, Processing, and a Secure Storage. BTC, ETH, and most protocols act primarly as secure storage with additional features gatekeeping, which is a critical need. However, being a ledger first is a not sutible strategy for real-time networking or streaming solutions, which do not need every edit to live on a ledger, and instead need real-time performance. The Decelium SDK allows any Decelium address holder to upload real-time applications to the Network, that can provide a variety of global services, from streaming video to running a multiplayer game. 

# Decelium Wallet
### Protecting an individuals identiy, rights, and data, while they use the network.

The Decelium Wallet repository bundles two features together; a user wallet to allow users self-custody over their resources (websites, processes, jobs). Second, a Protocol client for connecting to the network and running commands. These tools are in an experimental stage, and we will be crafting our own underlying libraries.

1. A User Wallet - wallet.py
    1. Self Custody: Local User Key Management
    2. Mini Database: Local Secrets Management
    3. Authorization: Local Message Signing
    4. Privacy: Local Cypher Support
2. A Decelium Protocol Client -decelium.py
    1. Create a Website
    2. Create a User
    2. Sign a Request
    3. See Examples repository for more information

If you are interested in creating systems on the Decelium Network, please visit decelium.com. You will find an Examples repository which will link many real life examples of systems hosted on the Decelium Nework. If you would like to contribute, please visit decelium.com and get in touch.


# Getting Started
### Install

Clone the wallet to get started. 
> git clone https://github.com/Decelium/decelium_wallet

Install any dependencies locally
> pip install -r requirements.txt

### Create a wallet (Local)
```
    #Create
    path = './test-'+str(uuid.uuid4())+'.wallet.dec'
    dw = decelium.SimpleWallet()
    dw.load(path)
    user = dw.create_account()
    dw.save(path,"Test_a_strong_password_here")
    
    # Load
    dw = decelium.SimpleWallet()
    dw.load(path,"Test_a_strong_password_here")
    print(dw.get_raw())
    
    # Create Network Connection to the Testnet
    url_version = 'test.paxfinancial.ai'   
    pq_raw = decelium.Decelium(url_version=url_version,api_key=user['api_key'])
    pq = decelium.SimpleCryptoRequester(pq_raw,{user['api_key']:user})
``` 
> Note: It would be hard to crack your wallet, but it is absolutely possible for a trained professional to brute force your wallet.
> Save it somewhere secure. We will be releasing a full air-gapped cold wallet solution as soon as possible, 
> and if you are a volunteer interested in this part of the project get in touch!

### IPFS Based Website
```
    website = '''<!DOCTYPE html><html><body><h1>Generic Heading</h1></p></body></html>'''
    # Push file online
    res_obj =pq.create_entity({'api_key':user['api_key'],  
                                'path':'/html_files/', 
                                'name':'index.html',
                                'file_type':'ipfs', 
                                'payload':website,},remote=True)

    # Visit 'http://dev.paxfinancial.ai/obj/'+res_obj to see the website!
    cid_information =pq.download_entity({'api_key':user['api_key'],  
                                         'path':'index.html',
                                         'attrib':True})
    data =pq.download_entity({'api_key':user['api_key'],  
                                         'path':'index.html'})
``` 

### Custom Domain Name
``` 
    # Register a domain (you must own the DNS and will get instructions from this method)
    res_url =pq.create_entity({'api_key':user['api_key'],
                                    'path':'/apps/'+app_dir+'/domains/',
                                    'name':"my_test_domain.com",
                                    'file_type':'host',
                                    'attrib':{'host':my_test_domain.com,
                                                'secret_password':"CHOOSE_A_PASSWORD_HERE",
                                                'target_id':res_obj}
                                },remote=True)
```
### Final Notes
1. The Decelium Network hosts have over 192 avaliable functions!
2. Over the coming months, we are working on documentation.
3. The best place to begin is the ./tests/ folder.
4. This is a new repository and still in progress
5. Get in touch!
