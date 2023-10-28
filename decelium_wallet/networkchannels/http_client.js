//import axios from 'axios';
import fetch from 'cross-fetch';
import * as IPFS from 'ipfs-core';
let fs = undefined;
let path = undefined;
let base58btc= undefined;
let encode= undefined;
let CID=  undefined;
//const ipfs = await IPFS.create()

//node worker_http.js 1 > debug.txt

/*
class jsondateencode_local {
    static loads(dic) {
        console.log("DECODING");
        console.log(dic);
        console.log("DECODING2");
        let p =  JSON.parse(dic, this.datetime_parser);
        console.log("DECODING3");

    }

    static dumps(dic) {
        return JSON.stringify(dic, this.datedefault);
    }

    static datedefault(key, val) {
        if (Array.isArray(val) && val[0] === '__ref') {
            return ['__ref', ...val.slice(1)];
        }
        if (val instanceof Date) {
            return val.toISOString();
        }
        return val;
    }

    static datetime_parser(key, val) {
        if (typeof val === 'string' && val.includes('T')) {
            const date = moment(val, 'YYYY-MM-DDTHH:mm:ss', true);
            if (date.isValid()) {
                return date.toDate();
            }
        }
        return val;
    }
}*/

class jsondateencode_local {
    static loads(dic) {
        //console.log("DECODING");
        //console.log(dic);
        //console.log(typeof dic);
        //console.log("DECODING2");
        let p;
        if (typeof dic === 'string') {
            if (this.isJsonString(dic)) {
                p = JSON.parse(dic, this.datetime_parser);
            } else if (!isNaN(dic)) {
                p = Number(dic);
            } else {
                p = dic;
            }
        } else if (typeof dic === 'object') {
            p = this.datetime_parser('', dic);
        }
        else
        {
            p = dic;
        }
        //console.log("DECODING3");
        //console.log(p);
        return p;
    }

    static isJsonString(str) {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }

    static dumps(dic) {
        return JSON.stringify(dic, this.datedefault);
    }

    static datedefault(key, val) {
        if (Array.isArray(val) && val[0] === '__ref') {
            return ['__ref', ...val.slice(1)];
        }
        if (val instanceof Date) {
            return val.toISOString();
        }
        return val;
    }

    static datetime_parser(key, val) {
        if (typeof val === 'string' && val.includes('T')) {
            const date = new Date(val);
            if (!isNaN(date)) {
                return date;
            }
        } else if (typeof val === 'object') {
            for (let k in val) {
                val[k] = this.datetime_parser(k, val[k]);
            }
        }
        return val;
    }
}




class http_client_wrapped {
    constructor(url_version = null, api_key = null, port = null) {
        this.url_version = url_version;
        this.api_key = api_key;
        this.port = port;
        
    }

    __run_query(q, remote = true, show_url = false) {
        let wait_seconds = 120; 
        let re_query_delay = 5;
        if (!('api_key' in q) || q['api_key'] === null) {
            q['api_key'] = this.api_key;
        }
        return this.query(q, this.current_attr, {remote, url_version: this.url_version, wait_seconds, re_query_delay, show_url});
    }
    
    async loadFileData (path_in) {
        //let itemsToAdd = [];
        // This function will get all the files recursively from a directory
        const getFilesRecursive = (dir) => {
            let results = [];
            const list = fs.readdirSync(dir);
            list.forEach((file) => {
                const filePath = path.join(dir, file);
                const stat = fs.statSync(filePath);
                if (stat && stat.isDirectory()) {
                    results = results.concat(getFilesRecursive(filePath));
                } else {
                    results.push(filePath);
                }
            });
            return results;
        };

        let itemsToAdd = [];
        if (fs.statSync(path_in).isDirectory()) {
            const allFiles = getFilesRecursive(path_in);
            for (const filePath of allFiles) {
                const relativePath = path.relative(path_in, filePath);
                const fileContent = fs.readFileSync(filePath);
                itemsToAdd.push({
                    path: relativePath,
                    content: fileContent
                });
            }
        } else {
            const fileContent = fs.readFileSync(path_in);
            itemsToAdd.push({
                "path": this.getBasename(path_in),
                "content": fileContent
            });
        }    
        return itemsToAdd;
    }


