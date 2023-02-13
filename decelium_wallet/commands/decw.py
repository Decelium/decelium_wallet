import sys
import importlib

def run(*args):
    command = args[0]
    name = "decelium_wallet.commands."+command
    mod = importlib.import_module(name)
    class_commands = ["deploy","secret","deploy_dns"]
    if command in class_commands:
        c=mod.Deploy()
        c.run(*args[1:])
    else:
        mod.run(*args[1:])

if __name__ == "__main__":
    
    run(*sys.argv[1:])
    
    
