import sys,os
import importlib

def run():
    
    # Save the original CWD
    original_cwd = os.getcwd()

    # Change the CWD to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if len(sys.argv) < 2:
        print("expected format: decw COMMAND ARGUMENTS. Installed commands:")
        commands_dir = os.path.join(script_dir, "commands")
        if os.path.isdir(commands_dir):
            command_files = [f[:-3] for f in os.listdir(commands_dir) if f.endswith('.py') and f != '__init__.py']
            for command in command_files:
                print(command)
        else:
            print("No commands directory found.")
        return

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
            try:
                parser = c.get_parser()
                result,args = c.parse_arguments(sys.argv[2:])
                if result == False:
                    return args
                print(c.run(args))
            except:
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

            print("----------------------")    
            import traceback as tb
            tb.print_exc()
    finally:
        os.chdir(original_cwd)
    
if __name__ == "__main__":
    run()


'''
TODO -- Notes for argument parsing decorator in progress
    def get_parser(self):
        parser = argparse.ArgumentParser(description='Command description.')
        parser.add_argument('wallet_path', nargs='?', default=None, type=str, help='This is the path for your project wallet, usually named .wallet.dec')
        parser.add_argument('--wallet_path', default=None,required=False, dest='wallet_path_named', type=str, help='This is the path for your project wallet, usually named .wallet.dec')
        self.parser = parser

    def parse_arguments(self,args):
        # parser = self.get_parser()
        try:
            # return False,args
            try:
                parsed_args = self.parser.parse_args(args)
            except:
                return False,{"error":"Failure parsing args. Please run decw generate_a_wallet --help"}
            # Decide which wallet_path to use (prioritize the named argument if provided)
            try:
                assert parsed_args.wallet_path_named != None
                wallet_path = parsed_args.wallet_path_named
            except:
                wallet_path = parsed_args.wallet_path
        
            arguments_dict = {
                'wallet_path': wallet_path,
            }
            if (wallet_path == None or type(wallet_path) != str):
                return False, {"error":"wallet_path is required, and must be a string"}
            return True, arguments_dict
        except Exception as e:
            error_msg = f"Error parsing arguments: {e}\n"
            error_traceback = traceback.format_exc()
        
            # Constructing the error dictionary
            error_dict = {
                'error': error_msg +":"+ error_traceback
            }
        
            return False, error_dict

'''