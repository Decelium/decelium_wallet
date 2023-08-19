const fs = require('fs');
const path = require('path');

const pythonFiles = ['crypto.py', 'decelium.py', 'wallet.py',];

pythonFiles.forEach((file) => {
  const filePath = path.join(__dirname, file);
  const content = fs.readFileSync(filePath, 'utf8');
  const jsFilePath = path.join(__dirname, `${file}.js`);
  const jsContent = `export default \`${content}\`;\n`;
  fs.writeFileSync(jsFilePath, jsContent);
});
