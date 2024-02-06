// core.js
import { wallet } from "./wallet.js";
import { network } from "./network.js";
class service {}
let fs, path,url;
fs = null;
path = null;
import code_py from './py_bundle.py.js';
const BUNDLE_NAME = "py_bundle";

class Core {
  isNode() {
    if (typeof window === "undefined") return true;
        return false;
  }

  constructor() {}

    async import_python_bundle(bundle_name) {
        let temp_filename = bundle_name;
        let modulename = bundle_name;
        this.pyodide.globals.set(`${temp_filename}_py`, code_py);
        await this.pyodide.runPythonAsync(`import sys, importlib`);

        await this.pyodide.runPythonAsync(`
        ${temp_filename}_py_bytes = codecs.encode(${temp_filename}_py, 'utf-8')
        with open("${modulename}.py", "wb") as f:
            f.write(${temp_filename}_py_bytes)
            f.close()`);
        
        await this.pyodide.runPythonAsync(`import ${modulename}`);
  
  }
    async findRootDir(currentDir) {
        try {
            const files =  fs.readFileSync(path.join(currentDir, 'package.json'), 'utf-8');
            return currentDir;
        } catch (error) {
            const parentDir = path.dirname(currentDir);
            if (parentDir === currentDir) {
                throw new Error('Reached the file system root without finding a package.json.');
            }
            return this.findRootDir(parentDir);
        }
    } 

    async init() {
        this.target_user = 'admin'; // By convention, we always look for an admin user
        const originalConsoleLog = console.log;
        const originalStdoutWrite = process.stdout.write.bind(process.stdout);
        const originalStderrWrite = process.stderr.write.bind(process.stderr);

        process.stdout.write = () => { };
        process.stderr.write = () => { };
        console.log = function (message) {
            //if (!message.includes("Loading") && !message.includes("Loaded") && !message.includes("loaded")) {
            //   originalConsoleLog.apply(console, arguments);
            //}
        };
        try {
            // Execute the function and await its completion
            const result = await this.init_console_logs();

            // Return the result after restoring console output
            console.log = originalConsoleLog;
            process.stdout.write = originalStdoutWrite;
            process.stderr.write = originalStderrWrite;

            return result;
        } catch (error) {
            console.log = originalConsoleLog;
            process.stdout.write = originalStdoutWrite;
            process.stderr.write = originalStderrWrite;
            throw error;
        }
    }

    async sr(request, user = null) {
        if (user == null)
            user = this.target_user;
        return await this.dw.sr({
            q: request,
            user_ids: [user]
        });
    }

    async init_console_logs() {

        if (this.init_done) return true;
        let pathVar='path';
        let fsVar='fs';
      
        if (typeof window === 'undefined') { 
            fs = await import('fs');
            path = await import('path');
            url = await import('url');

        }

        if (this.isNode()) {
            // Do a manual search for package.json, then locate the pyodide NPM package.
            // This method is more reliable than relying on convention.
            const { loadPyodide } = await import("pyodide");
            const currentDir = path.dirname(url.fileURLToPath(import.meta.url));

            const __dirname = await this.findRootDir(currentDir);
            const pyodidePath = path.join(__dirname, '..', 'node_modules', 'pyodide');
            this.pyodide = await loadPyodide({
                indexURL: path.join(pyodidePath, '/'), 
            });

        } else {
            this.pyodide = await window.loadPyodide({
            indexUrl: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js",
            });
        }

        await this.pyodide.runPythonAsync(`
            import codecs`);

        await this.pyodide.loadPackage("micropip");
        await this.pyodide.runPythonAsync(`
            import micropip
            micropip.INDEX_URL = 'https://pypi.org/simple'
            import os
            import time

            def wait_for_file(filename, timeout=5):
                start_time = time.time()
                while not os.path.exists(filename):
                    time.sleep(0.1)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout:
                        raise FileNotFoundError(f"File {filename} not found within {timeout} seconds.")
        
            `);
        const micropip = this.pyodide.pyimport("micropip");
        await micropip.install("requests");
        await micropip.install("ecdsa");
        await micropip.install("cryptography");
        this.bundle_name = BUNDLE_NAME;
        await this.import_python_bundle(this.bundle_name);

        this.dw = new wallet(this);
        if (!this.net) this.net = new network();
        this.service = new service();
        this.node_peer_list = null;
      
        await this.dw.init();
      
        this.init_done = true;
        return true;
    }

