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
    /*
    async load_wallet_strings_from_disk() {
        for (const root of ['./', '../', '../../', '../../../', '../../../../']) {
            try {
                const password = await fs.readFile(root + '.password', 'utf-8');
                const walletstr = await fs.readFile(root + '.wallet.dec', 'utf-8');
                return {
                    password: password.trim(),
                    data: walletstr.trim(),
                };
            } catch (err) {
                // ignore errors
            }
        }
        return { error: 'could not find .password and .wallet.dec in parent path' };
    }*/
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
        //console.log ("FINISHED INIT");
        //console.log (this.core.pyodide);
        const raw_wallet = await this.load_wallet_strings_from_disk();
        //console.log ("disk");
        if (raw_wallet.error)
            throw new Error('Failed to load wallet fron disk: '+raw_wallet.error);
            
        const success = this.core.load_wallet(raw_wallet.data, raw_wallet.password);
        //console.log('success', success);
        if (success !== true) {
            throw new Error('Failed to load wallet');
        }

        const connected = await this.core.initial_connect(
            'https://'+this.node_address+'/data/query',
            'test_user'
        );
        if (connected !== true) {
            throw new Error('Failed to connect');
        }
        //console.log(this.core.dw.get_raw())
        return true;
    }

    async stage_broadcast() {
        //return true;
        const mimi = new MiniGetterSetter();

        const port = 5003 + parseInt(workerId);
        const name = 'node-session-file-' + workerId + '.node';
        const public_handlers = [
            ['set_value', mimi.set_value.bind(mimi)],
            ['get_value', mimi.get_value.bind(mimi)],
            ['get_all', mimi.get_all.bind(mimi)],
            ['do_echo', (args) => args],
        ];

        const resp = await this.core.listen(port, name,"test_user", public_handlers);
        console.log("Listening");
        await new Promise(resolve => setTimeout(resolve, 10000));
        console.log("Done");
        return resp;
    }
    /*
    #############################
    ###
    ###  3. List all remote nodes. Ensure you can connect
    ###
    def stage_list_nodes(self):
        time.sleep(0.5)
        nodes = self.core.node_list()
        found = False
        count = 0
        for n in nodes:            
            if n['self_id'] == self.core.self_id:
                print ("found self")
                found = True
            else:
                if 'test_id' in n['connect_data']['meta']:
                    count = count + 1
                    print("py passed inspection" + n['self_id'] )
        try:
            assert len(self.peer_ids) == count
        except Exception as e:
            print("self.peer_ids",len(self.peer_ids))
            print("count",count)
            pprint(nodes)
            raise e
        return found    
    
    */
    /*
    async stage_list_nodes() {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const nodes = await this.core.node_list();
        let found = true; // True until we implement broadcast

        for (const n of nodes) {
            if (n.self_id === this.core.self_id) {
                console.log('found self');
                found = true;
            } else {
                let x = 0;
                if ('test_id' in n.connect_data.meta) {
                    console.log('js passed inspection' + x.toString()+n.self_id);
                }
            }
        }

        return found;
    }*/
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
            connect_data.api_key = this.core.dw.pubk('test_user');
            const sid = await this.core.net.connect(
                connect_data,
                this.core.handle_connection.bind(this.core)
            );

            const val = uuidv4();
            
            console.log("Target Funk");
            console.log(this.core.net.set_value);
            const respset = await this.core.net.set_value(
                {
                    api_key: this.core.dw.pubk('test_user'),
                    key: 'test' + workerId,
                    val,
                },
                { session_id: sid }
            );
            const respget = await this.core.net.get_value(
                {
                    api_key: this.core.dw.pubk('test_user'),
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

/*

def run_all_tests(worker_id,node,peers):
    
    worker = WorkerHTTP(core(),node,peers)
    
    steps = [
        worker.stage_init,
        worker.stage_broadcast,
        worker.stage_list_nodes,
        worker.stage_set,
        worker.stage_verify,
        worker.stage_shutdown,
    ]

    results = []
    for i, step in enumerate(steps):
        print(step)
        print("----------------------------------------------------------")
        print(f"[{i}] Worker {worker_id}: {step.__name__}")
        result = False
        try:
            result = step()
        except Exception as e:
            import traceback as tb
            result = tb.format_exc()
            try:
                print("forcing shutdown . . .", end="")
                worker.stage_shutdown()
                print(" done")
            except:
                pass
        print(f"worker_http.py_{worker_id}: Step {step.__name__} {'succeeded' if result else 'failed'}")
        if not result == True:
            raise Exception(f"[{i}] Worker {worker_id}: {step.__name__}"+str(result))
        if result != True:
            break
            
if __name__ == "__main__":
    print("running "+str(sys.argv[1])+" on "+sys.argv[2])
    worker_id = int(sys.argv[1])
    node = sys.argv[2]
    peers = json.loads(json.loads(sys.argv[3]))
    
    run_all_tests(worker_id,node,peers)
*/



/*
async function run_all_tests() {
    const worker = new WorkerHTTP(new Core());

    const steps = [
        worker.stage_init.bind(worker),
        worker.stage_broadcast.bind(worker),
        worker.stage_list_nodes.bind(worker),
        worker.stage_set.bind(worker),
        //worker.stage_verify.bind(worker),
        worker.stage_shutdown.bind(worker),
    ];

    const results = [];
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        console.log(`----------------------------------------------------------`);
        console.log(`[${i}] Worker ${workerId}: ${step.name}`);

        let result = false;
        try {
            result = await step();
        } catch (err) {
            console.error(err);
        }

        if (result !== true) {
            console.log(result);
        }
        results.push(result);
        console.log(`worker_http.js_${workerId}: Step ${step.name} ${result ? 'succeeded' : 'failed'}`);

        if (result !== true) {
            break;
        }
    }

    await fs.writeFile(`worker${workerId}_output.txt`, results.join('\n'));
}

//if (require.main === module) { THIS CAUSED BUGS
console.log('running ' + process.argv[2]);
const workerId = parseInt(process.argv[2]);
run_all_tests();
//}
*/



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

//if (require.main === module) {
if (!process.argv[2] || !process.argv[3] || !process.argv[4]) {
    console.error('Required arguments not provided');
    process.exit(1);
}

console.log('running ' + process.argv[2] + ' on ' + process.argv[3]);
const workerId = parseInt(process.argv[2]);
const node = process.argv[3];
const peers = JSON.parse(process.argv[4]);

run_all_tests(workerId, node, peers).catch(e => console.error(e));
//} node ./nodejs/worker_http.js 1 dev.paxfinancial.ai "[]"
