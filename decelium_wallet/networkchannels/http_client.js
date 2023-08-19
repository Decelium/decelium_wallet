//import axios from 'axios';
import fetch from 'cross-fetch';
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
        console.log("DECODING");
        console.log(dic);
        console.log(typeof dic);
        console.log("DECODING2");
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
        console.log("DECODING3");
        console.log(p);
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

//    __run_query(q, remote = true, wait_seconds = 120, re_query_delay = 5, show_url = false) {
//        if (!('api_key' in q) || q['api_key'] === null) {
//            q['api_key'] = this.api_key;
//        }
//        return this.query(q, this.current_attr, {remote, url_version: this.url_version, wait_seconds, re_query_delay, show_url});
//    }
    __run_query(q, remote = true, wait_seconds = 120, re_query_delay = 5, show_url = false) {
        if (!('api_key' in q) || q['api_key'] === null) {
            q['api_key'] = this.api_key;
        }
        return this.query(q, this.current_attr, {remote, url_version: this.url_version, wait_seconds, re_query_delay, show_url});
    }
    
    
    async query(filter, source_id, {remote = false, url_version = 'dev', wait_seconds = 120, re_query_delay = 5, show_url = false}) {
        const time_start = Date.now();
        let resp = undefined;
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
         //    console.log("GETTING DATA3");
         //   console.log(resp);
       
        
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

        //if (show_url) {
        //    console.log("QUERY REMOTE");
        //    console.log(url_version);
        //    console.log(query);
        //    console.log(data);
        //}
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