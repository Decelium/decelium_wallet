
### Installation

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
    