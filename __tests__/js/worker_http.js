// WorkerHTTP.js
import { Core } from '../../decelium_wallet/core.js';
import { MiniGetterSetter } from './MiniGetterSetter.js';
import fs from 'fs';
import process from 'process';
import { v4 as uuidv4 } from 'uuid';

//const fs = require('fs');

class WorkerHTTP {
    constructor(core) {
        this.core = core;
        this.node_address = node;
        this.peer_ids = peers;     
        
    }

    load_wallet_strings_from_disk() {
        let ret = {};
        const wallets = this.core.discover_wallet();
        console.log(wallets);
        for (let wal of wallets) {
            if (wal['wallet'].includes('test_wallet')) {
                try {
                    ret['data'] = fs.readFileSync(wal['wallet'], 'utf8');
                    if (ret['data'].length <= 0) {
                        console.error("Error: Data file is empty.");
                        continue;
                    }

                    ret['password'] = fs.readFileSync(wal['passfile'], 'utf8');
                    if (ret['password'].length <= 0) {
                        console.error("Error: Password file is empty.");
                        continue;
                    }
                    return ret;

                } catch (error) {
                    return {"error":"could not find .password and .wallet.dec in parent path:" + error.toString()};
                }
            }
            
        }
        return {"error":"could not find .password and .wallet.dec in parent path"};
    }
    
    

    async stage_init() {
        await this.core.init();
        const raw_wallet = await this.load_wallet_strings_from_disk();
        if (raw_wallet.error)
            throw new Error('Failed to load wallet fron disk: '+raw_wallet.error);
            
        const success = await this.core.load_wallet(raw_wallet.data, raw_wallet.password);
        if (success !== true) {
            throw new Error('Failed to load wallet');
        }

        const connected = await this.core.initial_connect(
            'https://'+this.node_address+'/data/query',
            'admin'
        );
        if (connected !== true) {
            throw new Error('Failed to connect');
        }
        return true;
    }

    async stage_ipfs_upload() {
        let signed_del = await this.core.dw.sr({q: {'api_key':await this.core.dw.pubk("admin"),
                                   'path':'/test_website/website.ipfs'},user_ids:["admin"]})
        let del_fil  = await this.core.net.delete_entity(signed_del);
        if (typeof del_fil === 'object' && del_fil.error) {
            console.log("delete warning:"+del_fil.error );
            del_fil = true;
        }
        if (del_fil != true) {
            throw new Error("Could not delete old website :"+del_fil );
        }
        
        console.log("1) ------------ REMOVED OLD FILE!")
        let dict_list  = await this.core.net.create_ipfs({
            'api_key':await this.core.dw.pubk("admin"),
            'file_type':'ipfs',
            'ipfs_url':"/dns/35.167.170.96/tcp/5001/http",
            'payload_type':'local_path',
            'payload':'./example_site'});
        console.log({dict_list});
        if (dict_list===undefined) 
            throw new Error("COULD NOT PIN");
        if( typeof dict_list != "object")
            throw new Error("Did not get a list of pins back");
        if( dict_list.length != 5)
            throw new Error("wrong number of files returned");
        
        dict_list.forEach((item) =>{
            
            if( item.cid ==undefined)
                throw new Error("Did not get a CID back");
            if( item.path ==undefined)
                throw new Error("Did not get a path back");
            if( typeof item.cid != 'string')
                throw new Error("Invalid CID");
            if( typeof item.path != 'string')
                throw new Error("Invalid path");
        });
        // TODO check for root item label
        console.log("2) ------------ UPLOADED TO IPFS!")
        let q = {'api_key':this.core.dw.pubk("admin"),
            'path':'test_website',
            'name':'website.ipfs',
            'file_type':'ipfs',
            'payload_type':'ipfs_pin_list',
            'payload':dict_list}
        let q_signed = await this.core.dw.sign_request({q,user_ids:["admin"]});
        let fil  = await this.core.net.create_entity(q_signed);
        
        if (typeof fil === 'object' && fil.error) {
            throw new Error('Failed to connect:'+ fil.error);
        }

        if (typeof fil === 'string' && !fil.includes('obj-')) {
            throw new Error("'obj-' not found in fil:"+fil );
        } 
        
        
        q ={'api_key':this.core.dw.pubk("admin"),
            'self_id':fil,  
            'inner_path':'index.html',
           }
        let content  = await this.core.net.download_entity(q,true,true);        
        console.log(content);
        q ={'api_key':this.core.dw.pubk("admin"),
            'self_id':"obj-7a4a4a4e-62e7-497e-b8a1-1ff3fec7d06a",  
            'inner_path':'data/img.png',
           }
        content  = await this.core.net.download_entity(q,true,true);        
        console.log(content);
        
        return true;
    }
    
    async stage_broadcast() {
        const mimi = new MiniGetterSetter();

        const port = 5003 + parseInt(workerId);
        const name = 'node-session-file-' + workerId + '.node';
        const public_handlers = [
            ['set_value', mimi.set_value.bind(mimi)],
            ['get_value', mimi.get_value.bind(mimi)],
            ['get_all', mimi.get_all.bind(mimi)],
            ['do_echo', (args) => args],
        ];

        const resp = await this.core.listen(port, name,"admin", public_handlers);
        console.log("Listening");
        await new Promise(resolve => setTimeout(resolve, 10000));
        console.log("Done");
        return resp;
    }
 
