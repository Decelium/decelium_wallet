import {IPythonWrapper} from './IPythonWrapper.js';
import code_py from './crypto.py.js';

class crypto extends IPythonWrapper {
    constructor(core) {
        super();
        this.core = core;
        this.pyodide = this.core.pyodide;
    }
    async init()
    {
        const modulename = this.core.get_bundle_name_for("crypto");
        const classname = "crypto";
        const instanceName = "crypto";
        if (this.done_init)
            return true;
        await this.bindMethods(code_py,modulename,classname,instanceName);
        this.done_init = true;
        return true;
    }
}
export { crypto};
export default crypto;