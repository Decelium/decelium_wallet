#contract=BaseService
#version=0.2    
import warnings
import json
import subprocess
import shutil
import inspect
import tempfile

try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.simplefilter("ignore", NotOpenSSLWarning)
except ImportError:
    from urllib3.exceptions import InsecureRequestWarning    
    # Fallback to suppress InsecureRequestWarning if NotOpenSSLWarning is not available
    warnings.simplefilter("ignore", InsecureRequestWarning)

from contextlib import contextmanager
import os

"""
USAGE:

#contract=HelloCommand --- Tells Decelium which class to import (to support large files)
#version=0.2 --- Tells Decelium to assume the command inherits BaseService
# Example inheriting class -- Make the class
class HelloCommand(BaseService):
    @classmethod
    def run(cls, **kwargs):
        print(f"MyService running with arguments: {kwargs}")
        return 0  # Success exit code

# Enable the CLI interface via "python3 HelloCommand.py arg1=arg arg2=arg_other"
if __name__ == "__main__": -- To 
    HelloCommand.run_cli()

"""
'''
@contextmanager
def suppress_stdout():
    # Save the original stdout
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    try:
        yield
    finally:
        # Restore original stdout
        sys.stdout.close()
        sys.stdout = original_stdout
'''
@contextmanager
def suppress_stdout():
    """
    Suppresses stdout and stderr by redirecting them to /dev/null.
    Restores them properly after the context ends.
    """
    # Save the original sys.stdout and sys.stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Open /dev/null
    devnull = open(os.devnull, 'w')

    try:
        # Redirect sys.stdout and sys.stderr to /dev/null
        sys.stdout = devnull
        sys.stderr = devnull
        yield
    finally:
        # Restore original sys.stdout and sys.stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        devnull.close()


