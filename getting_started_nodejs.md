
#### NPM Install 

NPM installation of the [**Decelium wallet**](https://github.com/Decelium/decelium_wallet) is necessary if you want to write JavaScript programs or apps that interact with the Decelium server.

The installation command is
    
    npm install https://github.com/Decelium/decelium_wallet

# Getting Started with Decelium Wallet Node.js SDK

The Decelium Wallet Node.js SDK allows developers to interact with the Decelium Wallet platform from within Node.js applications.

## Prerequisites

Before you can use the Decelium Wallet Node.js SDK, you will need to have Node.js and npm installed on your machine. You can download Node.js from the official Node.js website, and npm is included with Node.js.

You will also need a Decelium Wallet account. You can sign up for a Decelium Wallet account on the Decelium Wallet website.

## Installation

To install the Decelium Wallet Node.js SDK, run the following command in your project directory:

    npm install decelium-wallet
    
## Usage

To use the Decelium Wallet Node.js SDK, you will need to import the various commands provided by the SDK:

```javascript
const generateAWallet = require('decelium-wallet').generateAWallet;
const generateUser = require('decelium-wallet').generateUser;
const createUser = require('decelium-wallet').createUser;
const fund = require('decelium-wallet').fund;
const checkBalance = require('decelium-wallet').checkBalance;
const deploy = require('decelium-wallet').deploy;
const deleteUser = require('decelium-wallet').deleteUser;
```

Once you have imported the commands, you can use them in your code. Here is an example script that uses the Decelium Wallet Node.js SDK to generate a wallet, create a user, fund the user's account, deploy a website, and then delete the user:

```javascript
const generateAWallet = require('decelium-wallet').generateAWallet;
const generateUser = require('decelium-wallet').generateUser;
const createUser = require('decelium-wallet').createUser;
const fund = require('decelium-wallet').fund;
const checkBalance = require('decelium-wallet').checkBalance;
const deploy = require('decelium-wallet').deploy;
const deleteUser = require('decelium-wallet').deleteUser;
const assert = require('assert');

(async () => {
  try {
    const wallet = await generateAWallet.run('./test_wallet.dec');
    assert.strictEqual(wallet.length, 0);

    const testUsername = 'test_user' + Math.random().toString(36).substring(7);
    const user = await generateUser.run('./test_wallet.dec', testUsername, 'confirm');
    assert.strictEqual(user[testUsername].description, '');
    assert.strictEqual(user[testUsername].image, '');
    assert.strictEqual(user[testUsername].secrets.length, 0);
    assert.strictEqual(user[testUsername].title, '');
    assert.strictEqual(user[testUsername].user.api_key.length, 40);
    assert.strictEqual(user[testUsername].user.private_key.length, 64);
    assert.strictEqual(user[testUsername].user.version, 3);

    const userId = await createUser.run('./test_wallet.dec', 'test_user', testUsername, 'test.paxfinancial.ai', 'passtest');
    assert.strictEqual(userId.substr(0, 4), 'obj-');

    const fundResult = await fund.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
    assert.strictEqual(fundResult, true);

    const balance = await checkBalance.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
    assert.strictEqual(balance, 200);

    const websiteId = await deploy.run('./test_wallet.dec', 'test_user', 'test.paxfinancial
```