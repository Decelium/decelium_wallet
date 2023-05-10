import {crypto} from './crypto.js';

//import wallet_py from './wallet.py.js';

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
        
        
        const wallet_py = (await import  ("./wallet.py.js")).default;
        console.log(wallet_py);
        
        
        this.pyodide = this.core.pyodide;
        this.pyodide.globals.set("wallet_py", wallet_py);
     
        await this.pyodide.runPythonAsync(`
        wallet_py_bytes = codecs.encode(wallet_py, 'utf-8')
        with open("wallet.py", "wb") as f:
            f.write(wallet_py_bytes)
            f.close()`);        
        
        await this.pyodide.runPythonAsync(`import wallet`);              
        
        const py_wallet_var = "test123";
        this.pyodide.runPython(py_wallet_var+`= wallet.wallet()`);        
        
        this.pyodide.runPython(`print(`+py_wallet_var+`)`);        
        
        
        const methodRegex = /def\s+(\w+)\s*\(/g;
        const walletMethods = [];
        let match;
        
        while (match = methodRegex.exec(wallet_py)) {
            walletMethods.push(match[1]);
        }
        
        walletMethods.forEach(method=>
            this[method] = (args) => {
                if (!args)
                    args={};
                let argString = '('; 
                for ( const key in args ) {
                    argString=argString+key+'="'+args[key]+'",';
                }
                argString=argString+'format="json")';
                //console.log(argString);
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