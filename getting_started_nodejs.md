# Getting Started in Node.js

The Decelium Wallet Node.js SDK allows developers to interact with the Decelium Wallet platform from within Node.js applications.

## Prerequisites

Before you can use the Decelium Wallet Node.js SDK, you will need to have Node.js and npm installed on your machine. You can download Node.js from the official Node.js website, and npm is included with Node.js.

## Installation

To install the Decelium Wallet for Node.js, run the following command in your project directory:

    npm install https://github.com/Decelium/decelium_wallet
    
## Usage

To use the Decelium Wallet Node.js SDK, you will need to import it:

```javascript
const {decelium_wallet} = require('decelium-wallet').decelium;
```

Once you have imported the Decelium wallet, you can use it in your code. Here is an example script that uses the Decelium Wallet Node.js SDK to generate a wallet, generate a user in the wallet, create a user on Decelium, fund the user's account, deploy a website, and then delete the user from Decelium:

```javascript
const {decelium_wallet} = require('decelium-wallet').decelium;

async function runScript () {
  
    const dw = decelium_wallet;  
      
    const wallet = await dw.commands.generate_a_wallet.run('./test_wallet.dec');

    const user = await dw.commands.generate_user.run('./test_wallet.dec', 'test_user', 'confirm');
      
    const testUsername = 'test_user' + Math.random().toString(36).substring(7);
    const userId = await dw.commands.create_user.run('./test_wallet.dec', 'test_user', testUsername, 'test.paxfinancial.ai', 'passtest');

    const fundResult = await dw.commands.fund.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');

    const balance = await dw.commands.check_balance.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');

    const websiteId = await dw.commands.deploy.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai', 'test/example_small_website.ipfs', './website/');

  const delResult = await dw.commands.delete_user.run('./test_wallet.dec', 'test_user', testUsername, 'test.paxfinancial.ai');      
}                                                   

runScript();

```