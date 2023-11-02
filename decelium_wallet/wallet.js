import {crypto} from './crypto.js';
import py_data from './wallet.py.js'
import {IPythonWrapper} from './IPythonWrapper.js';

class wallet extends IPythonWrapper {
    constructor(core) {
        super();
        this.core = core
        this.crypto = new crypto(core);
    }
    
    async init()
    {
        const temp_filename = "wallet";
        const modulename = "wallet";
        const classname = "wallet";
        const instanceName = "wallet";
        
        if (this.done_init)
            return true;
        await this.crypto.init();
        await this.bindMethods(temp_filename,modulename,classname,instanceName,py_data);
        
        this.done_init = true;
        return true;
    }
}
export { wallet};
export default wallet;