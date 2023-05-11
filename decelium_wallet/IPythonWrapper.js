class IPythonWrapper {


    async bindMethods(temp_filename,modulename,classname,instanceName){
    
        const code_py = (await import  (`./${temp_filename}.py.js`)).default;
        //console.log(code_py);
        
        this.pyodide = this.core.pyodide;
        this.pyodide.globals.set(`${temp_filename}_py`, code_py);
     
        await this.pyodide.runPythonAsync(`
        ${temp_filename}_py_bytes = codecs.encode(${temp_filename}_py, 'utf-8')
        with open("${modulename}.py", "wb") as f:
            f.write(${temp_filename}_py_bytes)
            f.close()`);        
        
        await this.pyodide.runPythonAsync(`import ${modulename}`);              
        
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
                console.log("CALLING method ", method);
                console.log("---------------------------------------");
                console.log(args);
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
                    if (Array.isArray(args)) {
                        console.log("AM ARRAY");
                        // args is an array, join elements with commas
                        argString += args.join(',') + ',';
                    } else {
                        console.log("AM NOT ARRAY");
                        // args is an object, join key-value pairs with commas
                        for (const key in args) {
                            argString += key + '="' + args[key] + '",';
                        }
                    }            
                }
                //for ( const key in args ) {
                //    argString=argString+key+'="'+args[key]+'",';
                //}
                argString='('+argString+'format="json")';
                console.log(instanceName+`.`+method+argString);
                let result = this.pyodide.runPython(instanceName+`.`+method+argString);
                return JSON.parse(result); 
              } 
        );            
    }
    
};

export default IPythonWrapper;
export {IPythonWrapper};