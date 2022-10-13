# if you import as a library, then the importer is in charge of these imports
import os
import sys
#sys.path.append('./')
#from decelium.crypto import crypto
import decelium
import uuid
import base64
import pprint
import shutil    
import commands
from commands.deploy import Deploy

if __name__ == "__main__":
    command_name = sys.argv[1:][0]
    arg_list = sys.argv[1:][1:] 
    print('----------------')
    print(command_name)
    print(arg_list)
    print('----------------')
    c = Deploy()
    c.run(*arg_list)

