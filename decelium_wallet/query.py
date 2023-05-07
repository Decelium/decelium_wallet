import json
import base64
import pickle
import uuid, json

class Query:
    def __init__(self):
        self.handlers = {
        }
    def set_handler(self,args):    
        reqs = ["name", "handler","group","runtime","meta"];
        for key in reqs:
            assert key in list(args.keys())
        g =args['group']
        n = args['name']
        if g not in self.handlers:
            self.handlers[g] = {}
        self.handlers[g][n] = args 
            
    def run(self, json_obj,group='public'):
        if not 'public' in self.handlers:
            return {"error":"No public handler registered for query"}
        qtype = json_obj.get("qtype")
        if not qtype:
            return {"error":"qtype is missing in the JSON object"}

        if qtype not in self.handlers[group]:
            return {"error":f"No handler found for qtype '{qtype}'"}

        handler = self.handlers[group][qtype]['handler']
        encoded_payload = json_obj.get("__encoded_query")
        if not encoded_payload:
            return {"error":"Encoded payload is missing in the JSON object"}

        decoded_payload = self.do_decode(encoded_payload)
        response = handler(decoded_payload,{})
        return response


    def do_encode(self,request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self,data_packet):
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        #data2 = user_data_dev
        data2 = pickle.loads(user_data_dev)
        data2 = json.loads(data2)
        return data2
    
    def do_encode_string(self,obj):
        string = json.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self,data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2
    
    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_query
    
    def __run_query(self, args):
        #method_to_call = getattr(self, self.current_attr)        
        json_obj = {
            "qtype": self.current_attr,
            "__encoded_query":query.do_encode(json.dumps(req))  
        }
        return query.run(json_obj)       
        
        
    
# Example usage:
if __name__ == "__main__":
    query = Query()
    # Setup of Endpoints
    # [X] Should take Classes
    # [ ] Should take One Off Functions
    # [ ] Should take Versioned Contracts
    # [ ] Should run in WASM sub process?
    
    class MiniGetterSetter:
        def __init__(self):
            self.vals = {}
        def set_value(self, args,settings):
            assert 'key' in args
            assert 'val' in args            
            self.vals[args['key']] = args['val']
            return True
        
        
        def get_value(self, args,settings):
            if args['key'] in self.vals:
                return self.vals[args['key']]
            return False
        
    mimi = MiniGetterSetter()
    
    def do_echo(args,settings):
        return args
    
    for cfg in [("set_value",mimi.set_value),
                ("get_value",mimi.get_value),
                ("do_echo",mimi.do_echo),
               
               ]:
        query.set_handler({"name":cfg[0],
                           "handler":cfg[1],
                           "group":"public",
                           "runtime":None,
                           "meta":{}
                          }) 
    
    
    # Usage #######
    req = {"key":"test_key","val":str(uuid.uuid4())}
    dec = query.set_value(req)
    print(dec)
    
    val = query.get_value({"key":"test_key"})  
    print(val)