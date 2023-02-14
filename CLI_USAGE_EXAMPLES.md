 

# Decelium Wallet Command Line Usage

## Examples

The following are examples Decelium commands using the `decw` command-line tool. To use this tool you must have pip-installed the Decelium wallet.  All of these tools will prompt you for your wallet password if you don't have a `.password` file.  If you do have a `.password` file, then `generate_a_wallet` and `generate_user` will still prompt you for your password, but the other commands will no longer prompt you but will take your password from the file.

- `decw generate_a_wallet test_wallet1.dec`: Generate a new wallet with the name `test_wallet1.dec`. This will prompt you for your password, twice for confirmation.
- `decw display_wallet test_wallet1.dec`: Display the contents of the `test_wallet1.dec` wallet.
- `decw generate_user test_wallet1.dec test_user`: Generate a new user with the name `test_user` in the `test_wallet1.dec` wallet. This will prompt you for your password, and then will prompt for a yes/no answer to create the user in the wallet.
- `decw display_wallet test_wallet1.dec`: Display the contents of the `test_wallet1.dec` wallet.
- `decw create_user test_wallet.dec test_user test_user1 test.paxfinancial.ai`: Create a new Decelium account with user name `test_user1` on the `test.paxfinancial.ai` server. This account will have the same API key as the wallet user `test_user` in the wallet `test_wallet.dec`.
- `decw deploy test_wallet.dec test_user test.paxfinancial.ai test/test_upload/example_small_website.ipfs ./example_small_website/ test.testdecelium.com decelium_com_dns_code`: Deploy the website contained in the `./example_small_website/` directory to the Decelium Network. The deployment uses the `test.paxfinancial.ai` server, so the website will have an address on the `test.paxfinancial.ai` domain. The wallet `test_wallet.dec` contains the wallet user `test_user`. To deploy, `test_user` must have created a Decelium account on `test.paxfinancial.ai`. The file will be stored in the Decelium file system in `test_user`'s files at the path `test/test_upload/example_small_website.ipfs`.  The user has added a DNS to the website so that it will appear at the address `test.testdecelium.com`; the user owns the domain `testdecelium.com` and has their DNS secret code stored as a secret in their wallet with the key `decelium_com_dns_code`.
- `decw delete_user test_wallet.dec test_user test_user1 test.paxfinancial.ai`: Delete the Decelium account with the name `test_user1` from the server `test.paxfinancial.ai`. The Decelium account is owned by the wallet user `test_user` in the wallet `test_wallet.dec`.
- `decw check_balance test_wallet.dec test_user test.paxfinancial.ai`: Check the balance of the user with the name `test_user` in the `test_wallet.dec` wallet, with the domain `test.paxfinancial.ai`.
- `decw list_account test_wallet.dec test_user test.paxfinancial.ai /`: List the files in the root directory of the user with the name `test_user` in the `test_wallet.dec` wallet, with the domain `test.paxfinancial.ai`.
- `decw download_entity test_wallet.dec test_user test.paxfinancial.ai /`: Download the file(s) in the root directory of the user with the name `test_user` in the `test_wallet.dec` wallet, with the domain `test.paxfinancial.ai`.
- `decw secret test_wallet1.dec test_user list`: List all the secrets in the `test_wallet1.dec` wallet for the `test_user`.
- `decw secret test_wallet1.dec test_user add my_secret my_secret_value`: Add a secret with the key `my_secret` and the value `my_secret_value` to the `test_wallet1.dec` wallet for the `test_user`.
- `decw secret test_wallet1.dec test_user list`: List all the secrets in the `test_wallet1.dec` wallet for the `test_user`.
- `decw secret test_wallet1.dec test_user view my_secret`: View the value of the secret with the key `my_secret` in the `test_wallet1.dec` wallet for the `test_user`.

Note: Replace the wallet and user names, domain, and file/directory paths as appropriate for your use case.