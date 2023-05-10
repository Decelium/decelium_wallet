import wallet_py from './wallet.py.js';

class wallet {
    constructor(core) {
        return;
        this.pyodide = core.pyodide;
        this.pyodide.globals.set("wallet.py", wallet_py);
     
        
        const py_wallet_var = "test123";
        wallet.pyodide.runPython(py_wallet_var+`= wallet.wallet()`);        
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
                let result = wallet.pyodide.runPython(py_wallet_var+`.`+method+argString);
                return JSON.parse(result); 
              } 
        );        
        
        
        
        
    }
    
    load({ data, password })
    {
        //console.log(data);
        //console.log(data);
        return true;
    }
}
export { wallet};
export default wallet;