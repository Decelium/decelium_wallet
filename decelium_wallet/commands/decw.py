import sys
import importlib

def run():
    command = sys.argv[1]
    name = "decelium_wallet.commands."+command
    mod = importlib.import_module(name)
    class_commands = ["deploy","secret","deploy_dns"]
    if command in class_commands:
        c=mod.Deploy()
        c.run(*sys.argv[2:])
    else:
        mod.run(*sys.argv[2:])

if __name__ == "__main__":
    
    run()
    
    
