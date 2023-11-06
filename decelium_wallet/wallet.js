import {crypto} from './crypto.js';
import {IPythonWrapper} from './IPythonWrapper.js';
import code_py from './wallet.py.js'


class wallet extends IPythonWrapper {
    constructor(core) {
        super();
        this.core = core;
        this.pyodide = this.core.pyodide;
        this.crypto = new crypto(core);
    }
    
    async init()
    {
        const modulename = this.core.get_bundle_name_for("wallet");        
        const classname = "wallet";
        const instanceName = "wallet";
        console.log("wallet 1");
        if (this.done_init)
            return true;
        console.log("wallet 2");
        await this.crypto.init();
        console.log("wallet 3");
        await this.bindMethods(code_py,modulename,classname,instanceName);
        console.log("wallet 4");
        
        this.done_init = true;
        return true;
    }
}
export { wallet};
export default wallet;