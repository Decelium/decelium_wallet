import json
import base64
import pickle
import uuid, json
import copy


class jsondt:
    def loads(dic):
        return json.loads(dic,object_hook=jsondt.datetime_parser)
    def dumps(dic):
        return json.dumps(dic,default=jsondt.datedefault)

    def datedefault(o):
        if isinstance(o, tuple):
            l = ['__ref']
            l = l + o
            return l
        if isinstance(o, (datetime.date, datetime.datetime,)):
            return o.isoformat()

    def datetime_parser(dct):
        DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
        for k, v in dct.items():
            if isinstance(v, str) and "T" in v:
                try:
                    dct[k] = datetime.datetime.strptime(v, DATE_FORMAT)
                except:
                    pass
        return dct

class service:
    def __init__(self):
        self.handlers = {
        }
    def set_handler(self,args):    
        reqs = ["id","name", "handler","group","runtime","meta"];
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
        try:
            if not 'public' in self.handlers:
                return {"error":"No public handler registered for query"}
            qtype = json_obj.get("qtype")
            if not qtype:
                return {"error":"qtype is missing in the JSON object -- "+ str(json_obj)}

            if qtype not in self.handlers[group]:
                return {"error":f"No handler found for qtype '{qtype}'"}

            handler = self.handlers[group][qtype]['handler']
            
            if json_obj.get("__encoded_query"):
                encoded_payload = json_obj.get("__encoded_query")

                if not encoded_payload:
                    return {"error":"PIK Encoded payload is missing in the JSON object"}
                #return encoded_payload
                decoded_payload = self.do_decode(encoded_payload)
                #return str(decoded_payload) + str(handler)
                response = jsondt.dumps(handler(decoded_payload,{}))
                return response
            
            if json_obj.get("__str_encoded_query"):
                encoded_payload = json_obj.get("__str_encoded_query")

                if not encoded_payload:
                    return {"error":"STR Encoded payload is missing in the JSON object"}
                #return encoded_payload
                decoded_payload = self.do_decode_string(encoded_payload)
                #return str(decoded_payload) + str(handler)
                response = jsondt.dumps(handler(decoded_payload,{}))
                return response
            return {"error":"Could not find a decoding method"}
            
        except:
            import traceback as tb
            return "service.run critical error: "+tb.format_exc()


    def do_encode(self,request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self,data_packet):
        from urllib.parse import unquote
        #data_packet = base64.b64decode(unquote(data_packet))   
        data_packet = base64.b64decode(data_packet)   
        #data2 = user_data_dev
        data2 = pickle.loads(data_packet)
        if type(data2) == str:
            data2 = jsondt.loads(data2)
        return data2
    
    def do_encode_string(self,obj):
        string = jsondt.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self,data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = jsondt.loads(user_data_dev.decode("ascii"))
        return data2
    
    def __getattr__(self,attr):
        self.current_attr = attr
        return self.__run_query
    
    def __run_query(self, args):
        #method_to_call = getattr(self, self.current_attr)
        json_obj = {
            "qtype": self.current_attr,
            "__encoded_query":self.do_encode(jsondt.dumps(args))  
        }
        return self.run(json_obj)       