import json
import os
import datetime
import pickle
import base64
from flask import Flask, request
import logging
from multiprocessing import Process
import threading

class jsondateencode_local:
    def loads(dic):
        return json.loads(dic,object_hook=jsondateencode_local.datetime_parser)
    def dumps(dic):
        return json.dumps(dic,default=jsondateencode_local.datedefault)

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

class httpws_server():
    def __init__(self, port=None, handler=None):
        self.port = port
        self.handler = handler
        self.app = Flask(__name__)
        self.shutdown_token = 'yyhhcthdjasif7'
        self.server_process = None

        # Configure logging to suppress output
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.parent_conn, self.child_conn = Pipe()

        @self.app.route('/', methods=['GET', 'POST'])
        @self.app.route('/<path:path>', methods=['GET', 'POST'])
        def index(path='/'):
            args = request.args if request.method == 'GET' else request.form
            if self.handler == None:
                return '''{"error":"no httpws_server handler assigned"}'''
            self.child_conn.send((path, args.to_dict()))
            response = self.child_conn.recv()
            return response

        @self.app.route('/disconnect', methods=['GET'])
        def disconnect():
            if self.shutdown_token is None:
                return 'Shutdown endpoint is not secured'
            if request.args.get('token') != self.shutdown_token:
                return 'Unauthorized', 401
            raise Exception("Time for me to die")

            return 'Server shutting down...'

        self.server = None

    def listen(self, port):
        self.server_process = Process(target=self.app.run, kwargs={'port': port})
        self.server_process.start()
        return True

    def listening(self):
        return self.server_process is not None and self.server_process.is_alive()

    def process_requests(self):
        while self.listening():
            if self.parent_conn.poll():
                path, args = self.parent_conn.recv()
                response = self.handler(path, args)
                self.parent_conn.send(response)

    def listen(self, port):
        self.process_requests_thread = threading.Thread(target=self.process_requests)
        self.server_process = Process(target=self.app.run, kwargs={'port': port})
        self.server_process.start()
        self.process_requests_thread.start()
        return True

    def listening(self):
        return self.server_process is not None and self.server_process.is_alive()

    def disconnect(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()
            self.process_requests_thread.join()

    def do_encode(self, request_obj):
        serial = pickle.dumps(request_obj)
        user_data_enc = base64.b64encode(serial).decode("ascii")                   
        return user_data_enc
    
    def do_decode(self, data_packet):
        from urllib.parse import unquote
        user_data_dev = base64.b64decode(unquote(data_packet))   
        data2 = pickle.loads(user_data_dev)
        return data2
    
    def do_encode_string(self, obj):
        string = json.dumps(obj, separators=(',', ':'))
        encoded = base64.b64encode(string.encode('ascii'))
        return encoded.decode('ascii') 

    def do_decode_string(self, data_packet):
        user_data_dev = base64.b64decode(data_packet)                   
        data2 = json.loads(user_data_dev.decode("ascii"))
        return data2


