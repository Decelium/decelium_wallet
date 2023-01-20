
jest.setTimeout(30000);
/*
test('Run python tests', async () => {
    let program_out=undefined;
    let program_err=undefined;
    let args = {'example':1};
    
    try {
        // Use the spawn function to run the Python script and capture the output
        console.log("OPEN");
        const pythonProcess = spawn('python3', ['./__tests__/full.py', JSON.stringify(args)]);
        pythonProcess.stdout.on('data', (data) => {
            console.log("DATA");
            program_out = data.toString();
        });
        pythonProcess.stderr.on('data', (data) => {
            console.log("ERR");
            program_err = data.toString();
        });
    
        await new Promise((resolve) => {
            pythonProcess.on('close', (code) => {
                console.log("CLOSED 2");
                console.log(`child process exited with code ${code}`);
                resolve();
            });           
            //pythonProcess.on('close', resolve);
        });

    } catch (err) {
        console.log(err);
    }
    outStr = "";
    if (program_out) outStr  = outStr + program_out;
    if (program_err) outStr  = outStr + program_err;
    console.log(outStr);
    expect(parseInt(program_out.toString())).toEqual(1,outStr);
});*/

test('Run nodejs tests', async () => {
    
    /*
    try {
        const data = fs.readFileSync('../program.py', 'utf8');
        modData = `"""`+data+`"""`;
    } catch (err) {
        console.log(err);
    }    
    console.log(modData);*/
    
    const { loadPyodide } = require("pyodide");
    const fs = require('fs');
    modData = undefined;

    let pyodide = await loadPyodide();
    let mountDir = "/mnt";
    pyodide.FS.mkdir(mountDir);
    pyodide.FS.mount(pyodide.FS.filesystems.NODEFS, { root: "." }, mountDir);
    pyodide.runPython("import os; print(os.listdir('/mnt'))");

    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install('ecdsa');    
    
    await pyodide.loadPackage(['cryptography'])
    pkg1 = pyodide.pyimport("cryptography");
    console.log(pyodide.runPython("import cryptography"));
    
    await pyodide.runPythonAsync(`
        with open("/mnt/crypto.py", "rb") as f1:
            with open("crypto.py", "wb") as f2:
                s = f1.read()
                f2.write(s)
        `)
    crypto = pyodide.pyimport("crypto");    

    //console.log(crypto.calculate())
    //console.log("DATA");
    //console.log(JSON.stringify(crypto.crypto.generate_user(format="json")))
    await pyodide.runPythonAsync(`import crypto`)
    console.log(await pyodide.runPythonAsync(`crypto.crypto.generate_user(format="json")`));

    expect(1).toEqual(1);

});