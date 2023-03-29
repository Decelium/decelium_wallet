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
    
### Unit Tests

To run the unit tests, `cd` to the `__tests__/python` directory and run
    
    bash test_script.sh
    
### Using the Decelium Wallet in Python

#### Creating a Wallet

    wallet=generate_a_wallet.run("./test_wallet.dec")
    
#### Creating a User Id in the Wallet

    wallet=generate_user.run("./test_wallet.dec","test_user","confirm")
    
#### Registering a User on Decelium

    user_id=create_user.run("./test_wallet.dec","test_user",test_username,"test.paxfinancial.ai","passtest")
    
#### Funding a User

    fund_result=fund.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
    
#### Uploading a Website

    website_id = deploy.run("./test_wallet.dec","test_user","test.paxfinancial.ai","test/example_small_website.ipfs","./website/")
 
#### Visiting the Uploaded Website

The uploaded website will be available at `https://test.paxfinancial.ai/obj/[website_id]/` where `[website_id]` is the value returned upon uploading the website in the previous step.