import argparse, pprint, sys
class BaseService(): 
    
    @classmethod
    def get_command_map(cls):
        raise Exception("Unimplemented - please override this method")
        command_map = {
            'example': {
                'required_args': [],
                'method': cls.example,
            },

        }
        return command_map
    
    @classmethod
    def get_core_command_map(cls):
        # compile_for(cls, platform: str = "auto", onefile: bool = True, output_dir: str = None):
        command_map = {
            'compile_for': {
                'required_args': ['platform','onefile','output_dir'],
                'method': cls.example,
            },

        }
        return command_map    
    
    @classmethod
    def example(cls,**kargs):
        raise Exception("Unimplemented - please ignore this instructive method")

        # Interface for times when persitance allows the command to keep some internal state in self
        import pprint
        print("The Args")
        pprint.pprint(kargs)
        return 1
    
    
    @classmethod
    def run(cls, **kwargs):
        # Apply dynamic config files, if attached in args.        
        # If you detect "!XYZ=JSON+PATH -- inline replace the key with values"
        cfg_in = {}
        for key in list(kwargs.keys()):

            if type(kwargs[key]) != str or not kwargs[key].endswith(".json]]"):
                continue
            pth = kwargs[key].replace("]]","").replace("[[","")
            with open(pth.strip(), "r") as f:
                #print(f"READING {pth}")
                parse_str = f.read()
                #print(f"READING {parse_str}")
                cfg_in = json.loads(parse_str)                
    
            if key.startswith("[["):
                kwargs.update(cfg_in)
                del kwargs[key]
            elif kwargs[key].startswith("[["):
                kwargs[key] = cfg_in

        command_map = cls.get_command_map()
        command_map.update(cls.get_core_command_map())
        assert '__command'  in  kwargs, f"Need at least one command. Like >command_exec COMMAND: COMMAND is required from {command_map.keys()} "
        
        assert len(kwargs['__command']) == 1, f"Exactly one command must be specified {kwargs['__command']}:{kwargs['__command']} "
        cmd = kwargs['__command'][0]
        if cmd not in command_map:
            raise ValueError(f"Unknown command: {cmd}")

        command_info = command_map[cmd]
        required_args = command_info.get('required_args', [])
        method = command_info['method']
        for arg in required_args:
            assert arg in kwargs, f"Missing required argument: {arg} for command {cmd}"
        del(kwargs['__command'])
        method_kwargs = kwargs
        return method(**method_kwargs)   

    @staticmethod
    def _strip_enclosing_quotes(value: str) -> str:
        if (
            isinstance(value, str)
            and len(value) >= 2
            and value[0] == value[-1]
            and value[0] in ("'", '"', "`")
        ):
            return value[1:-1]
        return value    
    @classmethod
    def run_cli(cls):
        """This method parses CLI arguments, converts them to kwargs, and passes them to run."""
        # Create a parser that accepts positional arguments
        parser = argparse.ArgumentParser(description="Generic service CLI for any BaseService subclass.")

        # Add positional argument to capture any argument
        parser.add_argument('args', nargs=argparse.REMAINDER, help='Command arguments and key=value pairs')

        # Parse all the arguments
        args = parser.parse_args()

        # Separate positional arguments (commands) and keyword arguments
        positional_args = []
        kwargs = {}

        verbose = False
        for item in args.args:
            if item == '--v':
                verbose = True
            elif '=' in item:
                # Split key=value pairs
                key, value = item.split('=', 1)
                kwargs[key] = BaseService._strip_enclosing_quotes(value)
            else:
                # Treat anything without '=' as a positional argument
                positional_args.append(item)
        #print(" ARG WORK")
        #print(f"kwargs {kwargs}")
        #print(f"positional_args {positional_args}")
        # Store the positional args as a list under the '__command' key
        if positional_args:
            kwargs['__command'] = positional_args
        #print(cls)

        kwargs = cls.add_depth(kwargs)
        #print(json.dumps(kwargs, indent = 4))
        kwargs = cls.add_depth(kwargs)
        #print("Debug json:"+json.dumps(kwargs, indent = 4))
        #return
        result = cls.run(**kwargs)
        print(f"{result}")
        #return result
        # Suppress stdout and stderr until the result is ready
    '''
    @classmethod
    def add_depth(cls, flat: dict) -> dict:
        """
        Convert a flat dict with dot‑notation keys into a nested dict.
        Keys without a dot remain at the root.

        Parameters
        ----------
        flat : dict
            Input dictionary. Keys may be of the form "group.subkey".

        Returns
        -------
        nested : dict
            Nested dictionary.

        Example
        -------
        >>> flat = {
        ...     "command.field_1": 2,
        ...     "command.hello": "hi",
        ...     "field": 2,
        ...     "other.no": "x",
        ...     "other.what": "y",
        ... }
        >>> add_depth(flat)
        {
            "command": {"field_1": 2, "hello": "hi"},
            "field": 2,
            "other": {"no": "x", "what": "y"}
        }
        """
        nested = {}
        for key, value in flat.items():
            if '.' in key:
                group, subkey = key.split('.', 1)
                nested.setdefault(group, {})[subkey] = value
            else:
                nested[key] = value
        return nested
    '''

    @classmethod
    def to_arg_string(cls,flat: dict) -> str:
        """
        Convert a flat dictionary into a command-line argument string.
        
        Each key-value pair is formatted as:
            "key"=value
        where the key is always enclosed in double quotes. If a value is a string,
        it will also be enclosed in double quotes.
        
        Parameters
        ----------
        flat : dict
            A flat dictionary with keys and their corresponding values.
        
        Returns
        -------
        str
            A single argument string with each key-value pair separated by a space.
        
        Examples
        --------
        >>> flat = {"a.a": 1, "b": "2"}
        >>> to_arg_string(flat)
        '"a.a"=1 "b"="2"'
        """
        parts = []
        for key, value in flat.items():
            # Always quote the key.
            formatted_key = f'"{key}"'
            # Format the value: quote it if it's a string.
            if isinstance(value, str):
                formatted_value = f'"{value}"'
            else:
                formatted_value = str(value)
            parts.append(f'{formatted_key}={formatted_value}')
        return " ".join(parts)
    
    @classmethod
    def add_depth(cls, flat: dict, sep: str = ".") -> dict:
        from collections.abc import MutableMapping

        def insert_path(nested, keys, value):
            key = keys[0]
            is_index = key.isdigit()
            idx = int(key) - 1 if is_index else key

            if len(keys) == 1:
                if is_index:
                    # Ensure list is large enough
                    while len(nested) <= idx:
                        nested.append(None)
                    nested[idx] = value
                else:
                    nested[key] = value
                return

            next_key = keys[1]
            is_next_index = next_key.isdigit()

            if is_index:
                while len(nested) <= idx:
                    nested.append([] if is_next_index else {})
                if not isinstance(nested[idx], (list, dict)):
                    nested[idx] = [] if is_next_index else {}
                insert_path(nested[idx], keys[1:], value)
            else:
                if key not in nested:
                    nested[key] = [] if is_next_index else {}
                insert_path(nested[key], keys[1:], value)

        nested = {}
        for flat_key, value in flat.items():
            keys = flat_key.split(sep)
            is_root_index = keys[0].isdigit()
            if is_root_index:
                if not isinstance(nested, list):
                    nested = []
                insert_path(nested, keys, value)
            else:
                insert_path(nested, keys, value)

        return nested


    # Example usage
    if __name__ == "__main__":
        flat_config = {"a.a": 1, "b": "2"}
        arg_string = to_arg_string(flat_config)
        print(arg_string)  # Output: "a.a"=1 "b"="2"
    
    '''
    @classmethod
    def flatten(cls,nested: dict, parent_key: str = "", sep: str = ".") -> dict:
        """
        Convert a nested dictionary into a flat dictionary with dot‑notation keys.
        Nested keys are concatenated using a dot, forming keys like "group.subkey".

        Parameters
        ----------
        nested : dict
            The nested input dictionary.
        parent_key : str, optional
            A prefix used in the recursion to build the dot‑notation key. 
            Defaults to an empty string.
        sep : str, optional
            The separator between key components. Defaults to ".".

        Returns
        -------
        flat : dict
            The flattened dictionary.

        Example
        -------
        >>> nested = {
        ...     "command": {"field_1": 2, "hello": "hi"},
        ...     "field": 2,
        ...     "other": {"no": "x", "what": "y"}
        ... }
        >>> flatten(nested)
        {
            "command.field_1": 2,
            "command.hello": "hi",
            "field": 2,
            "other.no": "x",
            "other.what": "y"
        }
        """
        flat = {}
        for key, value in nested.items():
            # If there is a parent key, prepend it to the current key using the separator
            full_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                # Recurse into the nested dictionary and update the flat dictionary
                flat.update(cls.flatten(value, full_key, sep=sep))
            else:
                flat[full_key] = value
        return flat
    '''
    @classmethod
    def flatten(cls, nested: dict, parent_key: str = "", sep: str = ".") -> dict:
        from collections.abc import Mapping, Sequence

        flat = {}

        def _flatten(obj, parent_key):
            if isinstance(obj, Mapping):
                for k, v in obj.items():
                    full_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
                    _flatten(v, full_key)
            elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
                for i, v in enumerate(obj, start=1):
                    full_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                    _flatten(v, full_key)
            else:
                flat[parent_key] = obj

        _flatten(nested, parent_key)
        return flat
    '''
_cmd_start kwargs: {'protocol': 'http', 'host': '127.0.0.1', 'port': '8003', 'url': '/do_upload', 'command_uri': '/cmd', 'upload_dir': './tmp/upload', 'settings_dir': './tmp/settings', 'tokens': '<<DSH_SERVER_TOKEN_LIST>>', 'openai_api_key': '<<OPENAI_API_KEY>>', 'published': []}
_cmd_start cmdDict: {'protocol': 'http', 'host': '127.0.0.1', 'port': '8003', 'url': '/do_upload', 'command_uri': '/cmd', 'upload_dir': './tmp/upload', 'settings_dir': './tmp/settings', 'tokens': '<<DSH_SERVER_TOKEN_LIST>>', 'openai_api_key': '<<OPENAI_API_KEY>>'}
'''

    @classmethod
    def compile_for(cls, platform: str = "auto", onefile: bool = True, output_dir: str = None):
        """
        Compiles the current service class to a standalone binary using Nuitka.

        Parameters:
        - platform: Target platform (currently placeholder; actual cross-compilation is not implemented).
        - onefile: Whether to bundle output as a single executable.
        - output_dir: Where to place the compiled binary. If None, creates a temp directory.
        """
        source_file = inspect.getfile(cls)
        service_name = cls.__name__
        output_dir = output_dir or tempfile.mkdtemp()
        build_args = [
            "nuitka",
            "--standalone",
            "--follow-imports",
            f"--output-dir={output_dir}",
        ]

        if onefile:
            build_args.append("--onefile")

        build_args.append(source_file)

        print(f"Compiling {service_name} from {source_file} to {output_dir}...")
        subprocess.run(build_args, check=True)
        print(f"Compilation complete. Files in: {output_dir}")

    @classmethod
    def get_binary_name(cls, platform: str = None):
        """
        Returns the expected output binary filename based on class name and platform.
        """
        name = cls.__name__
        ext = ".exe" if (platform or sys.platform).startswith("win") else ""
        return f"{name}{ext}"


    #@classmethod
    #def __init_subclass__(cls, **kwargs):
    #    """This method is automatically called when a subclass is created."""
    #    super().__init_subclass__(**kwargs)
    #    #print("INIT SUBCLASS")
    #    #print(sys.modules['__main__'].__file__)
    #    #print(sys.argv[0])
    #    ## Automatically run the CLI when the subclass is executed as the main module
    #    #if sys.argv[0] in sys.modules['__main__'].__file__:
    #    #    
    #    #    cls.run_cli()






