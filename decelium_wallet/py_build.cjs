const fs = require('fs');
const path = require('path');

const pythonFiles = ['crypto.py',  'wallet.py',];
let content = "";

/*
Export each python file. Ideally Pyodide could load these files easily. It cannot. These files are used to map the avaliable functions using a regex.
*/

pythonFiles.forEach((file) => {
  const filePath = path.join(__dirname, file);
  content = fs.readFileSync(filePath, 'utf8');
  const jsFilePath = path.join(__dirname, `${file}.js`);
  const jsContent = `export default \`${content}\`;\n`;
  fs.writeFileSync(jsFilePath, jsContent);
});

/*
Bundle all python files as an export. Pyodide seems to, in the browser, reliably handle one import, using a very terrible import method. It is very likely the import method we are using (which works on NodeJs, and in Browser!) is not the ideal method, however it does function reliably, every time. Whereas stepwise imports of the files (above) sometimes leads to missing imports, and silent falures. Thus, we bundle.
*/
content = "";
pythonFiles.forEach((file) => {
  const filePath = path.join(__dirname, file);
  content = content +'\n'+ fs.readFileSync(filePath, 'utf8');
});
const jsFilePath = path.join(__dirname, `py_bundle.py.js`);
const jsContent = `export default \`${content}\`;\n`;
fs.writeFileSync(jsFilePath, jsContent);