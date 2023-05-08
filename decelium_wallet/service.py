import json
import base64
import pickle
import uuid, json
import copy

class service:
    def __init__(self):
        self.handlers = {
        }
    def set_handler(self,args):    
        reqs = ["id", "handler","group","runtime","meta"];
        for key in reqs:
            assert key in list(args.keys())
        g =args['group']
        n = args['id']
        if g not in self.handlers:
            self.handlers[g] = {}
        self.handlers[g][n] = args 
    
    
    def get_registry(self, group):
        if group not in self.handlers:
            return {"error":"This kind of handler group is not registered"}
        
        reg = copy.deepcopy(self.handlers[group])
        for k in reg:
            del(reg[k]['handler'])
            del(reg[k]['group'])
            del(reg[k]['runtime'])
        return reg
    
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