#contract=HelloCommand
#version=0.2
import argparse, pprint
try:
    from BaseService import BaseService
except:
    from .BaseService import BaseService

class HelloCommand(BaseService):
    '''
    Example Use:
    ~/data # 
    ~/data # decw hello_command_v2 example=hello
    MyService running with arguments: {'example': 'hello', '__command': ['hello_command_v2']}    
    '''
    @classmethod
    def run(cls, **kwargs):
        print(f"MyService running with arguments: {kwargs}") 
        return 0  # Success exit code

# To test the base class and the run_cli functionality:
if __name__ == "__main__":
    HelloCommand.run_cli()
