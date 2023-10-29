class IPythonWrapper {


    async bindMethods(temp_filename,modulename,classname,instanceName){
        
        const code_py = (await import  (`./${temp_filename}.py.js`)).default;
        this.pyodide = this.core.pyodide;
        this.pyodide.globals.set(`${temp_filename}_py`, code_py);
        
        //await this.pyodide.runPythonAsync(`import ${modulename}`);  
        let maxAttempts = 5;
        let attempts = 0;
        let delay = 100; // initial delay of 0.1 seconds
        await this.pyodide.runPythonAsync(`import sys, importlib`);

        await this.pyodide.runPythonAsync(`
        ${temp_filename}_py_bytes = codecs.encode(${temp_filename}_py, 'utf-8')
        with open("${modulename}.py", "wb") as f:
            f.write(${temp_filename}_py_bytes)
            f.close()`);
        await this.pyodide.runPythonAsync(`mod_list = set(sys.modules.keys())`);
        await this.pyodide.runPythonAsync(`import ${modulename}`);
        //await this.pyodide.runPythonAsync(`importlib.import_module('${modulename}')`);
        await this.pyodide.runPythonAsync(`
        mod_list_new = set(sys.modules.keys())
        new_mods = mod_list_new - mod_list
        `);
        
        this.pyodide.runPython(instanceName+`= ${modulename}.${classname}()`);        
        this.pyodide.runPython(`print(`+instanceName+`)`);        
        
        const methodRegex = /def\s+(\w+)\s*\(/g;
        const instanceMethods = [];
        let match;
        
        while (match = methodRegex.exec(code_py)) {
            instanceMethods.push(match[1]);
        }
        
        instanceMethods.forEach(method=>
            this[method] = (args) => {
            
                const objectToPythonDict = (item) => {
                    if (item== null || item == undefined)
                        return "None"
                    if (typeof item === 'string') {
                        return `'${item}'`;
                    } else if (typeof item === 'number') {
                        return item;
                    } else if (item === true) {
                        return "True";
                    } else if  (item === false) {
                        return "False";
                    } else if (typeof item === 'object') {
                        if (Array.isArray(item)) {
                            return '[' + item.map(objectToPythonDict).join(', ') + ']';
                        } else {
                            let dictString = "{";
                            for (const [key, value] of Object.entries(item)) {
                                dictString += `'${key}': ${objectToPythonDict(value)}, `;
                            }
                            dictString = dictString+ "}";
                            return dictString;
                        }
                    } else {
                        throw new Error(`Unsupported data type: ${typeof item}`);
                    }
                };

            
                if (!args)
                    args={};
            
                let argString = '';             
                if (typeof args !== 'object') {
                    if (typeof args === 'number')
                        argString = `${args},`;
                    else
                        argString = `"${args}",`;
                }
                else
                {
                    if (Array.isArray(args) &&  args.length ==1) {
                        //console.log("AM ARRAY");
                        // args is an array, join elements with commas
                        for (const val of args) {
                            argString += '' +  objectToPythonDict(val) + ',';
                        }
                        
                        //argString += args.join(',') + ',';
                    } else {
                        //console.log("AM NOT ARRAY");
                        //console.log(args);
                        // args is an object, join key-value pairs with commas
                        for (const key in args) {
                            //console.log(key);
                            //console.log(args[key]);
                            argString += key + '=' + objectToPythonDict(args[key]) + ',';
                        }
                    }            
                }
                //for ( const key in args ) {
                //    argString=argString+key+'="'+args[key]+'",';
                //}
                argString='('+argString+'format="json")';
                // console.log(instanceName+`.`+method+argString);
                //instanceName+`.`+method+argString
                //throw new Error(instanceName+`.`+method+argString);
                let result = this.pyodide.runPython(instanceName+`.`+method+argString);
                //console.log("wallet result");
                //console.log({result});
            
                return JSON.parse(result); 
              } 
        );            
    }
    
};

export default IPythonWrapper;
export {IPythonWrapper};