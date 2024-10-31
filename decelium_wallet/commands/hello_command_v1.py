#contract=HelloCommand
#version=0.1

class HelloCommand():    
    def run(*args):
        print(args)
        return 1

    def exec(self,args):
        import pprint
        print("The Args")
        pprint.pprint(args)
        return 1
