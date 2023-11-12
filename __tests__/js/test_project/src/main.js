import { helloWorld } from './hello';
import Core from "../../../../decelium_wallet/core.js";
import {run_ipfs_tests,run_all_tests} from '../../../../__tests__/nodejs/worker_http_core.js';

let upload_files = undefined;
document.getElementById('directory').addEventListener('change', async function() {
    const filesData = [];

    for (let file of this.files) {
        const buffer = await readFileAsBuffer(file);
        const splitPath = file.webkitRelativePath.split('/');
        // Remove the first element (the directory name)
        splitPath.shift();
        // Join the remaining parts back into a string
        const newPath = splitPath.join('/');
        console.log('Selected file from directory:', newPath);
                
        
        filesData.push({
            path: newPath,
            content: buffer
        });
    }
    
    // Now you can pass `filesData` to ipfs.addAll
    console.log(filesData);
    upload_files = filesData;
    // Example: await ipfs.addAll(filesData);
});

function readFileAsBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(event) {
            resolve(new Uint8Array(event.target.result));
        };
        reader.onerror = function(error) {
            reject(error);
        };
        reader.readAsArrayBuffer(file);
    });
}



function trigger_upload()
{
// FILL IN WALLET DATA!
let data_in = {wallet:{
                    data:"",

                    password:""
                }};
    
    data_in["files"] = upload_files;
    run_ipfs_tests("1", "dev.paxfinancial.ai", "[]",data_in).catch(e => console.error(e));

//console.log(run_ipfs_tests);
//if (!process.argv[2] || !process.argv[3] || !process.argv[4]) {
//    console.error('Required arguments not provided');
//    process.exit(1);
//}
//console.log('running ' + process.argv[2] + ' on ' + process.argv[3]);
//const workerId = parseInt(process.argv[2]);
//const node = process.argv[3];
//const peers = JSON.parse(process.argv[4]);
//run_ipfs_tests(workerId, node, peers).catch(e => console.error(e));
document.getElementById('hello-message').innerText = helloWorld();

}


document.addEventListener('DOMContentLoaded', (event) => {
    let uploadButton = document.querySelector('button');
    uploadButton.addEventListener('click', trigger_upload);
});

/*
54.187.82.133/:1 Access to fetch at 'http://35.167.170.96:5001/api/v0/add?stream-channels=true&wrap-with-directory=true&progress=false' from origin 'http://54.187.82.133:5000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
*/