    get_bundle_name_for(module_name)
    {
        return this.bundle_name;
    }

  getpass(walletpath) {
    const wallet_path = path.resolve(walletpath);
    const wallet_dir = path.dirname(wallet_path);
    let password_file = path.join(
      wallet_dir,
      path.basename(wallet_path, path.extname(wallet_path)) + ".dec.password"
    );

    if (!fs.existsSync(password_file)) {
      password_file = path.join(wallet_dir, ".password");
      if (!fs.existsSync(password_file)) {
        const current_dir = __dirname;
        const wallet_infos = wallet.discover(current_dir);
        for (let info of wallet_infos) {
          if (info["wallet"] === wallet_path) {
            password_file = info["passfile"];
            break;
          }
        }
        if (!fs.existsSync(password_file)) {
          throw new Error("Password file not found.");
        }
      }
    }

    const password = fs.readFileSync(password_file, "utf8").trim();

    return password;
  }

  discover_wallet(root = "./", password = null) {
    root = path.resolve(root);
    let original_root = root;
    let wallet_infos = [];

    for (let depth = 0; depth < 8; depth++) {
      const current_dir = path.resolve(root);
      const files = fs.readdirSync(current_dir);

      files.forEach((file) => {
        if (path.extname(file) === ".dec") {
          let password_file = path.join(
            current_dir,
            path.basename(file, ".dec") + ".dec.password"
          );

          if (!fs.existsSync(password_file)) {
            password_file = path.join(
              current_dir,
              path.basename(file, ".dec") + ".password"
            );
          }

          const wallet_info = {
            wallet: path.join(current_dir, file),
            passfile: fs.existsSync(password_file) ? password_file : null,
          };

          wallet_infos.push(wallet_info);
        }
      });

      root = path.dirname(current_dir);
    }

    root = original_root;
    if (password === null) {
      for (let depth = 0; depth < 8; depth++) {
        const current_dir = path.resolve(root);
        const files = fs.readdirSync(current_dir);

        files.forEach((file) => {
          if (
            path.extname(file) === ".password" &&
            path.basename(file, ".password")
          ) {
            const wallet_file = path.join(
              current_dir,
              path.basename(file, ".password") + ".dec"
            );
            if (!fs.existsSync(wallet_file)) {
              wallet_infos.push({
                wallet: null,
                passfile: path.join(current_dir, file),
              });
            }
          }
        });

        root = path.dirname(current_dir);
      }
    }

    return wallet_infos;
  }

  async load_wallet(data, password, mode = "js") {
    if (typeof data !== "string" || typeof password !== "string") {
      throw new Error("Invalid argument types.");
    }
    this.dw = new wallet(this);
    await this.dw.init();
      
    const success = this.dw.load({ data, password, mode });
    return success;
  }

  gen_node_ping(port, name, wallet_user) {
    let services = {};
    if (this.service.get_registry)
      services = this.service.get_registry("public");
    if (Object.keys(services).includes("error")) services = {};
    const q = this.net.gen_node_ping({
      name,
      api_key: this.dw.pubk(wallet_user),
      self_id: null,
      services,
      meta: { test_id: "unit_test" },
      port,
    });
    return q;
  }
  /*

    async listen(port, name,wallet_user="admin", public_handlers = []) {
        public_handlers.forEach((cfg) => {
            this.service.set_handler({
                id: cfg[0],
                name: cfg[0],
                handler: cfg[1],
                group: 'public',
                runtime: null,
                meta: {},
            });
        });

        const q = this.gen_node_ping(port, name,wallet_user);
        const qSigned = this.dw.sign_request(q, [wallet_user]);
        if ('error' in qSigned) {
            return qSigned;
        }
        const resp = await this.net.node_ping(qSigned);
        if ('error' in resp) {
            return resp;
        }
        this.self_id = resp.self_id;
        this.net.listen(port);
        if (!this.net.listening()) {
            return { error: 'could not start listening' };
        }
        await new Promise((resolve) => setTimeout(resolve, 3000));
        return true;
    }*/

  setInterval(func, keepRunning, sec, ...args) {
    const intervalId = setInterval(() => {
      if (keepRunning()) {
        func(...args);
      } else {
        clearInterval(intervalId);
      }
    }, sec * 1000); 
    return intervalId;
  }

