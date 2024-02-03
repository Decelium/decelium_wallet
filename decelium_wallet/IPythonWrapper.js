class IPythonWrapper {
    async bindMethods(code_py,modulename,classname,instanceName){
        this.pyodide.runPython(instanceName+`= ${modulename}.${classname}()`);        
        // this.pyodide.runPython(`print(`+instanceName+`)`);        
        
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
                        // args is an array, join elements with commas
                        for (const val of args) {
                            argString += '' +  objectToPythonDict(val) + ',';
                        }
                    } else {
                        for (const key in args) {
                            argString += key + '=' + objectToPythonDict(args[key]) + ',';
                        }
                    }            
                }
                argString='('+argString+'format="json")';
                let result = this.pyodide.runPython(instanceName+`.`+method+argString);
                return JSON.parse(result); 
              } 
        );            
    }
};
export default IPythonWrapper;
export {IPythonWrapper};