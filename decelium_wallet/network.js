import http_client from './networkchannels/http_client.js';
//import http_server from './http_server.js';
import { v4 as uuidv4 } from 'uuid';

class networkWrapped {
    constructor() {
        this.sessions = {};
        this.servers = {};
    }

    __run_query(...args) {
        let session_id = args.pop();
        if (session_id === undefined) {
            session_id = Object.keys(this.sessions)[0];
        }
        const inst = this.sessions[session_id].instance;
        const method_to_call = inst[this.current_attr];
        return method_to_call(...args);
    }

    gen_node_ping(args) {
        for (const k of ['name', 'api_key', 'self_id', 'port', 'meta', 'services']) {
            if (!(k in args)) {
                return { "error": "network: you must provide " + k };
            }
        }

        for (const skey in args.services) {
            for (const k of ['name', 'id']) {
                if (!(k in args.services[skey])) {
                    throw new Error(`Missing key ${k} in services[${skey}]`);
                }
            }
        }
        args.meta.port = args.port;
        args.meta.url = "http://localhost:" + args.port + "/";

        const message = {
            'name': args.name,
            'api_key': args.api_key,
            'self_id': args.self_id,
            'connect_data': {
                "id": "localhost-" + args.port,
                'type': 'tcpip',
                'meta': args.meta,
                'services': args.services
            }
        };
        return message;
    }

    node_list(session_id = null) {
        if (session_id === null) {
            session_id = Object.keys(this.sessions)[0];
        }
        let date = new Date();
        date.setMinutes(date.getMinutes() - 3);

        let query = {
            "connect_data.ping": {"$gte": date},
            "file_type":"node"
        };
        
        // Assuming "list" method exists in the http_client instance
        this.nodes = this.sessions[session_id].instance.list({"attrib":query,'limit':10});
        return this.nodes;
    }

    connect(args, handler = null) {
        if (typeof args === 'object') {
            let inst_id = uuidv4();
            if ('connect_data' in args) {
                let cd = args['connect_data'];
                this.sessions[inst_id] = args;
                this.sessions[inst_id].instance = new http_client(cd['meta']['url'], args['api_key'], cd['meta']['port']);
            } else {
                this.sessions[inst_id] = args;
                this.sessions[inst_id].instance = new http_client(args['url'], args['api_key'], args['port']);
            }
            return inst_id;
        } else {
            return false;
        }
    }

    listen(args, handler) {
        return false; // Unsupported in JS
        /*
        if (typeof args === 'object') {
            let inst_id = uuidv4();
            if ('connect_data' in args) {
                let cd = args['connect_data'];
                this.servers[inst_id] = args;
                this.servers[inst_id].instance = new http_server(cd['meta']['port'], handler);
                this.servers[inst_id].instance.listen(cd['meta']['port']);
            } else {
                this.servers[inst_id] = args;
                this.servers[inst_id].instance = new http_server(args['port'], handler);
                this.servers[inst_id].instance.listen(args['port']);
            }
            return inst_id;
        } else {
            return false;
        }*/
    }

    disconnect(session_id = null) {
        return true;
        /*for (let skey in this.servers) {
            // Assuming "disconnect" method exists in the http_server instance
            let disconnect = this.servers[skey].instance.disconnect();
        }
        return true;*/
    }

    list_sessions() {
        return this.sessions;
    }

    connected() {
        return Object.keys(this.sessions).length > 0;
    }

    listening() {
        return true;
    }
}

// Proxy handler for the dynamic function calls
const proxyHandler = {
    get(target, propKey) {
        if (Reflect.has(target, propKey)) {
            return Reflect.get(target, propKey);
        } else {
            target.current_attr = propKey;
            return target.__run_query.bind(target);
        }
    }
};

// Factory function to create a new network instance with proxy
function network() {
    const net = new networkWrapped();
    return new Proxy(net, proxyHandler);
}

export default network;
export {network};
