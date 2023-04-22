import { Peer } from 'peerjs';

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

    this.connect();
  }

  async connect() {
    this.peer = new Peer(undefined, {
      host: SERVER_ADDR,
      port: SERVER_PORT,
        path:"/myapp",
      secure: false, // Add this line        
    });
    console.log('Connecting!');

    this.peer.on('open', (id) => {
      console.log('Connected with ID:', id);
      this.peer.on('connection', this.handleConnection.bind(this));
    });

    this.peer.on('disconnected', () => {
      console.log('Disconnected.');
      this.connect();
    });

    this.peer.on('error', (error) => {
      console.error('Peer error:', error);
    });
    console.log('Connecting 2!');
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
    let conn = this.peers.get(receiverUuid);
    console.log("1?");
    if (!conn) {
      conn = this.peer.connect(receiverUuid);
      this.handleConnection(conn);
        conn.on('open', () => {
            console.log("3.1?");
          console.log('Sending message:',receiverUuid, content);
          conn.send(content);
        });
    }
      else
      {
            console.log("3.2?");
          conn.send(content);
      
      }
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