'''
#
# INHERIT METHOD ONE - CLOBBER THE RUN COMMAND
#
class HelloCommand(BaseService):
    @classmethod
    def run(cls, **kwargs):
        print(f"MyService running with arguments: {kwargs}")
        return 0  # Success exit code

# To test the base class and the run_cli functionality:
if __name__ == "__main__":
    HelloCommand.run_cli()
'''

'''
#
# INHERIT METHOD TWO - Register named services
#
# This second method allows users to use get_command_map() to return a 
#
class HelloCommand(BaseService):
    @classmethod
    def get_command_map(cls):
        command_map = {
            'example': {
                'required_args': [],
                'method': cls.example,
            },
            'example_req': {
                'required_args': ['arg1','arg2'],
                'method': cls.example_req,
            },

        }
        return command_map

    @classmethod
    def example(cls,**kargs):
        # Interface for times when persitance allows the command to keep some internal state in self
        import pprint
        print("The Args")
        pprint.pprint(kargs)
        return 1
    @classmethod
    def example_req(cls,arg1,arg2):
        # Interface for times when persitance allows the command to keep some internal state in self
        import pprint
        pprint.pprint(arg1)
        pprint.pprint(arg2)
        return 1

# To test the base class and the run_cli functionality:
if __name__ == "__main__":
    HelloCommand.run_cli()
# python3 BaseService.py example hello=1
# python3 BaseService.py example_req arg1=1 arg2=1 
'''

#if __name__ == "__main__":
#    BaseService.run_cli()
