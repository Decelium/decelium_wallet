const fs = require('fs');
const path = require('path');

const srcPath = path.resolve(__dirname, './decelium_wallet/');
const destPath = path.resolve(process.cwd(), './public/decelium_wallet');

// Create the destination directory if it doesn't exist
if (!fs.existsSync(destPath)) {
  fs.mkdirSync(destPath, { recursive: true });
}

// Copy the Python files to the destination directory
fs.readdirSync(srcPath).forEach((file) => {
  const srcFile = path.resolve(srcPath, file);
  const destFile = path.resolve(destPath, file);

  if (fs.statSync(srcFile).isFile()) {
    fs.copyFileSync(srcFile, destFile);
    console.log(`Copied ${file} to /public/decelium_wallet`);
  }
});
