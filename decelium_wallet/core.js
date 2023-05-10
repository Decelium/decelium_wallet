// core.js
import { wallet } from './wallet.js';
//import { network } from './network.js';
//import { service } from './service.js';
class network {};
class service {};


class Core {
    isNode()
    {
        if (typeof window === 'undefined') return true;
        return false;
    }
    
    constructor(){
        this.init();
    }
    
    
    async init() {
        
        if (this.isNode())
        {
            //const { loadPyodide } = require("pyodide");
            //const loadPyodide = async () => {
            //    const pyodideModule = await import('pyodide');
            //    return pyodideModule.loadPyodide();
            //};
            
            const { loadPyodide } = await import("pyodide");
            //this.pyodide = await loadPyodide();     
            //const pyodideReady = pyodideLoader.loadPyodide({
            //    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/",
            //    fs
            //});
            //this.pyodide = await pyodideReady;            
        }
        else
        {
            this.pyodide = await window.loadPyodide({indexUrl: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"});
            
        }
        
        this.net = new network();
        this.service = new service();
        this.node_peer_list = null;
    }
    
    
    load_wallet(data, password) {
        if (typeof data !== 'string' || typeof password !== 'string') {
            throw new Error('Invalid argument types.');
        }
        this.dw = new wallet(this);

        const success = this.dw.load({ data, password });
        return success;
    }


    gen_node_ping(port, name) {
        const services = this.service.get_registry('public');
        const q = this.net.gen_node_ping({
            name,
            api_key: this.dw.pubk('admin'),
            self_id: null,
            services,
            meta: { test_id: 'unit_test' },
            port,
        });
        return q;
    }

    async listen(port, name, public_handlers = []) {
        public_handlers.forEach((cfg) => {
            this.service.set_handler({
                id: cfg[0],
                name: cfg[0],
                handler: cfg[1],
                group: 'public',
                runtime: null,
                meta: {},
            });
        });

        const q = this.gen_node_ping(port, name);
        const qSigned = this.dw.sign_request(q, ['admin']);
        if ('error' in qSigned) {
            return qSigned;
        }
        const resp = await this.net.node_ping(qSigned);
        if ('error' in resp) {
            return resp;
        }
        this.self_id = resp.self_id;
        this.net.listen(port);
        if (!this.net.listening()) {
            return { error: 'could not start listening' };
        }
        await new Promise((resolve) => setTimeout(resolve, 3000));
        return true;
    }

    sync_node_list() {
        this.node_peer_list = [];
        this.nodes = this.net.node_list();

        let found = false;
        for (const n of this.nodes) {
            if (n.self_id === this.self_id) {
                found = true;
            } else {
                if ('test_id' in n.connect_data.meta) {
                    this.node_peer_list.push(n);
                    console.log('passed inspection' + n.self_id);
                }
            }
        }
    }

    node_list() {
        if (this.node_peer_list === null) {
            this.sync_node_list();
        }
        return this.nodes;
    }

    node_peers() {
        if (this.node_peer_list === null) {
            this.sync_node_list();
        }
        return this.node_peer_list;
    }

    list_sessions() {
        return this.list_sessions();
    }

    handle_connection(path, args) {
        try {
            const res = this.service.run(args);
            return res;
        } catch (err) {
            return err.stack;
        }
    }

    async initial_connect(target_url = 'https://dev.paxfinancial.ai/data/query', target_user = 'admin') {
        this.primary_session_id = await this.net.connect({
            type: 'tcpip',
            url: target_url,
            port: 5000,
            api_key: this.dw.pubk(target_user),
        }, this.handle_connection.bind(this));

        if (!this.net.connected()) {
            throw new Error('Not connected.');
        }
        return true;
    }
}

export { Core };
