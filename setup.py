from setuptools import setup

import os
import sys
import subprocess

#path = os.path.dirname(os.path.abspath(sys.argv[0]))
#subprocess.run(["setx", "PATH", "%PATH%;"+path], shell=True)

setup(
    name='decelium_wallet',
    version='0.1.0',    
    description='The Decelium wallet',
    url='https://github.com/Decelium/decelium_wallet.git',
    author='Justin Girard',
    author_email='justingirard@decelium.com',
    packages=['decelium_wallet','decelium_wallet.commands', 'decelium_wallet.tests','decelium_wallet.networkchannels', 'decelium_wallet.database'],
    entry_points = {
        'console_scripts': ['decw=decelium_wallet.decw:run'],
    },
    install_requires=[ 'ecdsa',
                        'cryptography',
                        'flask',
                        'pandas',
                        'zipfile36'
                      ],
)
