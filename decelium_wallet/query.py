import json
import base64
import pickle

class Query:
    def __init__(self):
        self.handlers = {
            "echo": self.echo_handler
        }

    def run(self, json_obj):
        qtype = json_obj.get("qtype")
        if not qtype:
            raise ValueError("qtype is missing in the JSON object")

        if qtype not in self.handlers:
            raise ValueError(f"No handler found for qtype '{qtype}'")

        handler = self.handlers[qtype]
        encoded_payload = json_obj.get("__encoded_query")
        if not encoded_payload:
            raise ValueError("Encoded payload is missing in the JSON object")

        decoded_payload = self.do_decode(encoded_payload)
        response = handler(decoded_payload)
        return response

    def echo_handler(self, payload):
        return payload

    #def decode_payload(self, encoded_payload):
    #    decoded_payload = base64.b64decode(encoded_payload)
    #    return pickle.loads(decoded_payload)

    def do_encode(self,request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self,data_packet):
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        #data2 = user_data_dev
        data2 = pickle.loads(user_data_dev)
        return data2
    
    def do_encode_string(self,obj):
        string = json.dumps(obj,separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self,data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2
    
# Example usage:
if __name__ == "__main__":
    query = Query()
    json_obj = {
        "qtype": "echo",
        "__encoded_query": "gAN9cQAoWAIAAAABYXJnc5RAWAYAAAABaGVsbG+mLmZsYXNrLmJ1aWx0aW5zLkltbXV0YWJsZUxpc3QKIm11dGFibGUgbGlzdCIKYXBwbGljYXRpb24vZGF0YQ=="
    }
    result = query.run(json_obj)
    print(result)
