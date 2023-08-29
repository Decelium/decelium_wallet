import sys,os
import importlib

def run():
    
    # Save the original CWD
    original_cwd = os.getcwd()

    # Change the CWD to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    try:
        sys.path.append('../') #Make sure decelium_wallet is in the path
        command = sys.argv[1]
        try:
            name = "decelium_wallet.commands."+command
            mod = importlib.import_module(name)
        except:
            mod = importlib.import_module("commands."+command)        
        with open(mod.__file__,'r') as f:
            code = f.read()
        code_lines = code.splitlines()
        version = None
        contract= None
        os.chdir(original_cwd)
        for r in code_lines[0:3]:
            the_line = r.replace(' ','')
            if the_line.startswith ('#version='):
                version =the_line.split('=')[1]
            if the_line.startswith ('#contract='):
                contract =the_line.split('=')[1]    
        if version == None or contract == None:
            print ("Could not run contract. Version and Contract undefined")


        try:
            contract_class = getattr(mod, contract)  # Get the class from the module
            c = contract_class()
            print(c.run(sys.argv[2:]))
        except:
            print("----------------------")    
            print("version",version)    
            print("----------------------")    
            print("contract",contract)   
            print("----------------------")    
            print("command",command)   
            print("----------------------")    
            print("module",mod.__file__)   

            #if c:
            #    print("----------------------")    
            #    print("c",c)

            print("----------------------")    
            import traceback as tb
            tb.print_exc()
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    run()