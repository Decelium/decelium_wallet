> Experimental: This code will change in the future, including function names. Please keep up to date with the repository!
# Decelium Protocol
### Decentralizing web hosting and containers

The decentralization community needs tools to host websites, run multiplayer games and stream video. The Decelium protocol allows people to host websites and run Docker containers with few limitations. We are technology-decentralized from day one, and you too can apply to host a community miner! We have plans to become legally decentralized after a series of stable releases, until then the project is run by volunteers.

Every modern computer has four properties: Network, Memory, Processing, and a Secure Storage. BTC, ETH, and most protocols act primarly as secure storage with additional features gatekeeping, which is a critical need. However, being a ledger first is a not sutible strategy for real-time networking or streaming solutions, which do not need every edit to live on a ledger, and instead need real-time performance. The Decelium SDK allows any Decelium address holder to upload real-time applications to the Network, that can provide a variety of global services, from streaming video to running a multiplayer game. 

# Decelium Wallet
### Protecting an individuals identiy, rights, and data, while they use the network.

The Decelium Wallet repository bundles two features together; a user wallet to allow users self-custody over their resources (websites, processes, jobs). Second, a Protocol client for connecting to the network and running commands. These tools are in an experimental stage, and we will be crafting our own underlying libraries.

1. A User Wallet
    1. Self Custody: Local User Key Management
    2. Mini Database: Local Secrets Management
    3. Authorization: Local Message Signing
    4. Privacy: Local Cypher Support
2. A Decelium Protocol Client
    1. Create a Website
    2. Create a User
    2. Sign a Request
    3. See Examples repository for more information

If you are interested in creating systems on the Decelium Network, please visit decelium.com. You will find an Examples repository which will link many real life examples of systems hosted on the Decelium Nework. If you would like to contribute, please visit decelium.com and get in touch.


# Getting Started
### Install

#### PIP Install

Pip installation installs the [**Decelium wallet**](https://github.com/Decelium/decelium_wallet) as a Python package. This will allow you to use the command-line tool `decw` that lets you create and manage your wallet and deploy websites from the command line. It also allows you to use Decelium wallet modules in your Python programs.

##### Linux

On Linux:

    pip install "git+https://github.com/Decelium/decelium_wallet.git"

##### Windows

On Windows:

<img src="./run_as_administrator.png" alt="How to run as administrator" width="250" height="225">

If you want to use the `decw` command-line tool, you will need to install using Command Prompt as an administrator (see image). Otherwise you will have to [use the Decelium wallet through Python](./PY_USAGE_EXAMPLES.md). 

    pip install "git+https://github.com/Decelium/decelium_wallet.git" 
    

#### NPM Install 

NPM installation of the [**Decelium wallet**](https://github.com/Decelium/decelium_wallet) is necessary if you want to write JavaScript programs or apps that interact with the Decelium server.

The installation command is
    
    npm install https://github.com/Decelium/decelium_wallet


#### Git Clone Install


Clone the wallet to get started. 
> git clone https://github.com/Decelium/decelium_wallet

Install any dependencies locally
> pip install -r requirements.txt

### Command line usage of the Decelium wallet

If you have pip-installed the Decelium wallet Python package, then you can use the `decw` command-line tool.  
The general usage is

    decw COMMAND ARGUMENTS   
    
#### Creating the wallet

From the command line run

    decw generate_a_wallet WALLET

where `WALLET` is the path to the wallet file you wish to create.

You will be prompted to enter a password twice.

#### Adding a user in the wallet

- Back up the wallet (i.e. make a copy of the wallet file)
- from the command line run
    ```
    decw generate_user WALLET USERNAME
    ```
    where `WALLET` is the path of the wallet file you created and `USERNAME` is the name you want the user to have
- Enter your password at the prompt
- The program will then ask "Are you sure you want to write this user? you should backup your wallet first!! (yes/no)", followed by a "Password:" prompt. Enter 'y' or 'yes' (without the quotes) at the prompt. 
- The program will output the new wallet info, including the user's API key and private key. Remember to keep your private key secret.

#### The .password file

You can avoid being prompted for your password when running `decw` commands (except with `generate_a_wallet` and `generate_user`, which will still prompt you) by creating a file called `.password` containing your Decelium wallet password. When you execute a `decw` command, the program searches the working directory for a file called `.password`, and then searches directories upward for a few levels. Hence it makes sense to place the `.password` file at or above the directory where you will be doing most of your Decelium wallet work.

#### Viewing wallet info

You can view the wallet info at any time by executing

    decw display_wallet WALLET
   
where `WALLET` is the path of the wallet file.

#### Further examples

For further examples of the usage of `decw` please see [here](./CLI_USAGE_EXAMPLES.md).

> Note: It would be hard to crack your wallet, but it is absolutely possible for a trained professional to brute force your wallet.
> Save it somewhere secure. We will be releasing a full air-gapped cold wallet solution as soon as possible, 
> and if you are a volunteer interested in this part of the project get in touch!

### Using the Decelium Wallet in Python Programs

There are examples of the use of the Decelium wallet in Python programs [here](./PY_USAGE_EXAMPLES.md).

### Final Notes
1. The Decelium Network hosts have over 192 avaliable functions!
2. Over the coming months, we are working on documentation.
3. The best place to begin is the ./tests/ folder.
4. This is a new repository and still in progress
5. Get in touch!
