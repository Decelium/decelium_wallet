// WorkerHTTP.js
import { Core } from '../../decelium_wallet/core.js';
import { MiniGetterSetter } from './MiniGetterSetter.js';
import fs from 'fs';
import process from 'process';
import { v4 as uuidv4 } from 'uuid';

//const fs = require('fs');

class WorkerHTTP {
    constructor(core,node,peers,data_in) {
        this.core = core;
        this.node_address = node;
        this.peer_ids = peers; 
        this.data_in = data_in;
        if (this.data_in == undefined)
            this.data_in = {"message":"Data in was not passed to WorkerHTTP"}
    }

    load_wallet_strings_from_disk() {
        let ret = {};
        const wallets = this.core.discover_wallet();
        //console.log(wallets);
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
        //console.log( this.data_in );
        await this.core.init();
        let raw_wallet = {}
        if (Object.keys(this.data_in).includes("wallet"))
        {
            raw_wallet["password"] = this.data_in["wallet"]["password"];
            raw_wallet["data"] = this.data_in["wallet"]["data"];
        }
        else
        {
            raw_wallet = await this.load_wallet_strings_from_disk();
        }
        
        
        //console.log("---------------------");
        let password = "1234";
        let encryption = await this.core.dw.crypto.encode({'content':"testmessage",'password':password});
        //console.log("encrypted data :"+encryption);
        let decrypted = await this.core.dw.crypto.decode({'payload':encryption,'password':password});
        //console.log("decrypted data :"+decrypted);
        //console.log("---------------------");
        
        //console.log( "INIT 2" );
        if (raw_wallet.error)
            throw new Error('Failed to load wallet fron disk: '+raw_wallet.error);
        //console.log( "INIT 3" );
        //console.log({raw_wallet})
        const success = await this.core.load_wallet(raw_wallet.data, raw_wallet.password);
        if (success !== true) {
            throw new Error('Failed to load wallet');
        }
        //console.log( "INIT 4" );

        const connected = await this.core.initial_connect(
            'https://'+this.node_address+'/data/query',
            'admin'
        );
        //console.log( "INIT 5" );
        
        if (connected !== true) {
            throw new Error('Failed to connect');
        }
        //console.log( "INIT 6" );
        
        //console.log(this.core.dw.get_raw())
        return true;
    }

