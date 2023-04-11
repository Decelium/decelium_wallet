

# Python Usage of the Decelium Wallet

## Examples

The following are the Python equivalents of the Decelium wallet [command-line usage examples](./CLI_USAGE_EXAMPLES.md).
Example Import:
import decelium_wallet.commmands.generate_a_wallet as generate_a_wallet

# Generate a wallet
### This line generates a new wallet file with the name "test_wallet1.dec"
```
generate_a_wallet.run("test_wallet1.dec")
```

# Display wallet
### This line displays the content of the wallet file "test_wallet1.dec"
```
display_wallet.run("test_wallet1.dec")
```

# Generate user
### This line generates a new user for the wallet file "test_wallet1.dec" with the username "test_user"
```
generate_user.run("test_wallet1.dec", "test_user")
```


# Display wallet
### This line displays the content of the wallet file "test_wallet1.dec"
```
display_wallet.run("test_wallet1.dec")
```

# Create user
### This line creates a new user "test_user1" for the wallet file "test_wallet.dec" with the username "test_user" 
```
create_user.run("test_wallet.dec", "test_user", "test_user1", "test.paxfinancial.ai")
```

# Deploy
### This block deploys a website located at "test/test_upload/example_small_website.ipfs" 
```
c = deploy.Deploy()
c.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "test/test_upload/example_small_website.ipfs", "./example_small_website/", "test.testdecelium.com", "decelium_com_dns_code")
```

# Delete user
### This line deletes the user "test_user" for the wallet file "test_wallet.dec" 
```
delete_user.run("test_wallet.dec", "test_user", "test_user", "test.paxfinancial.ai")
```

# Check balance
### This line checks the balance of the user "test_user" for the wallet file "test_wallet.dec" on the host "test.paxfinancial.ai"
```
check_balance.run("test_wallet.dec", "test_user", "test.paxfinancial.ai")
```

# List account
### This line lists the accounts for the user "test_user" for the wallet file "test_wallet.dec" on the host "test.paxfinancial.ai" starting from the root directory "/"
```
list_account.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")
```

# Download entity
### This line downloads the entities for the user "test_user" 
```
download_entity.run("test_wallet.dec", "test_user", "test.paxfinancial.ai", "/")
```
