const { execSync } = require('child_process');
const fs = require('fs');
const assert = require('assert');
const uuid = require('uuid');
const axios = require('axios');

function captureOutput() {
  process.stdout.flush();
  process.stderr.flush();

  const originalStdout = process.stdout;
  const originalStderr = process.stderr;

  process.stdout = fs.createWriteStream('data.out');
  process.stderr = process.stdout;

  return { originalStdout, originalStderr };
}

function restoreOutput(originalStdout, originalStderr) {
  process.stdout.flush();
  process.stderr.flush();

  process.stdout = originalStdout;
  process.stderr = originalStderr;
}

const { originalStdout, originalStderr } = captureOutput();

try {
  let cmdStr = 'rm .password';
  execSync(cmdStr);

  cmdStr = 'rm test_wallet.dec';
  execSync(cmdStr);

  cmdStr = 'rm -rf website';
  execSync(cmdStr);

  cmdStr = 'mkdir website';
  execSync(cmdStr);

  fs.writeFileSync(
    'website/index.html',
    `<!DOCTYPE html>
    <html>
    <body>
    
    <p>This text is normal.</p>
    
    <p><em>This text is emphasized.</em></p>
    
    </body>
    </html>`
  );

  cmdStr = 'yes | pip uninstall decelium_wallet';
  execSync(cmdStr);

  cmdStr = 'pip install "git+https://github.com/Decelium/decelium_wallet.git"';
  execSync(cmdStr);

  const generateAWallet = require('decelium_wallet/commands/generate_a_wallet');
  const generateUser = require('decelium_wallet/commands/generate_user');
  const createUser = require('decelium_wallet/commands/create_user');
  const fund = require('decelium_wallet/commands/fund');
  const checkBalance = require('decelium_wallet/commands/check_balance');
  const deploy = require('decelium_wallet/commands/deploy');
  const deleteUser = require('decelium_wallet/commands/delete_user');

  fs.writeFileSync('.password', 'passtest');

  let wallet = generateAWallet.run('./test_wallet.dec');
  assert.strictEqual(wallet.length, 0);

  wallet = generateUser.run('./test_wallet.dec', 'test_user', 'confirm');
  assert.strictEqual(wallet.hasOwnProperty('test_user'), true);
  assert.strictEqual(wallet.test_user.hasOwnProperty('description'), true);
  assert.strictEqual(wallet.test_user.hasOwnProperty('image'), true);
  assert.strictEqual(wallet.test_user.hasOwnProperty('secrets'), true);
  assert.strictEqual(wallet.test_user.hasOwnProperty('title'), true);
  assert.strictEqual(wallet.test_user.hasOwnProperty('user'), true);
  assert.strictEqual(wallet.test_user.user.hasOwnProperty('api_key'), true);
  assert.strictEqual(wallet.test_user.user.hasOwnProperty('private_key'), true);
  assert.strictEqual(wallet.test_user.user.hasOwnProperty('version'), true);

  const testUsername = `test_user${uuid.v4()}`;
  const userId = createUser.run('./test_wallet.dec', 'test_user', testUsername, 'test.paxfinancial.ai', 'passtest');
  assert.strictEqual(userId.startsWith('obj-'), true);

  const fundResult = fund.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
  assert.strictEqual(fundResult, true);

  const balance = checkBalance.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai');
  assert.strictEqual(balance, 200);

  const websiteId = deploy.run('./test_wallet.dec', 'test_user', 'test.paxfinancial.ai', 'test/example_small_website.ipfs', './website/');
  const url = `https://test.paxfinancial.ai/obj/${websiteId}/`;
  assert(websiteId.startsWith('obj-'));
  
  //const response = await axios.get(url);
  assert.strictEqual(response.status, 200);
  assert.strictEqual(response.data, `<!DOCTYPE html>\n<html>\n<body>\n\n<p>This text is normal.</p>\n\n<p><em>This text is emphasized.</em></p>\n\n</body>\n</html>\n`);
  
  const delResult = delete_user.run('./test_wallet.dec', 'test_user', testUsername, 'test.paxfinancial.ai');
  assert(delResult === true);
  
  fs.unlinkSync('.password');
  fs.unlinkSync('test_wallet.dec');
  fs.rmdirSync('website', { recursive: true });
    
  restoreOutput(originalStdout, originalStderr);
  console.log('1');
  process.exit(0);
} catch (e) {
  restoreOutput(originalStdout, originalStderr);
  console.error(e);
  process.exit(1);
}
