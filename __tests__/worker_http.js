// WorkerHTTP.js
import { Core } from '../decelium_wallet/core.js';
import { MiniGetterSetter } from './MiniGetterSetter.js';
import fs from 'fs/promises';
import process from 'process';

class WorkerHTTP {
    constructor(core) {
        this.core = core;
    }

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
    }

    async stage_init() {
        await this.core.init();
        console.log ("FINISHED INIT");
        //console.log (this.core.pyodide);
        const raw_wallet = await this.load_wallet_strings_from_disk();
        const success = this.core.load_wallet(raw_wallet.data, raw_wallet.password);
        console.log('success', success);
        if (success !== true) {
            throw new Error('Failed to load wallet');
        }

        //const connected = await this.core.initial_connect(
        //    'https://dev.paxfinancial.ai/data/query',
        //    'admin'
        //);
        //if (connected !== true) {
        //    throw new Error('Failed to connect');
        //}
        console.log(this.core.dw.get_raw())
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

        const resp = await this.core.listen(port, name, public_handlers);
        return resp;
    }

    async stage_list_nodes() {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const nodes = this.core.node_list();
        let found = false;

        for (const n of nodes) {
            if (n.self_id === this.core.self_id) {
                console.log('found self');
                found = true;
            } else {
                if ('test_id' in n.connect_data.meta) {
                    console.log('passed inspection' + n.self_id);
                }
            }
        }

        return found;
    }

    async stage_set() {
        this.sessions = [];
        for (const peer_connect_data of this.core.node_peers()) {
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

async function run_all_tests() {
    const worker = new WorkerHTTP(new Core());

    const steps = [
        worker.stage_init.bind(worker),
        //worker.stage_broadcast.bind(worker),
        //worker.stage_list_nodes.bind(worker),
        //worker.stage_set.bind(worker),
        //worker.stage_verify.bind(worker),
        //worker.stage_shutdown.bind(worker),
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

//if (require.main === module) {
console.log('running ' + process.argv[2]);
const workerId = parseInt(process.argv[2]);
run_all_tests();
//}

