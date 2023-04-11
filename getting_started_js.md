# Getting Started in JavaScript

This document describes the basics of using the Decelium wallet from within plain JavaScript. It will show you how to create a wallet, create a user ID in the wallet, and fund a user.
    
## Usage

Our example script will generate a wallet, generate a user in the wallet, create a user on Decelium, and fund the user's account.

We first must import the Decelium wallet 
```javascript
import {decelium_wallet} from "https://cdn.jsdelivr.net/gh/Decelium/decelium_wallet/decelium_wallet/decelium.mjs"
```
We must initialize the Decelium wallet,
```javascript
let dw = decelium_wallet; 
dw.init().then( async () => {
    //rest of the script will go here
})
```
The rest of our script will go in the body of the at-present empty callback function.

A wallet contains user ID's and associated public/private key pairs.  A wallet and wallet user ID are needed for virtually every Decelium command, hence our first step is to create a wallet, which is created in an empty state.  
```javascript    
    const wallet = await dw.commands.generate_a_wallet.run('./test_wallet.dec');
```
Now that we have a wallet, we can generate a user ID in the wallet. This will create a public/private key pair associated with the user ID, stored in the wallet.  We will name the wallet user ID "test_user".
```javascript
    const user = await dw.commands.generate_user.run('./test_wallet.dec', 'test_user', 'confirm');
```
In order to perform tasks such as uploading a website to Decelium, we have to also create a user on Decelium. This user is associated with a user ID, and hence public/private key pair, in the wallet.  We will create a user on Decelium with user name "test_user1" and password "passtest", which is associated with the "test_user" user ID in our wallet.
```javascript
    const userId = await dw.commands.create_user.run('./test_wallet.dec', 'test_user', 'test_user1', 'test.paxfinancial.ai', 'passtest');
```
Many tasks on Decelium, including uploading a website, require a fee to be paid in Celium, the crytpocurrency Decelium runs on. We can fund our wallet with Celium with the `fund` command:
```javascript
    const fundResult = await dw.commands.fund.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
```

Putting the above all together in a script, we have:

```javascript
<script type="module">
    import {decelium_wallet} from "https://cdn.jsdelivr.net/gh/Decelium/decelium_wallet/decelium_wallet/decelium.mjs"

    let dw = decelium_wallet; 
    dw.init().then( async () => {
      
        const wallet = await dw.commands.generate_a_wallet.run('./test_wallet.dec');

        const user = await dw.commands.generate_user.run('./test_wallet.dec', 'test_user', 'confirm');

        const userId = await dw.commands.create_user.run('./test_wallet.dec', 'test_user', 'test_user1', 'test.paxfinancial.ai', 'passtest');

        const fundResult = await dw.commands.fund.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
    })

</script>                                                   
```
Now that we have created a wallet, generated a user ID for it, created a user on Decelium, and funded our wallet with Celium, we are ready to perform other tasks on Decelium, such as uploading websites.

## Further Examples of Use of the Decelium Wallet in JavaScript

You can consult the unit tests to see further examples.