    // query(filter, source_id, {remote = false, url_version = 'dev', wait_seconds = 120, re_query_delay = 5, show_url = false})
    async stage_ipfs_upload() {
        
        //console.log('contentTest aaa');
        /*
        let q2 ={'api_key':this.core.dw.pubk("admin"),
            'self_id':"obj-a17db5c4-5544-48f1-9117-cb3de095231c",  
            'inner_path':'data/img.png',
            //'inner_path':'example.txt',
           }
        let contentTest  = await this.core.net.download_entity(q2,true,true);        
        console.log('contentTest b');
        console.log(contentTest);
        return true;       
        */
        
        
        let signed_del = await this.core.dw.sr({q: {'api_key':await this.core.dw.pubk("admin"),
                                   'path':'/test_website/website.ipfs'},user_ids:["admin"]})
        let del_fil  = await this.core.net.delete_entity(signed_del);
        if (typeof del_fil === 'object' && del_fil.error) {
            console.log("delete warning:"+del_fil.error );
            del_fil = true;
        }
        if (del_fil != true) {
            console.log(del_fil);
            throw new Error("Could not delete old website :"+del_fil );
        }
        console.log("1) ------------ REMOVED OLD FILE!");
        let dict_list = [];
        let connection_settings = {
          host: 'ipfs.infura.io',
          port: 5001,
          protocol: 'https',
          headers: {
            authorization: 'Basic ' + Buffer.from('2X4hcFqmM5QyWMj7aR9rQcthN5q' + ':' + '686773513d65eeb2d7d22dfdc79d230f').toString('base64'),
          },
        };       
        
        
        //let connection_settings = {
        //  host: '35.167.170.96',
        //  port: 5001,
        //  protocol: 'http',
        //  headers: {
        //  //  authorization: 'Basic ' + Buffer.from('2X4hcFqmM5QyWMj7aR9rQcthN5q' + ':' + '686773513d65eeb2d7d22dfdc79d230f').toString('base64'),
        //  },
        //};         
        
        if (Object.keys(this.data_in).includes("files"))
        {
         
            console.log("UPLOADING BYTES (browser and nodejs)");
             dict_list  = await this.core.net.create_ipfs({
                'api_key':await this.core.dw.pubk("admin"),
                'connection_settings':connection_settings,
                'file_type':'ipfs',
                'payload_type':'raw_file_list',
                'payload':this.data_in.files});          
            
        }
        else
        {
            console.log("UPLOADING DIRECTORY (nodjs only)");
             dict_list  = await this.core.net.create_ipfs({
                'api_key':await this.core.dw.pubk("admin"),
                'connection_settings':connection_settings,                 
                'file_type':'ipfs',
             //   'ipfs_url':"/dns/35.167.170.96/tcp/5001/http",
                'payload_type':'local_path',
                'payload':'./example_site'});          
            console.log(dict_list);
        }         
        
        console.log({dict_list});
        if (dict_list===undefined) 
            throw new Error("COULD NOT PIN");
        if( typeof dict_list != "object")
            throw new Error("Did not get a list of pins back");
        if( dict_list.length < 3)
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
        console.log(fil);
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
        console.log("INDEX CONTENT");
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
            
            console.log("Target Funk");
            console.log(this.core.net.set_value);
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


export async function run_all_tests(workerId, node, peers,data_in) {
    const worker = new WorkerHTTP(new Core(), node, peers,data_in);

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



export async function run_ipfs_tests(workerId, node, peers,data_in) {
    const worker = new WorkerHTTP(new Core(), node, peers,data_in);

    const steps = [
        worker.stage_init.bind(worker),
        worker.stage_ipfs_upload.bind(worker),
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
/*
 *
 * New Tests:
import pkg from 'hardhat';
const { ethers } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Core } from '../decelium_wallet/decelium_wallet/core.js';


async function main() {


    const core = new Core();
    const upload_path = '/nfts/sad_nft_data.ipfs';

    await core.init();
    const networkConfig = hre.network.config;
    const decPrivateKey = networkConfig.decAccounts ? networkConfig.decAccounts[0] : null;

    if (!decPrivateKey) {
        console.error('No private key found for the current network.');
        return;
    }
    const userData = await core.dw.crypto.generate_user_from_string(decPrivateKey);
    const credential_data = await core.dw.create_account({ user: userData, label: 'admin' });

    const connected = await core.initial_connect(
     'https://devdecelium.com/data/query',
        'admin'
    );

    let signed_del = await core.dw.sr({
        q: {
            'api_key': await core.dw.pubk("admin"), // update out
            'path': upload_path
        }, user_ids: ["admin"]
    });
    let del_fil = await core.net.delete_entity(signed_del);

    let pin_list = await core.net.create_ipfs({
        'api_key': await core.dw.pubk("admin"),
        'connection_settings': {
            'host': 'devdecelium.com',
            'port': '5001',
            'protocol': 'http',
            'headers': {}
        },
        'payload_type': 'local_path',
        'payload': './art/data',
        'file_type': 'ipfs'
    });

    let signed_create = await core.dw.sr({
        q: {
            'api_key': core.dw.pubk("admin"),
            'path': upload_path,
            'file_type': 'ipfs',
            'payload_type': 'ipfs_pin_list',
            'payload': pin_list
        }, user_ids: ["admin"]
    });

    let object_id = await core.net.create_entity(signed_create);

    const pinListJson = JSON.stringify(pin_list, null, 4);
    let filePath = './art/pin_list.json';
    try {
        fs.writeFileSync(filePath, pinListJson, 'utf8');
        console.log(`JSON file has been saved to ${filePath}`);
    } catch (err) {
        console.error('An error occurred while writing JSON Object to file:', err);
    }

    console.log(object_id);
    console.log("Uploading art");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error:", error);
        process.exit(1);
    });

-----

async function main() {
    const core = new Core();
    await core.init();
    const networkConfig = hre.network.config;

    const credential_data = await core.dw.create_account_from_private({ private_key: networkConfig.decAccounts[0] });
    const user_context = { 'api_key': await core.dw.pubk() };
    const upload_context = { ...user_context, 'path': '/nfts/sad_nft_data.ipfs' };
    const connected = await core.initial_connect('https://devdecelium.com/data/query');

    let del_fil = await core.net.delete_entity(await core.sr({ ...upload_context }));
    let pin_list = await core.net.create_ipfs({ ...user_context, 'payload': './art/data' });
    let signed_create = await core.sr({ ...upload_context, 'payload': pin_list, 'file_type': 'ipfs', 'payload_type': 'ipfs_pin_list' });
    let object_id = await core.net.create_entity(signed_create);

    const pinListJson = JSON.stringify(pin_list, null, 4);
    let filePath = './art/pin_list.json';
    fs.writeFileSync(filePath, pinListJson, 'utf8');
    console.log(`JSON file has been saved to ${filePath}`);
*/