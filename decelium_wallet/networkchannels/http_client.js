import axios from 'axios';
import moment from 'moment';

class jsondateencode_local {
    static loads(dic) {
        return JSON.parse(dic, this.datetime_parser);
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
        while ((Date.now() - time_start) / 1000 < wait_seconds) {
            let resp = await this.query_wait(filter, source_id, {remote, url_version, show_url});
            if (resp && typeof resp === 'object' && 'state' in resp && resp['state'] === 'updating') {
                console.log(filter);
                console.log(resp);
                console.log('.');
                await new Promise(resolve => setTimeout(resolve, re_query_delay * 1000));
                if ('force_refresh' in filter) {
                    delete filter['force_refresh'];
                }
            } else {
                break;
            }
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
        data['__str__encoded_query'] = this.do_encode_string(query);

        if (show_url) {
            console.log(url_version);
            console.log(query);
        }

        let r = await axios.post(url_version, data);
        let dat;

        try 
        {
            dat = jsondateencode_local.loads(r.data);
        
        } catch (e) {
            console.log(e);
            dat = r.data;
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