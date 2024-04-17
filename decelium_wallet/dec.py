import sys
import os
import json
import argparse
import importlib

def load_configuration(source_path,context_file):
    """ Load configuration from a local 'dec_config.json' if it exists. """
    config_path = os.path.join(source_path, context_file)
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    return {}

def merge_configs(cmd_args, file_config):
    """ Merge command line arguments with file configuration. Command line args take precedence. """
    for key, value in cmd_args.items():
        file_config[key] = value
    return file_config

def run():
    # Change the CWD to the script's directory
    original_cwd = os.getcwd()
    source_path = original_cwd
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    # Initialize argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Command to execute')
    known_args, remaining_argv = parser.parse_known_args()

    if known_args.command.lower() == "help":
        # If the help command is given, show available commands
        commands_dir = os.path.join(script_dir, "commands")
        if os.path.isdir(commands_dir):
            command_files = [f[:-3] for f in os.listdir(commands_dir) if f.endswith('.py') and f != '__init__.py']
            for command in command_files:
                print(command)
        else:
            print("No commands directory found.")
        os.chdir(original_cwd)
        return
    
    command_line_args = {}
    while remaining_argv:
        if remaining_argv[0].startswith('--'):
            command_line_args[remaining_argv[0][2:]] = remaining_argv[1]
        remaining_argv = remaining_argv[2:]

    if 'ctx' in list(command_line_args.keys()):
        context_file = command_line_args['ctx']
    else:
        context_file = 'dec_config.json'
    file_config = load_configuration(source_path,context_file)
    # Merge configurations
    final_args = merge_configs(command_line_args, file_config)


    # Load and run the command module
    current_cwd = os.getcwd()
    try:
        os.chdir(script_dir)

        sys.path.append('../')  # Ensure decelium_wallet is in the path
        try:
            mod = importlib.import_module("commands." + known_args.command)
        except:
            print("Could not find command `"+ known_args.command+"`")
            return False
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

        contract_class = getattr(mod, contract)  # Use a defined class attribute to specify contract
        instance = contract_class()
        print(instance.exec(final_args))  # Run the command with final_args

    except Exception as e:
        print("Error running command:", str(e))
        import traceback
        traceback.print_exc()

    finally:
        os.chdir(original_cwd)
    
if __name__ == "__main__":
    run()
