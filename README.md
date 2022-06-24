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
### Get up and running on the network right away

Clone the wallet to get started. 
> git clone https://github.com/Decelium/decelium_wallet

Install any dependencies locally
> pip install -r requirements.txt

In a python file, import key libraries:
> import decelium.decelium as decelium
> import decelium.crypto as crypto
> 
> 

Create your first wallet:
> 
> 
> 

Create a website:
> 
> 
> 

Create second user:
>
>
>

Transfer website to user:
>
>
>



