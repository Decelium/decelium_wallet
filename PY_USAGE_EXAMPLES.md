

# Python Usage of the Decelium Wallet

## Examples

The following are the Python equivalents of the Decelium wallet [command-line usage examples](./CLI_USAGE_EXAMPLES.md).
Example Import:
import decelium_wallet.commmands.generate_a_wallet as generate_a_wallet

```
# Generate a wallet
generate_a_wallet.run("test_wallet1.dec")
# This line generates a new wallet file with the name "test_wallet1.dec"

# Display wallet
display_wallet.run("test_wallet1.dec")
# This line displays the content of the wallet file "test_wallet1.dec"

# Generate user
generate_user.run("test_wallet1.dec", "test_user")
# This line generates a new user for the wallet file "test_wallet1.dec" with the username "test_user"

# Display wallet
display_wallet.run("test_wallet1.dec")
# This line displays the content of the wallet file "test_wallet1.dec"

# Create user
create_user.run("test_wallet.dec", "test_user", "test_user1", "test.paxfinancial.ai")
# This line creates a new user "test_user1" for the wallet file "test_wallet.dec" with the username "test_user" 

# Deploy
c = deploy.Deploy()
c.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "test/test_upload/example_small_website.ipfs", "./example_small_website/", "test.testdecelium.com", "decelium_com_dns_code")
# This block deploys a website located at "test/test_upload/example_small_website.ipfs" 

# Delete user
delete_user.run("test_wallet.dec", "test_user", "test_user", "test.paxfinancial.ai")
# This line deletes the user "test_user" for the wallet file "test_wallet.dec" 

# Check balance
check_balance.run("test_wallet.dec", "test_user", "test.paxfinancial.ai")
# This line checks the balance of the user "test_user" for the wallet file "test_wallet.dec" on the host "test.paxfinancial.ai"

# List account
list_account.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")
# This line lists the accounts for the user "test_user" for the wallet file "test_wallet.dec" on the host "test.paxfinancial.ai" starting from the root directory "/"

# Download entity
download_entity.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")
# This line downloads the entities for the user "test_user" 
```
