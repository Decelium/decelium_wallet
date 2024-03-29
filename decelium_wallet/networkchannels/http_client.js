/* disable-eslint-disable disable-import/first */

import fetch from 'cross-fetch';
import * as ipfsClient from 'ipfs-http-client';

let fs = undefined;
let path = undefined;
let base58btc= undefined;
let encode= undefined;
let CID=  undefined;

class http_client_wrapped {
    constructor(url_version = null, api_key = null, port = null) {
        this.url_version = url_version;
        this.api_key = api_key;
        this.port = port;
    }
    
   async applyAlternateProcessing(filter, sourceId) {
        let pathVar;
        let fsVar; // Hiding from webpack's idiotic module scanner
       
        if (fs == undefined)
        {
            path = await import('path');
            fs = await import('fs');
        }
       if (sourceId === "create_ipfs" && filter.file_type === undefined) {
           filter.file_type = 'ipfs';
       }

       // Check if payload_type is not defined and payload is a string, then set payload_type to 'local_path'
       if (sourceId === "create_ipfs" && filter.payload_type === undefined && typeof filter.payload === 'string') {
           filter.payload_type = 'local_path';
       }

       // Check if payload_type is not defined and payload is an object (note: null is also considered an object in JavaScript)
       if (sourceId === "create_ipfs" && filter.payload_type === undefined && typeof filter.payload === 'object' && filter.payload !== null) {
           filter.payload_type = 'raw_file_list';
       }

        if (sourceId === "create_ipfs" && filter['file_type'] === 'ipfs' )
        {
            if (filter['payload_type'] != 'local_path' && filter['payload_type'] != 'raw_file_list')
                return {error:"only payload_type local_path and raw_file_list is accepted with create_ipfs"}
        }
        if (sourceId === "create_ipfs"  && 'file_type' in filter && filter['file_type'] === 'ipfs' && 'payload_type' in filter) {
            try {
                let itemsToAdd = [];
                if (filter['payload_type'] === 'local_path')
                    itemsToAdd = await this.loadFileData(filter['payload']);
                if (filter['payload_type'] === 'raw_file_list')
                    itemsToAdd =filter['payload'];
                    
                let connection_settings = filter.connection_settings;
                if (connection_settings == undefined) {
                    const url = new URL(this.url_version);
                    connection_settings = {
                        host: url.hostname,
                        protocol: url.protocol.slice(0, -1),
                        port: 5002
                    }
                }
                
                if (connection_settings.host == undefined) return {"error":"ipfs host must be specified in connection_settings"};
                if (connection_settings.port == undefined) return {"error":"ipfs port must be specified in connection_settings"};
                if (connection_settings.protocol == undefined) return {"error":"ipfs protocol must be specified in connection_settings"};
                if (connection_settings.headers == undefined)
                    connection_settings.headers = {};
                console.log("INSPECTING connection_settings");
                console.log(connection_settings);
                this.ipfs = ipfsClient.create(connection_settings);
                let generator = await this.ipfs.addAll(itemsToAdd, { wrapWithDirectory: true });
                let addedItems = [];

                for await (const item of generator) {
                    // For each added item, to avoid errors, painstakingly verify each file.
                    const pinResult = await this.ipfs.pin.add(item.cid);
                    let isPinned = false;
                    for await (const pin of this.ipfs.pin.ls({ paths: item.cid })) {
                        if (pin.cid.toString() === item.cid.toString()) {
                            isPinned = true;
                            break;
                        }
                    }
                    
                    if(isPinned == false)
                    {
                        console.error('Error Could not add pin to your pinning service:'+ item.cid.toString());
                        throw new Error("Could not add pin to pinning service.");                    
                    }
                    item.cid = item.cid.toString();
                    item.name = item.path.toString();
                    if (item.name == "")
                    {
                        item.root = true;
                    }
                    addedItems.push(item);

                }

                return addedItems;
            } catch (error) {
                console.error('Error adding to IPFS:', error);
                return { error: 'Error adding to IPFS:' + error.toString() }

            }
            
        } else {
            return undefined;
        }
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
            //itemsToAdd.push({
            //    path: 'root',
            //    content: Buffer.from('')  // Representing empty content for root dir
            //});            
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
                "content": fileContent,
                "root":true
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
            const digestArray = Object.values(file.cid.multihash.digest);
            const digestBytes = Uint8Array.from(digestArray);
            const mh = encode('sha2-256', digestBytes);
            const cid = CID.create(0, 112, mh);

            const cidString = cid.toString(base58btc);

            return {
                path: file.path,
                cid: cidString
            };
        });
    }





    getBasename(path) {
        return path.split('/').pop();
    } 
    
    async query(filter, source_id, {remote = false, url_version = 'dev', wait_seconds = 120, re_query_delay = 5, show_url = false}) {

        const time_start = Date.now();
        let resp = undefined;
        resp = await this.applyAlternateProcessing(filter, source_id);
        if (resp!== undefined)
        {
            return resp;
        }
        if(show_url === true)
        {
            console.log("THE RAW  QUERY()");
            console.log({source_id,url_version,filter});
        }
        while ((Date.now() - time_start) / 1000 < wait_seconds) {
            resp = await this.query_wait(filter, source_id, {remote, url_version, show_url});
            if (resp && typeof resp === 'object' && 'state' in resp && resp['state'] === 'updating') {

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
        let r = await fetch(url_version, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        let rData = "could not load";
        let dat;
        let responseData;
        let contentType = r.headers.get("content-type");        
        try {

            let rawData = await r.arrayBuffer();
            const decoder = new TextDecoder();       
            const vall = decoder.decode(rawData);
            if (contentType && contentType.includes("application/json")) {
                // Handle JSON response
                responseData = new TextDecoder().decode(rawData);
            } else if (contentType && contentType.includes("text")) {
                // Handle text response
                responseData = new TextDecoder().decode(rawData);
            } else {
                try {
                    // Try to parse as JSON
                    responseData = JSON.parse(new TextDecoder().decode(rawData));
                } catch (e) {
                    try {
                        // If JSON parsing fails, try reading as text
                        responseData = new TextDecoder().decode(rawData);
                    } catch (e) {
                        try {
                            // If text parsing fails, handle it as a Blob
                            responseData = new Blob([rawData]);
                        } catch (e) {
                            console.log("An error occurred while converting the response:", e);
                            responseData = null;
                        }
                    }
                }
            }
        } catch (e) {
            console.log("An error occurred while reading the response:", e);
            responseData = null;
        }        

        try 
        {
            dat = jsondateencode_local.loads(responseData);
        } catch (e) {
            console.log("decelium warning -- could not json decode:");
            console.log(responseData);
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

class jsondateencode_local {
    /*
    static loads(dic) {

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

        return p;
    }*/
    static loads(dic) {
        let p;
        if (typeof dic === 'string') {
            if (this.isJsonString(dic)) {
                // Use an arrow function to preserve the context of `this`
                p = JSON.parse(dic, (key, val) => this.datetime_parser(key, val));
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


function http_client(url_version = null, api_key = null, port = null) {
    const client = new http_client_wrapped(url_version, api_key, port);
    return new Proxy(client, proxyHandler);
}

export default http_client;
export {http_client};