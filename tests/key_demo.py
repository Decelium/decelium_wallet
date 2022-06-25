import ecdsa
import sys,binascii
sys.path.append('../')
from crypto import crypto
import pprint


#user = crypto.generate_user()
users = {}
users ['justin'] = {'api_key': 'e66eebeb3b56bd627c082a36fb0528e45d1fa8d6a1b9e47d478c3af9a11baaf6431bfdb491ceb6d8c5a3674433dcf5a1a1f9af74cf5a9414d026b68fdcedfc5d', 
                    'private_key': 'e453d4d02b8ce82d0bb1328ea38e7bb47437f6253c25b8bcd91aa9770618a180', 
                    'version':"python-ecdsa-0.1",
                    'type': 'ecdsa.SECP256k1'}

users ['new_justin'] = {'api_key': 'a7c85ae300241c848f3ef6f355ef4c8865574ad40f1d2bdb5c42e51da076694cdc3982031b7c69e9d9f389d3526f1b97510774289956eed485e00718e11808e3', 
                        'private_key': 'beeb1986ec17859ac094b46e937bfefb91194b76534107bca7cfc44e773ee4dd', 
                        'version': 'python-ecdsa-0.1'}


user = users['new_justin']
#print(user)
msg = {'api_key':user['api_key'], 'v1':'a', 'v2':'b'}
signers = [{'api_key':user['api_key'], 'private_key':user['private_key']}]
msg_verified = crypto.sign_request(msg,signers)
pprint.pprint(crypto.verify_request(msg_verified))