    async convertFilesToDicts(files) {
        if(base58btc == undefined)
        {
            let base58Module = await import('multiformats/bases/base58');
            let digestModule = await import('multiformats/hashes/digest');
            let cidModule = await import('multiformats/cid');

            base58btc = base58Module.base58btc;
            encode = digestModule.encode;
            CID = cidModule.CID;
        }
        return files.map(file => {
            // Convert the digest object to Uint8Array
            const digestArray = Object.values(file.cid.multihash.digest);
            const digestBytes = Uint8Array.from(digestArray);

            // Create the multihash and then the CID
            const mh = encode('sha2-256', digestBytes);
            const cid = CID.create(0, 112, mh);

            // Convert the CID to a base58-encoded string
            const cidString = cid.toString(base58btc);

            return {
                path: file.path,
                cid: cidString
            };
        });
    }



    
   async applyAlternateProcessing(filter, sourceId) {
        if (fs == undefined)
        {
            path = await import('path');
            fs = await import('fs');
        }
        if (sourceId === "create_ipfs" 
            && 'file_type' in filter && filter['file_type'] === 'ipfs' 
            && 'payload_type' in filter && filter['payload_type'] === 'local_path') {
            
            console.log("PROCESSING IPFS IN PaxFinancialAPI-------------------------------");
            console.log(filter['payload']);
            console.log(this.getBasename(filter['payload'])); 
            
            //const api = IPFS.create({ 
            //    host: '35.167.170.96', 
            //    port: '5001', 
            //    protocol: 'http',
            //});
            const api = await IPFS.create({url: "http://35.167.170.96:5001/api/v0" });
  
            let itemsToAdd = await this.loadFileData(filter['payload']);

            try {
                let generator = await api.addAll(itemsToAdd);
                let addedItems = [];

                for await (const item of generator) {
                    item.cid = item.cid.toString();
                    addedItems.push(item);

                }
                return addedItems;
            } catch (error) {
                console.error('Error adding to IPFS:', error);
                return undefined;
            }
        } else {
            return undefined;
        }
    }

    getBasename(path) {
        return path.split('/').pop();
    } 
    
    async query(filter, source_id, {remote = false, url_version = 'dev', wait_seconds = 120, re_query_delay = 5, show_url = false}) {

        
        const time_start = Date.now();
        let resp = undefined;
        resp = await this.applyAlternateProcessing(filter, source_id);
        if (resp!= undefined)
        {
            return resp;
        }
        
        while ((Date.now() - time_start) / 1000 < wait_seconds) {
            resp = await this.query_wait(filter, source_id, {remote, url_version, show_url});
            if (resp && typeof resp === 'object' && 'state' in resp && resp['state'] === 'updating') {
                //console.log(filter);
                //console.log(resp);
                //console.log('.');
                await new Promise(resolve => setTimeout(resolve, re_query_delay * 1000));
                if ('force_refresh' in filter) {
                    delete filter['force_refresh'];
                }
            } else {
                break;
            }
        }
        if(show_url === true)
        {
            console.log("RETURN FROM QUERY()");
            console.log(resp);
        }
        return resp;
    }

    async query_wait(filter, source_id, {remote = false, url_version = 'dev', show_url = false}) {
        
        if ('__encoded_query' in filter) {
            let dic = this.do_decode(filter['__encoded_query']);
            filter = {...filter, ...dic};
            delete filter['__encoded_query'];
        }

        if ([true, 'http', 'https'].includes(remote)) {
            let resp = await this.query_remote(source_id, filter, url_version, show_url);
            
            return resp;
        }
        return null;
    }

    async query_remote(source_id, query, url_version = 'dev', show_url = false) {
        
        let data = {};
        data['qtype'] = source_id;
        data['__str_encoded_query'] = this.do_encode_string(query);

        if (show_url) {
            console.log("show_url QUERY REMOTE");
            console.log(url_version);
            console.log(query);
            console.log(data);
        }
        //console.log('query_remote----------------------');
        //console.log(url_version);
        //console.log(data);
        //console.log(query);
        /*
        let r = await axios.post(url_version, data);
        //console.log("query_remote_data",r.data);
        let dat;

        try 
        {
            dat = jsondateencode_local.loads(r.data);
        
        } catch (e) {
            console.log(e);
            dat = r.data;
        }
        */
        let r = await fetch(url_version, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        let rData = "could not load";
        let dat;
        try {
            let rText = await r.text();
            try {
                if (show_url) {
                    console.log("show_url return text:");
                    console.log(rText);
                }
                
                rData = JSON.parse(rText);
            } catch (e) {
                console.log("Response is not JSON:", e);
                rData = rText;
                console.log("data",rData);
            }
            dat = rData;
        } catch (e) {
            console.log("An error occurred while reading the response:", e);
        }       

        try 
        {
            dat = jsondateencode_local.loads(rData);
        } catch (e) {
            console.log(e);
            dat = rData;
        }        
            
        if (show_url) {
            console.log("show_url return val:");
            console.log(dat);
        }
        
        return dat;
        
    }

    do_encode(request_obj) {
        return false;
    }

    do_decode(data_packet) {
        return false;
    }

    do_encode_string(obj) {
        let string = JSON.stringify(obj);
        let encoded = btoa(string);
        return encoded;
    }

    do_decode_string(data_packet) {
        let user_data_dev = atob(data_packet);
        let data2 = JSON.parse(user_data_dev);
        return data2;
    }


}


    
const proxyHandler = {
    get: function(target, propKey) {
        if (typeof target[propKey] === 'function') {
            return target[propKey];
        } else {
            target.current_attr = propKey;
            return target.__run_query.bind(target);
        }
    }
};

function http_client(url_version = null, api_key = null, port = null) {
    const client = new http_client_wrapped(url_version, api_key, port);
    return new Proxy(client, proxyHandler);
}

export default http_client;
export {http_client};