import wallet_py from './wallet.py.js';
import {crypto} from './crypto.js';

class wallet {
    constructor(core) {
        this.core = core
        this.crypto = new crypto(core);
    }
    
    
    async init()
    {
        if (this.done_init)
            return true;
        await this.crypto.init();
        
        this.pyodide = this.core.pyodide;
        this.pyodide.globals.set("wallet_py", wallet_py);
     
        await this.pyodide.runPythonAsync(`
        wallet_py_bytes = codecs.encode(wallet_py, 'utf-8')
        print("-------writing wallet.py")
        with open("wallet.py", "wb") as f:
            f.write(wallet_py_bytes)
            f.close()
        print("-------wrote wallet.py")`);        
        
        await this.pyodide.runPythonAsync(`import wallet`);              
        
        const py_wallet_var = "test123";
        this.pyodide.runPython(py_wallet_var+`= wallet.wallet()`);        
        
        this.pyodide.runPython(`print(`+py_wallet_var+`)`);        
        
        
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
                let result = this.pyodide.runPython(py_wallet_var+`.`+method+argString);
                return JSON.parse(result); 
              } 
        );        
        
        
        this.done_init = true;
        return true;
        
        
    }
    

}
export { wallet};
export default wallet;