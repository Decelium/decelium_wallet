/*
import { XMLHttpRequest } from 'xmlhttprequest';
//import { default as WebRTC } from 'electron-webrtc';
import { WebSocket as WS } from 'ws';
import wrtc from 'wrtc'; // Import 'wrtc' instead of 'electron-webrtc'

global.window = global;  

global.XMLHttpRequest = XMLHttpRequest;

//const wrtc = WebRTC();
//global.RTCPeerConnection = wrtc.RTCPeerConnection;
//global.RTCSessionDescription = wrtc.RTCSessionDescription;
//global.RTCIceCandidate = wrtc.RTCIceCandidate;

global.RTCPeerConnection = wrtc.RTCPeerConnection;
global.RTCSessionDescription = wrtc.RTCSessionDescription;
global.RTCIceCandidate = wrtc.RTCIceCandidate;

console.log(global.RTCPeerConnection);
console.log(RTCPeerConnection);


global.WebSocket = WS;
global.location = {
  protocol: 'http'
};


global.window.postMessage = (message, targetOrigin) => {
  setImmediate(() => {
    const event = new MessageEvent('message', { data: message, origin: targetOrigin });
    global.window.dispatchEvent(event);
  });
};

global.window.addEventListener = (type, listener) => {
  global.window.on(type, listener);
};

global.window.removeEventListener = (type, listener) => {
  global.window.off(type, listener);
};

global.window.dispatchEvent = (event) => {
  const listeners = global.window.listeners.get(event.type) || [];
  for (const listener of listeners) {
    listener(event);
  }
};


global.window.listeners = new Map();

global.window.on = (type, listener) => {
  let listeners = global.window.listeners.get(type);
  if (!listeners) {
    listeners = [];
    global.window.listeners.set(type, listeners);
  }
  listeners.push(listener);
};

global.window.off = (type, listener) => {
  const listeners = global.window.listeners.get(type);
  if (listeners) {
    const index = listeners.indexOf(listener);
    if (index >= 0) {
      listeners.splice(index, 1);
    }
  }
};
*/

import  Peer  from 'peerjs';


const SERVER_ADDR = '52.11.216.136';
const SERVER_PORT = 8765;

class PeerJSConnector {
  static instance = null;

  static getInstance() {
    if (!this.instance) {
      this.instance = new PeerJSConnector();
    }
    return this.instance;
  }
  setRequestHandler(aFunction){
      this.requestHandler = aFunction;
  }
  constructor() {
    if (PeerJSConnector.instance) {
      throw new Error('PeerJSConnector is a singleton. Use PeerJSConnector.getInstance() to get an instance.');
    }
    
    this.requestHandler = undefined;
    this.peer = null;
    this.peers = new Map();

   // this.connect();
  }

async connect() {
  return new Promise(async (resolve, reject) => {
    this.peer = new Peer(undefined, {
      host: SERVER_ADDR,
      port: SERVER_PORT,
      path: "/myapp",
        debug:3,
      secure: false,
    });

    console.log('Connecting!');

    this.peer.on('open', (id) => {
      console.log('Connected with ID:', id);
      this.peer.on('connection', this.handleConnection.bind(this));
      resolve(); // Resolve the promise when the connection is open
    });

    this.peer.on('disconnected', () => {
      console.log('Disconnected.');
      this.connect();
    });

    this.peer.on('error', (error) => {
      console.error('Peer error:', error);
      reject(error); // Reject the promise if there's an error
    });

    console.log('Connecting 2!');
  });
}
    

  async discoverPeers() {
    return new Promise(async (resolve) => {
      const response = await fetch(`http://${SERVER_ADDR}:${SERVER_PORT}/peerjs/peers`);
      const peers = await response.json();
      resolve(peers);
    });
  }

  async checkReceivedMessages() {
    return Array.from(this.peers.values()).map((conn) => {
      const messages = conn.messages || [];
      conn.messages = [];
      return { peerId: conn.peer, messages };
    });
  }
    
  async sendMessage(receiverUuid, content) {
    if (!this.peer || !this.peer.open)
    {
        console.error('sendMessage: Peer is not connected.');
        return;
    }
    let conn = this.peers.get(receiverUuid);
    console.log("1?");
    if (!conn) {
      conn = this.peer.connect(receiverUuid);
     console.log("2?");
      this.handleConnection(conn);
      console.log("3?");
        
      conn.on('open', () => {
            console.log("3.1?");
          console.log('Sending message:',receiverUuid, content);
          conn.send(content);
        });
      console.log("4?");
    }
      else
      {
            console.log("3.2?");
          conn.send(content);
      }
   console.log("5?");

  }

  async disconnect() {
    this.peer.destroy();
  }
    

  // New functions
  encodeData(data) {
    return btoa(JSON.stringify(data));
  }

  decodeData(encodedData) {
    return JSON.parse(atob(encodedData));
  }

  async sendRequest(destinationUser, func, payload, args) {
    const requestData = this.encodeData({ func, payload, args });
    await this.sendMessage(destinationUser, `*exe*${requestData}`);
  }

  async sendResponse(destinationUser, response) {
    const responseData = this.encodeData(response);
       console.log('Sending resp:',destinationUser , responseData);
    await this.sendMessage(destinationUser, `*resp*${responseData}`);
  }

  async processRequest(requestData) {
    const { func, payload, args } = this.decodeData(requestData);
    if (this.requestHandler)
        return await this.requestHandler({ func, payload, args } )
    return {"error":"no handler attached"};
  }

  async receiveResult(responseData) {
    const decodedData = this.decodeData(responseData);
    console.log(decodedData);
  }

  handleConnection(conn) {
    conn.on('data', async (data) => {
      console.log('Received message:', data);

      if (data.startsWith('*exe*')) {
        const requestData = data.slice(5);
        const result = await this.processRequest(requestData);
        await this.sendResponse(conn.peer, result);
      } else if (data.startsWith('*resp*')) {
        const responseData = data.slice(6);
        await this.receiveResult(responseData);
      } else {
        this.peer.messages = conn.messages || [];
        this.peer.messages.push(data);
        console.log('Received message:', data);
      }
    });

    conn.on('open', () => {
      console.log('Connected to peer:', conn.peer);
      this.peers.set(conn.peer, conn);
    });

    conn.on('close', () => {
      console.log('Connection closed:', conn.peer);
      this.peers.delete(conn.peer);
    });

    conn.on('error', (error) => {
      console.error('Connection error:', error);
    });      
      
  }    
}

export default PeerJSConnector;

// npm install node-peerjs-client
// npm install peerjs-nodejs