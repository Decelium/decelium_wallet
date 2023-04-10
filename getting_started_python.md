# Getting Started in Python

The Decelium wallet Python package allows you to use the Decelium wallet commands from within Python programs. This document will show you how to create a wallet, create a user ID in the wallet, and fund a user.

## Prerequisites

You will need Python 3 and pip installed.

## Installation

### Linux

On Linux:

    pip install "git+https://github.com/Decelium/decelium_wallet.git"

### Windows

On Windows:

    pip install "git+https://github.com/Decelium/decelium_wallet.git" 
    
    
## Using the Decelium Wallet in Python

Here is an example Python script that uses the Decelium wallet to generate a wallet, generate a user in the wallet, create a user on Decelium, and fund the user's account. Note that each command must be imported before it is used.

A wallet contains user ID's and associated public/private key pairs.  A wallet and wallet user ID are needed for virtually every Decelium command, hence our first step is to create a wallet, which is created in an empty state.  The wallet requires a password; a password should be stored in a file called `.password` in, or up to three levels above, the working directory in which you are using your Python code.  If there is no `.password` file you will be prompted to enter a password at the keyboard. 
```python
import decelium_wallet.commands.generate_a_wallet as generate_a_wallet
gen_wallet=generate_a_wallet.run("./test_wallet.dec")
```
Now that we have a wallet, we can generate a user ID in the wallet. This will create a public/private key pair associated with the user ID, stored in the wallet.  We will name the wallet user ID "test_user".
```python
import decelium_wallet.commands.generate_user as generate_user
gen_user=generate_user.run("./test_wallet.dec","test_user","confirm")
```
In order to perform tasks such as uploading a website to Decelium, we have to also create a user on Decelium. This user is associated with a user ID, and hence public/private key pair, in the wallet.  We will create a user on Decelium with user name "test_user1" and password "passtest", which is associated with the "test_user" user ID in our wallet.
```python
import decelium_wallet.commands.create_user as create_user    
user_id=create_user.run("./test_wallet.dec","test_user","test_user1","test.paxfinancial.ai","passtest")
```
Many tasks on Decelium, including uploading a website, require a fee to be paid in Celium, the cryptocurrency Decelium runs on. We can fund our wallet with Celium with the `fund` command:
```python
import decelium_wallet.commands.fund as fund
fund_result=fund.run("./test_wallet.dec","test_user","test.paxfinancial.ai")
```
Now that we have created a wallet, generated a user ID for it, created a user on Decelium, and funded our wallet with Celium, we are ready to perform other tasks on Decelium, such as uploading websites.


## Further Examples of Use of the Decelium Wallet in Python Programs

There are examples of the use of the Decelium wallet in Python programs [here](./PY_USAGE_EXAMPLES.md). You can also consult the unit tests to see further usage examples.