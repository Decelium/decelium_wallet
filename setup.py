from setuptools import setup

setup(
    name='decelium_wallet',
    version='0.1.0',    
    description='The Decelium wallet',
    url='https://github.com/Decelium/decelium_wallet.git',
    author='Justin Girard',
    author_email='justin.girard@justingirard.com',
    packages=['decelium_wallet','decelium_wallet.commands', 'decelium_wallet.tests'],
    install_requires=[ 'ecdsa',
                        'cryptography',
                        'flask',
                        'pandas',
                        'zipfile36'
                      ],
)