import http_client from './networkchannels/http_client.js';
//import http_server from './http_server.js';
import { v4 as uuidv4 } from 'uuid';

class networkWrapped {
    constructor() {
        this.sessions = {};
        this.servers = {};
        this.listen_on = false;
    }

    //__run_query(...args) {
    //    console.log(this.current_attr); 
    //    console.log(args);
    //    let session_id = args.pop().session_id;
    //    console.log("the session",session_id);
    //   
    //    if (session_id == undefined) {
    //        session_id = Object.keys(this.sessions)[0];
    //    }
    //    console.log("this.sessions[session_id]")
    //    console.log(this.sessions[session_id])
    //    console.log("this.sessions")
    //    console.log(this.sessions)
    //    
    //    const inst = this.sessions[session_id].instance;
    //    const method_to_call = inst[this.current_attr];
    //    return method_to_call(...args);
    //}
    async __run_query(...args) {
        //console.log(this.current_attr); 
        //console.log(args);

        let session_id;
        for (let i = args.length - 1; i >= 0; i--) {
            if (args[i].hasOwnProperty('session_id')) {
                session_id = args[i].session_id;
                args.splice(i, 1);
                break;
            }
        }
        //console.log("the session",session_id);

        if (session_id == undefined) {
            session_id = Object.keys(this.sessions)[0];
        }
        //console.log("this.sessions[session_id]")
        //console.log(this.sessions[session_id])
        //console.log("this.sessions")
        //console.log(this.sessions)

        if (!this.sessions.hasOwnProperty(session_id)) {
            console.error('No session found with the provided ID');
            return;
        }

        const inst = this.sessions[session_id].instance;
        const method_to_call = inst[this.current_attr];
        let val =  await method_to_call(...args);
        console.log("VAL FROM network");
        console.log(val);
        
        return val;
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

    async node_list(session_id = null) {
        if (session_id === null) {
            session_id = Object.keys(this.sessions)[0];
        }
        let date = new Date();
        let utcDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
        utcDate.setMinutes(utcDate.getMinutes() - 3);
        //utcDate.setHours(utcDate.getHours() - 3);
        
        let query = 
            {"attrib": {"connect_data.ping": {"$gte": utcDate.toISOString().split('.')[0].toString()},
                        "file_type":"node"},
            'limit':10};

        query = JSON.parse(JSON.stringify(query));
        //console.log("attrib",query);
        // Assuming "list" method exists in the http_client instance
        this.nodes = await this.sessions[session_id].instance.list(query);
        //console.log("source this.nodes",this.nodes );
        
        return this.nodes;
    }

    /*
    
{'api_key': 'e66eebeb3b56bd627c082a36fb0528e45d1fa8d6a1b9e47d478c3af9a11baaf6431bfdb491ceb6d8c5a3674433dcf5a1a1f9af74cf5a9414d026b68fdcedfc5d', 'limit': 10, 'offset': None, 'key': {'connect_data.ping': {'$gte': datetime.datetime(2023, 5, 12, 4, 42, 18)}, 'file_type': 'node'}}


    
    */
    
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
        this.listen_on = true;
        return true; // Unsupported in JS
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
        this.listen_on = false;
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
        return this.listen_on;
    }
}

// Proxy handler for the dynamic function calls
const proxyHandler = {
    get(target, propKey) {
        if (Reflect.has(target, propKey)) {
            return Reflect.get(target, propKey);
        } else {
            target.current_attr = propKey;
            //let v =  target.__run_query.bind(target);
            //console.log("proxy value!");
            //console.log (v);
            //return v;
            return async (...args) => {
                console.log( "TEST STR");
                let v = target.__run_query(...args);
                console.log( "-----v");
                console.log(v);
                v = await v;
                console.log( "-----await v");
                console.log(v);
                console.log(typeof v);
                return  v;
            };            
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
