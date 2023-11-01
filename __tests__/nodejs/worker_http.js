import {run_ipfs_tests,run_all_tests} from './worker_http_core.js';

if (!process.argv[2] || !process.argv[3] || !process.argv[4]) {
    console.error('Required arguments not provided');
    process.exit(1);
}

console.log('running ' + process.argv[2] + ' on ' + process.argv[3]);
const workerId = parseInt(process.argv[2]);
const node = process.argv[3];
const peers = JSON.parse(process.argv[4]);

run_ipfs_tests(workerId, node, peers).catch(e => console.error(e));


//run_all_tests(workerId, node, peers).catch(e => console.error(e));
//} node ./nodejs/worker_http.js 1 dev.paxfinancial.ai "[]"
// node ./worker_http.js 1 dev.paxfinancial.ai "[]"