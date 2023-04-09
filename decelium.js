import cryptoContent from './decelium_wallet/crypto.py.js';
import deceliumContent from './decelium_wallet/decelium.py.js';
import walletContent from './decelium_wallet/wallet.py.js';

function Decelium(url_version,api_key_in) {
    this.url_version = url_version;
    this.api_key = api_key_in;
}
Decelium.prototype.query = async function(query_name,query_in,callback)  {
    let url = this.url_version+'/data/query';
    let req = { qtype: query_name, api_key: query_in.api_key };
    req['__str_encoded_query'] =JSON.stringify(query_in);
    var encodedString = btoa(req['__str_encoded_query']);
    encodedString  = encodeURIComponent(encodedString);
    // ret_dat = {error:'jquery request failed'}
    req['__str_encoded_query'] = encodedString;
    let ret = {};

    let dat = await fetch(url +"?" + new URLSearchParams(req), {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
        }        
    });
    let txt = await dat.text();
    if (callback != undefined) 
        callback(txt);
    return txt;
}


/**
*
*  Base64 encode / decode
*  http://www.webtoolkit.info/
*
**/
var Base64 = {
    // private property
    _keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    // public method for encoding
    encode : function (input) {
        var output = "";
        var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        var i = 0;

        input = Base64._utf8_encode(input);
        while (i < input.length) {

            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);

            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;

             if (isNaN(chr2)) {
               enc3 = enc4 = 64;

            } else if (isNaN(chr3)) {
                enc4 = 64;
            }

            output = output +
            this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
            this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
        }
        return output;
    },
    // public method for decoding
    decode : function (input) {
        var output = "";
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;
        var i = 0;
        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        while (i < input.length) {
            enc1 = this._keyStr.indexOf(input.charAt(i++));
            enc2 = this._keyStr.indexOf(input.charAt(i++));
            enc3 = this._keyStr.indexOf(input.charAt(i++));
            enc4 = this._keyStr.indexOf(input.charAt(i++));
            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;
            output = output + String.fromCharCode(chr1);
            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }
        }
        output = Base64._utf8_decode(output);
        return output;
    },
    // private method for UTF-8 encoding
    _utf8_encode : function (string) {
        var utftext = "";
        for (var n = 0; n < string.length; n++) {
            var c = string.charCodeAt(n);
            if (c < 128) {
                utftext += String.fromCharCode(c);
            }
            else if((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            }
            else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }
        }
        return utftext;
    },
    // private method for UTF-8 decoding
    _utf8_decode : function (utftext) {
        var string = "";
        var i = 0;
        var c = c1 = c2 = 0;
        while ( i < utftext.length ) {
            c = utftext.charCodeAt(i);
            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            }
            else if((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i+1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            }
            else {
                c2 = utftext.charCodeAt(i+1);
                c3 = utftext.charCodeAt(i+2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        }
        return string;
    }

}




class wallet {
    //constructor() {}
    constructor() {
        const wi = "test123";
        wallet.pyodide.runPython(wi+`= wallet.wallet()`);        
        const wallet_methods = ['create_account','load','get_raw'];
        wallet_methods.forEach(method=>
                this[method] = (args) => {
                            if (!args)
                                args={};
                            let argString = '('; 
                            for ( const key in args ) {
                                argString=argString+key+'="'+args[key]+'",';
                            }
                            argString=argString+'format="json")';
                            console.log(argString);
                            let result = wallet.pyodide.runPython(wi+`.`+method+argString);
                            return JSON.parse(result); 
                          } 
            );
        
    }
}


class decelium_wallet {
    
    static async init() {
        //console.log("cryptoContent");
        //console.log(cryptoContent);
        //console.log("cryptoContent2");
        
        this.crypto = {};
        this.commands = {};
        this.wallet = wallet;
        this.pyodide = await window.loadPyodide({indexUrl: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"});
        this.wallet.pyodide = this.pyodide;
        console.log(this.pyodide);
        this.pyodide.globals.set("cryptoContent", cryptoContent);
        this.pyodide.globals.set("deceliumContent", deceliumContent);
        this.pyodide.globals.set("walletContent", walletContent);        
        await this.pyodide.runPythonAsync(`
        import codecs
        crypto_bytes = codecs.encode(cryptoContent, 'utf-8')
        decelium_bytes = codecs.encode(deceliumContent, 'utf-8')
        wallet_bytes = codecs.encode(walletContent, 'utf-8')

        with open("crypto.py", "wb") as f:
            f.write(crypto_bytes)
        with open("decelium.py", "wb") as f:
            f.write(decelium_bytes)
        with open("wallet.py", "wb") as f:
            f.write(wallet_bytes)
            
        with open("crypto.py", "r") as f:
            content = f.read()
        print(content)            
        `);      
        await this.pyodide.loadPackage("micropip");
        await this.pyodide.runPythonAsync(`
        import micropip
        micropip.INDEX_URL = 'https://pypi.org/simple'
        `);        
        const micropip = this.pyodide.pyimport("micropip");
        await micropip.install('requests');
        await micropip.install('ecdsa');
        await micropip.install('cryptography');
        this.pyodide.runPython(`
        import crypto
        import wallet
        `); 
        const crypto_methods = ['getpass','do_encode_string','do_decode_string',
            'generate_user','generate_user_from_string',
            'sign_request','verify_request',
            'decode','encode','encode_key','decode_key'];
        crypto_methods.forEach(method=>
                this.crypto[method] = (args) => {
                            if (!args)
                                args={};
                            let argString = '('; 
                            for ( const key in args ) {
                                argString=argString+key+'="'+args[key]+'",';
                            }
                            argString=argString+'format="json")';
                            console.log(argString);
                            let result = this.pyodide.runPython("crypto.crypto."+method+argString);
                            return JSON.parse(result); 
                          } 
            );
        const commands = [{
            name: "generate_a_wallet",
            argList: ["wallet_path"],
            optionalArgList: []
        },{
            name: "generate_user",
            argList: ["wallet_path", "wallet_user"],
            optionalArgList: ["confirm"]
        },{
            name: "check_balance",
            argList: ["wallet_path","wallet_user","url_version"],
            optionalArgList: []
        },{
            name: "create_user",
            argList: ["wallet_path","wallet_user","dec_username","url_version"],
            optionalArgList: ["password"]
        },{
            name: "delete_user",
            argList: ["wallet_path","wallet_user","dec_username","url_version"],
            optionalArgList: []
        },{
            name: "display_wallet",
            argList: ["wallet_path"],
            optionalArgList: []
        },{
            name: "download_entity",
            argList: ["wallet_path","wallet_user","url_version","root_directory"],
            optionalArgList: []
        },{
            name: "list_account",
            argList: ["wallet_path","wallet_user","url_version","root_directory"],
            optionalArgList: []
        },{
            name: "fund",
            argList: ["wallet_path","wallet_user","url_version"],
            optionalArgList: []
        },{ name: "secret",
            argList: ["wallet_path","wallet_user","command"],
            optionalArgList: ["secret_id","secret_value"]
        },{ name: "deploy",
            argList: ["wallet_path", "wallet_user", "url_version", "source_dir", "dest_path"],
            optionalArgList: ["dns_host", "dns_secret_location"] 
        },{
            name: "deploy_dns",
            argList: ["wallet_path", "wallet_user", "url_version", "target_id", "dns_host"],
            optionalArgList: []
        } ];
        /*
        for (const command of commands) {
            await this.pyodide.runPythonAsync(`
                response = await pyfetch("../../decelium_wallet/commands/${command.name}.py")
                with open("${command.name}.py", "wb") as f:
                    f.write(await response.bytes())
                    print("Wrote ${command.name}.py")
            `);
            this.commands[command.name] = {}
            this.commands[command.name]["run"] = (args) => {
                if (!args)
                    args={};
                let argString = '(';
                command.argList.forEach(arg=>{
                    if (arg in args) {
                        argString = argString +'"'+args[arg]+'",';
                    } else {
                        argString = argString + 'None,'; 
                    }
                });   
                command.optionalArgList.forEach(arg=>{
                    if (arg in args) {
                        argString = argString +'"'+args[arg]+'",';
                    }
                });                
                argString = argString+')';
                console.log(argString);
                this.pyodide.runPython("import json");
                this.pyodide.runPython("import "+command.name);
                let runString = "json.dumps("+command.name+".run"+argString+")";
                let result = this.pyodide.runPython(runString);
                if (result!=undefined) 
                     return JSON.parse(result);
                    
            }
        }*/
        /*
        const class_commands = [
            { name: "secret",
              argList: ["wallet_path","wallet_user","command"],
              optionalArgList: ["secret_id","secret_value"]
            }
        ];
        class_commands.forEach(command=>{
            this.commands[command.name] = {};
            this.commands[command.name]["Deploy"] = () => {
                let self = {};
                self.run = (args) => {
                    if (!args)
                        args = {};
                    let argString='(';
                    command.argList.forEach(arg=>{
                        if (arg in args) {
                            argString = argString +'"'+args[arg]+'",';
                        } else {
                            argString = argString + 'None,'; 
                        }
                    });
                    command.optionalArgList.forEach(arg=>{
                        if (arg in args) {
                            argString = argString +'"'+args[arg]+'",';
                        }
                    });
                    argString = argString+')';
                    console.log(argString);
                    this.pyodide.runPython("import "+command.name);
                
                }
            }        
        });
        */
        
            
            
    } 
        
    async fetching() {
        let encoded_string=this.pyodide.runPython(`
            print(dir(crypto.crypto))
            crypto.crypto.do_encode_string("abcd")
        `);
        console.log(encoded_string);
        
        let result_json=this.pyodide.runPython(`
import json
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()
json.dumps({
      'private_key': private_key.private_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PrivateFormat.PKCS8,
          encryption_algorithm=serialization.NoEncryption()
      ).hex(),
      'public_key': public_key.public_bytes(
          encoding=serialization.Encoding.PEM,
          format=serialization.PublicFormat.SubjectPublicKeyInfo
      ).hex()
  })`);
        console.log(JSON.parse(result_json));  
        
        return this.pyodide.runPython(`dir(crypto)`);
    }
    
    async calculate(){
        let pyodide = await window.loadPyodide({indexUrl: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js"});
        ///await pyodide.loadPackage(['cryptography'])
        //await pyodide.loadPackage(['json'])
        ///let pkg1 = pyodide.pyimport("cryptography");
        ///console.log(pyodide.runPython("import cryptography"));
        console.log(pyodide.runPython("print('Hello world!!')"));
        
        console.log(pyodide.runPython("1 + 2"));
        return pyodide.runPython("1+2");
    }
}



/*
PYTHON:
class Self:
    pass
obj = Self() 
obj.wallet = {IN_JAVASCRIPT_RENDER_YOUR_WALLET_STATE}
result = SimpleWallet.create_account(self=obj,user = "user_test",label="test",version='python-ecdsa-0.1')

[result,obj.wallet] 

Javascript:

class SimpleWallet()
{
        constructor(){
                this.wallet = {}
         }
         run(){
             let arr = ////PYTHON_{this.wallet }INVOKE///;
             let result = arr[0]
              this.wallet = arr[1]
          }

}

*/










export { decelium_wallet };

export default Decelium;
export { Decelium };
