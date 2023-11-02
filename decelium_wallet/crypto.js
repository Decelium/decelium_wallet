import {IPythonWrapper} from './IPythonWrapper.js';
import py_data from './crypto.py.js'


class crypto extends IPythonWrapper {
    constructor(core) {
        super();
        this.core = core
    }
    
    async init()
    {
        const temp_filename = "crypto";
        const modulename = "crypto";
        const classname = "crypto";
        const instanceName = "crypto";
        
        if (this.done_init)
            return true;
        await this.bindMethods(temp_filename,modulename,classname,instanceName,py_data);
        
        this.done_init = true;
        return true;
    }
}
export { crypto};
export default crypto;