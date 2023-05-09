class MiniGetterSetter:
    def __init__(self):
        self.vals = {}
    
    def set_value(self, args,settings):
        assert 'key' in args
        assert 'val' in args
        print("setting value "+args['val'])
        self.vals[args['key']] = args['val']
        return True


    def get_value(self, args,settings):
        if args['key'] in self.vals:
            print("getting value "+args['key'])
            return self.vals[args['key']]
        return self.vals
    
    def get_all(self, args,settings):
        return self.vals    