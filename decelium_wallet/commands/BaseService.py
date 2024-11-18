#contract=BaseService
#version=0.2    
import warnings


try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.simplefilter("ignore", NotOpenSSLWarning)
except ImportError:
    from urllib3.exceptions import InsecureRequestWarning    
    # Fallback to suppress InsecureRequestWarning if NotOpenSSLWarning is not available
    warnings.simplefilter("ignore", InsecureRequestWarning)

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
    def example(cls,**kargs):
        raise Exception("Unimplemented - please ignore this instructive method")

        # Interface for times when persitance allows the command to keep some internal state in self
        import pprint
        print("The Args")
        pprint.pprint(kargs)
        return 1
    
    
    @classmethod
    def run(cls, **kwargs):
        # TO INHERITOR - you may override run for manual control, or leave it in for standad method routing (see examples)
        #print(cls)
        # print(kwargs)        
        command_map = cls.get_command_map()

        assert len(kwargs['__command']) == 1, f"Exactly one command must be specified {kwargs['__command']} "
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

        for item in args.args:
            if '=' in item:
                # Split key=value pairs
                key, value = item.split('=', 1)
                kwargs[key] = value
            else:
                # Treat anything without '=' as a positional argument
                positional_args.append(item)

        # Store the positional args as a list under the '__command' key
        if positional_args:
            kwargs['__command'] = positional_args
        #print(cls)
        #print(kwargs)
        result = cls.run(**kwargs)
        print(f"{result}")
        return result
        # Suppress stdout and stderr until the result is ready
    
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
