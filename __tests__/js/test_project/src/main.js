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

let data_in = {wallet:{
                    data:"gAAAAABjnxvyiqOYNvG7-QxdW8LbxXi8kWjICnEd45cCuvB2qfIT9DlJO2uukqRwfjq-lJCYUR__Mh75NYDnMZcW-_gcibeQXQrrmIsrorqLdfDjb3nV1iKs1jHCsK25Pan1Jh5BnBv44sJudI8UjYs_cCPkxVEmlJP_qViJGOOzpcOUsBTRCjeP96z4puCLeH-wCkhptJNhQzbOiIiI9rnVDO-vOg7IY0ljr8vCZQiNzbOP0pC-n5Wz-FoCNXkmKrHNhrx1VGaaP5TZWBm6LsLrr4mJlqlcpp1kbLykoSAhs0wRf_jgdNwnZdiLhcf3v-awRqgW5tW9RDFKcHXjjayy1w3H0BmitADVGec_5QYTYjC6OE6yyjI7Du8k6eUodTlEnjmIuwR-IjiR3cbJ6ppI7BxDthDxK02IMGTe-R1wTAhlX5lVppxcxs0yqtcGal-Hrd7HI1ZiyyVYXe59uBmU5EtrmdNjfHnlCfpgk0WYyUQcEnlVinQNwtWB2FkO79uvfL6eHGTJoixXiHoig_szJVQ4mjqV59H4AGWQ4GzXe6fFRMxiwWB5cAlbX4NkAJe1TGOyIxHQI2UstGF7MHcXnLPazD78jriUgVvsyqqTE4Y7FTkWyJvibzWycQ4bznp_cLsfzjOw77Gx1r_VTJZGMF8EYsDaiFAzCHKIFwlO2ZY0h-99j5Ikrqk4v0qtyQiUH1aX5Y78Xmxk2DzyWxqdvEbzVkyhWJMKEZKlp0J7gLngZ_8VKQK0YCipoeo4nI8hQITgdksDuKSdqmbJp5m62XFYHwo4eh6kiKLxsnw12DAr6QdGEgfuUhAlmpRKIktrODq8s-R2sSqsxSgwyrov3Jfqqwh0zmsAXwSFHXvdxETxQhjDSnkbc6vCx_SQ1PAHK9ahyubo-b6DT1Y1pJIlzmAx98n5aww3lpkN_L9NL7iTFaCCF1Gxbt9AxIdfJZmrDZyghWXHuAJZT-tFeQqQe2RqHIZiBhNHXFnAvc1B1VLeioUeszFxGHyv0PunD_Pq6x918CH3v_dMZUpHNrdeR7LFKT6nC_5n_27ufA4bUe3WqXAsnDLNC-MIFTx8GYmkgqmP19u9dyWolEyPKVQW0gLT3ffWrLyfy5zQ2MnvyXOxwVhtMVs9J_zLRoAYPxCy9_VGt4fZhds1jkSCX1IIrfmfPgyCeuYga2X7MHWTpUGUfX3d8_I6T5gQ0GDlkEYzEZbZYBPULiaxgRlYUSiLV-w8HkUXDKz7L6LQojWEzmK0jXPKZlazmInVL1cNJyKEXd-Bmiuho0JufKeI0sB5JMlOfDWosrIIDD08bgH3HsY2ZnpavUDAlO-UO0tPnoAnMjWUEjTUN6yT5AO_MoTmLof1_tkxIqq7lSgO9nTEXxo62cqBoz3ekxbiyxABvlmAAnZPjYFgjVeye_qZKb1HDzUwnEBkrIxHbT2klwId3uOsPvldhttA9Atg-fSg50RBnJlxsTm0jZNNbE3Jrp4QWsws_y9VwsHwnfPI0tFf3C_yy82hsmIZEfJ0t_uRMxAqmQkuU2TTlZx4d1olb0Sbn1v_RaSa6WWV3Z2MmjvkL0oYRd1BXZRB6uWEejaFZiJaL0D9cNx5RCfOX3Fe1pYhIcUh9KpYnlX9BEns1RcmYY_U6SUZI4ayV7TwlGRlInsvXvTQwX2CNIQvPTvbEVfcWD-rH8LlzABuilGtPYSUtssZkw9oRVbWpM7PKNW94zgo6wpzPFQ_-8gDmlxgaOmmIMSlhuBiOV6cpXLV-UuglQdUA17Ic-w_1PiJ57cFhM8g7YZzsjoaNvg0cflaf8QCCgFXdZCJz3A4cG6toSXL35muu5dbfSeNaLS2VHcy46xlGFoyrBn-AuC3aRAjutirGLJK_NEo6_j3VoinUvOTCFiR_pgNJOVpdk-Vh9DHBdycWIlIHHLjvR5WgZ3Gcq48fAXRpx3yoh6TAvnN9Z-Lz0Pd522jUUICfwUVzpraQBz4Y1Wb3d4_Fvv2vnyZgTDAISmPf8YuK9TkLas3X2LgY_yVNwQ2ssmH-kKB1dAZTu2EtqoabcZczXJ4qHdQSROiBhT1MEfDORlCsP7TjSEZJrxkS61r6NZOmieqo2ayE-APLkHyeqWt1dkqt_KzSJYV6MuFIJuDm8Z8bNU-wS7riViLI4izRlAV6a3CPU4rb1NUU5UqNOBpg0h_3gzyNi3H9urFrioM_t6-_t2wIn3CSEQMXC5oq0De6xaBRVUMeRfkyovK7om_cnK2pcWIFNr4yFcKvHUYA5zWouA7De-bOK4D9eF7GFw7PfttAcASh6Rx6aZjewEdHb0cpPcjUu33rTe41-KqjkLLGieeUi05slpKNemLda1AtkVUubL1uQQOON4mZ59K238AtUJBOptXjtBsjWSEkITauMrLkpMR2XmWTTsMx8zyufhGt5wJ6e4r5y6gbo3JDjnAQLMNCbG372cpHB0tK3-ESrJKcjla99qMuPNCrzFQ91BbUnOPwIzISsBk3fhpKnD2FntTpuN7nm7GKxd8l6KLUcYex2P0aXXu6xMK2eimUS9GdPFIMJokaJnRuaK6MCxtfA2YcB_Q5VuiQwfPddvqTyBGuUZYKjHIwI16PRonVwtnfNSVvGWdCu42_q3VdOrdeOUL4FSY0Mzf2_RNHQA-cCEt5kEfBNwLZsrhUw9rebgLIGzXb28SHuQkEESm1K9PyxLQIPZX18HSAe2bF9e93w5k-FqR6psQAw_9hHNuNsUG_9HxoDynCsFUJUwoKhkJJwqYzbWDIK_ugHxHEUq6QEGoEkHVAEbzwPS9Y-A=",
                    password:"Masterblastermastersystem1"
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