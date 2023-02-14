

# Python Usage of the Decelium Wallet

## Examples

The following are the Python equivalents of the Decelium wallet [command-line usage examples](./CLI_USAGE_EXAMPLES.md). Note that `deploy` and `secret` have a different interface from the others, breaking the pattern that the rest follow.

```python
import decelium_wallet.commands.generate_a_wallet
decelium_wallet.commands.generate_a_wallet.run("test_wallet1.dec")

import decelium_wallet.commands.display_wallet
decelium_wallet.commands.display_wallet.run("test_wallet1.dec")

import decelium_wallet.commands.generate_user
decelium_wallet.commands.generate_user.run("test_wallet1.dec", "test_user")

import decelium_wallet.commands.display_wallet
decelium_wallet.commands.display_wallet.run("test_wallet1.dec")

import decelium_wallet.commands.create_user
decelium_wallet.commands.create_user.run("test_wallet.dec", "test_user", "test_user1", "test.paxfinancial.ai")

import decelium_wallet.commands.deploy
c = decelium_wallet.commands.deploy.Deploy()
c.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "test/test_upload/example_small_website.ipfs", "./example_small_website/", "test.testdecelium.com", "decelium_com_dns_code")

import decelium_wallet.commands.delete_user
decelium_wallet.commands.delete_user.run("test_wallet.dec", "test_user", "test_user", "test.paxfinancial.ai")

import decelium_wallet.commands.check_balance
decelium_wallet.commands.check_balance.run("test_wallet.dec", "test_user", "test.paxfinancial.ai")

import decelium_wallet.commands.list_account
decelium_wallet.commands.list_account.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")

import decelium_wallet.commands.download_entity
decelium_wallet.commands.download_entity.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")

import decelium_wallet.commands.secret
c = decelium_wallet.commands.secret.Deploy()
c.run("test_wallet1.dec", "test_user", "list")

import decelium_wallet.commands.secret
c = decelium_wallet.commands.secret.Deploy()
c.run("test_wallet1.dec", "test_user", "add", "my_secret", "my_secret_value")

import decelium_wallet.commands.secret
c = decelium_wallet.commands.secret.Deploy()
c.run("test_wallet1.dec", "test_user", "list")

import decelium_wallet.commands.secret
c = decelium_wallet.commands.secret.Deploy()
c.run("test_wallet1.dec", "test_user", "view", "my_secret")
```