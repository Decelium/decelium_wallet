import crypto_py from './crypto.py.js';

class crypto {
    constructor(core) {
        this.core = core
    }
    async init()
    {
        if (this.done_init)
            return true;
        this.pyodide = this.core.pyodide;
        this.pyodide.globals.set("crypto_py", crypto_py);
     
        await this.pyodide.runPythonAsync(`
        crypto_py_bytes = codecs.encode(crypto_py, 'utf-8')
        print("-------writing crypto.py")
        with open("crypto.py", "wb") as f:
            f.write(crypto_py_bytes)
            f.close()
        print("-------wrote crypto.py")`);        
        
        await this.pyodide.runPythonAsync(`import crypto`);              
        
        //const py_wallet_var = "test123";
        //this.pyodide.runPython(py_wallet_var+`= wallet.wallet()`);        
        
        
        
        //const wallet_methods = ['create_account','load','get_raw'];
        //wallet_methods.forEach(method=>
        //    this[method] = (args) => {
        //        if (!args)
        //            args={};
        //        let argString = '('; 
        //        for ( const key in args ) {
        //            argString=argString+key+'="'+args[key]+'",';
        //        }
        //        argString=argString+'format="json")';
        //        console.log(argString);
        //        let result = this.pyodide.runPython(py_wallet_var+`.`+method+argString);
        //        return JSON.parse(result); 
        //      } 
        //);        
        
        this.done_init = true;
        return true;
    }
}
export { crypto};
export default crypto;