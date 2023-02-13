#!/usr/bash
rm test_wallet1.dec
decw generate_a_wallet test_wallet1.dec
decw display_wallet test_wallet1.dec
decw generate_user test_wallet1.dec test_user
decw display_wallet test_wallet1.dec
decw create_user test_wallet.dec test_user test_user test.paxfinancial.ai
decw deploy test_wallet.dec test_user test.paxfinancial.ai test/test_upload/example_small_website.ipfs ./example_small_website/ test.testdecelium.com decelium_com_dns_code
decw delete_user test_wallet.dec test_user test_user test.paxfinancial.ai
decw check_balance test_wallet.dec test_user test.paxfinancial.ai
decw list_account test_wallet.dec test_user test.paxfinancial.ai /
decw download_entity test_wallet.dec test_user test.paxfinancial.ai /
decw secret test_wallet1.dec test_user list
decw secret test_wallet1.dec test_user add my_secret my_secret_value
decw secret test_wallet1.dec test_user list
decw secret test_wallet1.dec test_user view my_secret 