  async listen(port, name, wallet_user = "admin", public_handlers = []) {
    if (this.service.set_handler) {
      public_handlers.forEach((cfg) => {
        this.service.set_handler({
          id: cfg[0],
          name: cfg[0],
          handler: cfg[1],
          group: "public",
          runtime: null,
          meta: {},
        });
      });
    }

    let resp = await this.do_ping(port, name, wallet_user);
    if ("error" in resp) {
      return resp;
    }

    this.self_id = resp.self_id;
    resp.api_key = this.dw.pubk(wallet_user);
    this.net.listen(resp, this.handle_connection);

    if (!this.net.listening()) {
      return { error: "could not start listening" };
    }

    const run_pings_def = async () => {
      resp = await this.do_ping(port, name, wallet_user);
    };

    this.setInterval(run_pings_def, () => this.net.listening(), 5); // ping every 5 seconds

    return true;
  }

  async do_ping(port, name, wallet_user = "admin", public_handlers = []) {
    if (this.service.set_handler) {
      public_handlers.forEach((cfg) => {
        this.service.set_handler({
          id: cfg[0],
          name: cfg[0],
          handler: cfg[1],
          group: "public",
          runtime: null,
          meta: {},
        });
      });
    }
    const q = this.gen_node_ping(port, name, wallet_user);
    const qSigned = this.dw.sign_request({ q: q, user_ids: [wallet_user] });

    if ("error" in qSigned) {
      return qSigned;
    }
    const resp = await this.net.node_ping(qSigned);
    if ("error" in resp) {
      resp.error = resp.error + " with message " + JSON.stringify(qSigned);
      return resp;
    }
    try {
      this.self_id = resp.self_id;
      return resp;
    } catch {
      return {
        error: "gen_node_ping response is invalid: " + JSON.stringify(resp),
      };
    }
  }

  async sync_node_list() {
    this.node_peer_list = [];
    this.nodes = await this.net.node_list();

    let found = false;
    for (const n of this.nodes) {
      if (n.self_id === this.self_id) {
        found = true;
      } else {
        if ("test_id" in n.connect_data.meta) {
          this.node_peer_list.push(n);
        }
      }
    }
  }

  async node_list() {
    if (this.node_peer_list === null) {
      await this.sync_node_list();
    }
    return this.nodes;
  }

  async node_peers() {
    if (this.node_peer_list === null) {
      await this.sync_node_list();
    }
    return this.node_peer_list;
  }

  list_sessions() {
    return this.list_sessions();
  }

  handle_connection(path, args) {
    try {
      const res = this.service.run(args);
      return res;
    } catch (err) {
      return err.stack;
    }
  }
    /**
     *   async initial_connect(
    target_url = undefined,
    target_user = undefined,
    api_key = undefined
  ) {
    if (target_user == undefined)
        target_user = await this.dw.list_accounts()[0];
    if (!this.net) this.net = new network();
    let set_api_key = api_key;
    if (!set_api_key && target_user && this.dw)
      set_api_key = this.dw.pubk(target_user);
    if (!set_api_key) throw new Error("No valid credentials provided");
      if (!target_url) throw new Error("No valid URL provided");

      // Create a URL object from the target_url string
      const url = new URL(target_url);
    this.primary_session_id = await this.net.connect(
      {
        type: "tcpip",
        host: url.hostname, // Extracts the host part of the URL
        protocol: url.protocol.slice(0, -1),, // Extracts the protocol part of the URL (note: it includes the colon (:) at the end)
        path: url.pathname, // Extracts the path part of the URL
        port: 5000,
        api_key: set_api_key,
      },
      this.handle_connection.bind(this)
    );

     */
  async initial_connect(
    target_url = undefined,
    target_user = undefined,
    api_key = undefined
  ) {
    if (target_user == undefined)
    {
        let lst = await this.dw.list_accounts();
        if (lst.length > 0)
          target_user = await lst.list_accounts()[0];
    }
    if (!this.net) this.net = new network();
    let set_api_key = api_key;
    if (!set_api_key && target_user && this.dw)
      set_api_key = this.dw.pubk(target_user);
    if (!set_api_key) throw new Error("No valid credentials provided");

    this.primary_session_id = await this.net.connect(
      {
        type: "tcpip",
        url: target_url,
        port: 5000,
        api_key: set_api_key,
      },
      this.handle_connection.bind(this)
    );

    if (!this.net.connected()) {
      throw new Error("Not connected.");
    }
    return true;
  }
}

export { Core };
export default Core;
