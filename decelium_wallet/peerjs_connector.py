import json
import base64
from peerjspython.src.peerjs.peer import Peer, PeerOptions
from peerjspython.src.peerjs.enums import ConnectionType, ConnectionEventType, PeerEventType
from aiortc import RTCConfiguration, RTCIceServer
import asyncio

import requests
from threading import Thread

SERVER_ADDR = '52.11.216.136'
SERVER_PORT = 8765

class PeerJSConnector:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_request_handler(self, handler_function):
        self.request_handler = handler_function

    def __init__(self):
        if PeerJSConnector._instance is not None:
            raise Exception('PeerJSConnector is a singleton. Use PeerJSConnector.get_instance() to get an instance.')

        self.request_handler = None
        self.peer = None
        self.peers = dict()
        #self.connect()

    #def connect(self):
        #self.peer = Peer(id=None, host=SERVER_ADDR, port=SERVER_PORT, path='/myapp', secure=False)
        #print('Connecting!')
        
        

        #self.peer.on('open', lambda id: self.on_open(id))
        #self.peer.on('disconnected', lambda: self.on_disconnected())
        #self.peer.on('error', lambda error: self.on_error(error))
        #print('Connecting 2!')
    async def connect(self):
        options = PeerOptions(
            host=SERVER_ADDR,
            port=SERVER_PORT,
            secure=False,
            path="/myapp",
            config=RTCConfiguration(
                iceServers=[
                    # Add your RTCIceServer configurations here
                ]
            )
        )
        self.peer = Peer(id=None, peer_options=options)
        self.id_assigned = asyncio.Event()
        
        await self.peer.start()
        
        @self.peer.on(PeerEventType.Open)
        async def on_open(peer_id):
            print('Connected with ID:', peer_id)
            self.peer.on(PeerEventType.Connection, self.handle_connection)
            self.id_assigned.set()
        
        @self.peer.on(PeerEventType.Disconnected)
        async def on_disconnected():
            print('Disconnected.')
            await self.connect()

        @self.peer.on(PeerEventType.Error)
        async def on_error(error):
            print('Peer error:', error)        
        
        print('Connecting!')
        await self.id_assigned.wait()
    
    def on_open(self, id):
        print('Connected with ID:', id)
        self.peer.on('connection', lambda conn: self.handle_connection(conn))

    def on_disconnected(self):
        print('Disconnected.')
        self.connect()

    def on_error(self, error):
        print('Peer error:', error)

    def discover_peers(self):
        response = requests.get(f'http://{SERVER_ADDR}:{SERVER_PORT}/peerjs/peers')
        peers = response.json()
        return peers

    def check_received_messages(self):
        return [{"peerId": k, "messages": v.messages} for k, v in self.peers.items()]

    '''
    async def send_message(self, receiver_uuid, content):
        conn = self.peers.get(receiver_uuid)
        if not conn:
            conn = await self.peer.connect(receiver_uuid)
            self.handle_connection(conn)
            conn.on('open', lambda: conn.send(content))
        else:
            conn.send(content)
    '''
    async def send_message(self, receiver_uuid, content):
        conn = self.peers.get(receiver_uuid)
        if not conn:
            connection_options = {
                'originator': True,
                'reliable': True,
                'constraints':None,
                'type': ConnectionType.Data,  # Assuming you're using DataConnection
                'constraints': None,  # You can provide constraints if needed
                'metadata': None,  # You can provide metadata if needed
                'sdpTransform': None,  # You can provide an SDP transform function if needed
            }            
            #connection_options.sdpTransform = None
            conn_coroutine = await self.peer.connect(receiver_uuid,connection_options)
            
            conn = conn_coroutine
            # conn = await conn_coroutine
            self.handle_connection(conn)
            await conn.send(content)
        else:
            await conn.send(content)    
            
    def disconnect(self):
        self.peer.destroy()

    def encode_data(self, data):
        return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

    def decode_data(self, encoded_data):
        return json.loads(base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8'))

    def send_request(self, destination_user, func, payload, args):
        request_data = self.encode_data({"func": func, "payload": payload, "args": args})
        self.send_message(destination_user, f'*exe*{request_data}')

    def send_response(self, destination_user, response):
        response_data = self.encode_data(response)
        self.send_message(destination_user, f'*resp*{response_data}')

    async def process_request(self, request_data):
        data = self.decode_data(request_data)
        if self.request_handler:
            return await self.request_handler(data)
        return {"error": "no handler attached"}

    async def receive_result(self, response_data):
        decoded_data = self.decode_data(response_data)
        print(decoded_data)

    def handle_connection(self, conn):
        #conn.on('data', lambda data: self.on_data(conn, data))
        #conn.on('open', lambda: self.on_conn_open(conn))
        #conn.on('close', lambda: self.on_conn_close(conn))
        #conn.on('error', lambda error: self.on_conn_error(conn, error))
        pass
    
    def on_data(self, conn, data):
        print('Received message:', data)
        if data.startswith('*exe*'):
            request_data = data[5:]
            Thread(target=self.handle_exe, args=(conn.peer, request_data)).start()
        elif data.startswith('*resp*'):
            response_data = data[6:]
            Thread(target=self.handle_resp, args=(response_data,)).start()
        else:
            if not hasattr(conn, 'messages'):
                conn.messages = []
            conn.messages.append(data)
            print('Received message:', data)

    def handle_exe(self, peer, request_data):
        result = asyncio.run(self.process_request(request_data))
        self.send_response(peer, result)

    def handle_resp(self, response_data):
        asyncio.run(self.receive_result(response_data))

    def on_conn_open(self, conn):
        print('Connected to peer:', conn.peer)
        self.peers[conn.peer] = conn

    def on_conn_close(self, conn):
        print('Connection closed:', conn.peer)
        self.peers.pop(conn.peer, None)

    def on_conn_error(self, conn, error):
        print('Connection error:', error)