    async stage_list_nodes() {
        console.log("IN STAGE LIST NODES");
        await new Promise((resolve) => setTimeout(resolve, 500));
        const nodes = await this.core.node_list();
        let found = false;
        let count = 0;
        let count_all = 0;
        for (const n of nodes) {            
            if (n['self_id'] === this.core.self_id) {
                console.log("found self");
                found = true;
            } else {
                if ('test_id' in n['connect_data']['meta']) {
                    count = count + 1;
                    console.log("js passed inspection" + n['self_id']);
                }
            }
            count_all = count_all + 1;
        }
        if (this.peer_ids.length !== count) {
            console.log("self.peer_ids", this.peer_ids.length);
            console.log("count", count);
            console.log(nodes);
            throw new Error("Number of peer ids does not match the count");
        }
        return count_all > 0;    
    }
    

    async stage_set() {
        this.sessions = [];
        for (const peer_connect_data of await this.core.node_peers()) {
            const connect_data = peer_connect_data;
            connect_data.api_key = this.core.dw.pubk('admin');
            const sid = await this.core.net.connect(
                connect_data,
                this.core.handle_connection.bind(this.core)
            );

            const val = uuidv4();
            

            const respset = await this.core.net.set_value(
                {
                    api_key: this.core.dw.pubk('admin'),
                    key: 'test' + workerId,
                    val,
                },
                { session_id: sid }
            );
            const respget = await this.core.net.get_value(
                {
                    api_key: this.core.dw.pubk('admin'),
                    key: 'test' + workerId,
                },
                { session_id: sid }
            );

            if (respset !== true) {
                console.log("THE REPSET");
                console.log(respset);
                throw new Error('Failed to set value');
            }
            if (respget !== val) {
                throw new Error('Failed to get value');
            }
        }
        await new Promise((resolve) => setTimeout(resolve, 2000));
        return true;
    }

    async stage_verify() {
        this.sessions = [];
        console.log('Stored the following data');
        const vals = this.core.service.get_all({});
        console.log(vals);
        return true;
    }

    async stage_shutdown() {
        await this.core.net.disconnect();
        return true;
    }
}


async function run_all_tests(workerId, node, peers) {
    const worker = new WorkerHTTP(new Core(), node, peers);

    const steps = [
        worker.stage_init.bind(worker),
        worker.stage_broadcast.bind(worker),
        worker.stage_list_nodes.bind(worker),
        worker.stage_set.bind(worker),
        //worker.stage_verify.bind(worker),
        worker.stage_shutdown.bind(worker),
    ];

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        console.log(`----------------------------------------------------------`);
        console.log(`[${i}] Worker ${workerId}: ${step.name}`);

        let result = false;
        try {
            result = await step();
        } catch (err) {
            console.error(`Error: ${err}`);
            result = err.stack;
            try {
                console.log("forcing shutdown . . .");
                await worker.stage_shutdown();
                console.log("done");
            } catch (e) {
                console.error("Shutdown failed: ", e);
            }
        }

        console.log(`worker_http.js_${workerId}: Step ${step.name} ${result === true ? 'succeeded' : 'failed'}`);
        if (result !== true) {
            throw new Error(`[${i}] Worker ${workerId}: ${step.name} ${result}`);
        }
    }
}



async function run_ipfs_tests(workerId, node, peers) {
    const worker = new WorkerHTTP(new Core(), node, peers);

    const steps = [
        worker.stage_init.bind(worker),
        worker.stage_ipfs_upload.bind(worker),
    ];

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        console.log(`----------------------------------------------------------`);
        console.log(`.[${i}] Worker ${workerId}: ${step.name}`);

        let result = false;
        try {
            result = await step();
        } catch (err) {
            console.error(`Error: ${err}`);
            result = err.stack;
            try {
                console.log("forcing shutdown . . .");
                await worker.stage_shutdown();
                console.log("done");
            } catch (e) {
                console.error("Shutdown failed: ", e);
            }
        }

        console.log(`worker_http.js_${workerId}: Step ${step.name} ${result === true ? 'succeeded' : 'failed'}`);
        if (result !== true) {
            throw new Error(`[${i}] Worker ${workerId}: ${step.name} ${result}`);
        }
    }
}

//if (require.main === module) {
if (!process.argv[2] || !process.argv[3] || !process.argv[4]) {
    console.error('Required arguments not provided');
    process.exit(1);
}

console.log('running ' + process.argv[2] + ' on ' + process.argv[3]);
const workerId = parseInt(process.argv[2]);
const node = process.argv[3];
const peers = JSON.parse(process.argv[4]);

//run_all_tests(workerId, node, peers).catch(e => console.error(e));
run_ipfs_tests(workerId, node, peers).catch(e => console.error(e));

//} node ./nodejs/worker_http.js 1 dev.paxfinancial.ai "[]"
// node ./worker_http.js 1 dev.paxfinancial.ai "[]"