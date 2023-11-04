

class IPythonWrapper {

    async bindMethods(code_py,modulename,classname,instanceName){
        console.log("in bind");
        console.log(this.pyodide);
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
                        console.log("AM ARRAY");
                        // args is an array, join elements with commas
                        for (const val of args) {
                            argString += '' +  objectToPythonDict(val) + ',';
                        }
                        
                        //argString += args.join(',') + ',';
                    } else {
                        console.log("AM NOT ARRAY");
                        console.log(args);
                        // args is an object, join key-value pairs with commas
                        for (const key in args) {
                            console.log(key);
                            console.log(args[key]);
                            argString += key + '=' + objectToPythonDict(args[key]) + ',';
                        }
                    }            
                }
                //for ( const key in args ) {
                //    argString=argString+key+'="'+args[key]+'",';
                //}
                argString='('+argString+'format="json")';
                console.log(instanceName+`.`+method+argString);
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