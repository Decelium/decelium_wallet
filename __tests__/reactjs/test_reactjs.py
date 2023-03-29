const puppeteer = require('puppeteer');
const { exec } = require('child_process');

(async () => {
  // Run npm install in the local directory
  await new Promise((resolve, reject) => {
    exec('npm install', (err, stdout, stderr) => {
      if (err) {
        console.error(npm install error: ${err});
        reject(err);
      } else {
        console.log(npm install stdout: ${stdout});
        console.error(npm install stderr: ${stderr});
        resolve();
      }
    });
  });

  // Start up a React app on port 5000
  const app = await new Promise((resolve, reject) => {
    const child = exec('npm start', { env: { PORT: 5000 } });
    child.stdout.on('data', (data) => {
      if (/Compiled successfully/.test(data)) {
        console.log('React app started on port 5000');
        resolve(child);
      }
    });
    child.stderr.on('data', (data) => {
      console.error(React app error: ${data});
      reject(data);
    });
  });

  // Use Puppeteer to get the body of the root
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5000/');
  await page.waitForSelector('body');
  const html = await page.content();
  const text = await page.evaluate(() => document.body.textContent);

  // Assert some information about the body
  const expectedText = 'Hello, world!';
  if (text.includes(expectedText)) {
    console.log(Body contains "${expectedText}");
  } else {
    console.error(Body does not contain "${expectedText}");
  }

  // Close down the React app
  app.kill();

  // Save the results in a local file called test.json
  const results = { html, text };
  const fs = require('fs');
  fs.writeFileSync('test.json', JSON.stringify(results));
  console.log('Results saved to test.json');

  // Close the browser
  await browser.close();
})();