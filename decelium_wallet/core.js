// core.js
import { wallet } from "./wallet.js";
import { network } from "./network.js";
//import { service } from './service.js';
//class network {};
class service {}
//import fs from 'fs';
//import path from 'path';
let fs, path;
if (typeof window === "undefined") {
  // Check if in Node.js environment
  fs = require("fs");
  path = require("path");
}

class Core {
  isNode() {
    if (typeof window === "undefined") return true;
    return false;
  }

  constructor() {}

  async init() {
    if (this.init_done) return true;

    if (this.isNode()) {
      //const { loadPyodide } = require("pyodide");
      //const loadPyodide = async () => {
      //    const pyodideModule = await import('pyodide');
      //    return pyodideModule.loadPyodide();
      //};

      const { loadPyodide } = await import("pyodide");
      console.log(loadPyodide);
      this.pyodide = await loadPyodide({
        indexURL: "/app/projects/decelium_wallet/node_modules/pyodide/",
      });
      //const pyodideReady = pyodideLoader.loadPyodide({
      //    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/",
      //    fs
      //});
      //this.pyodide = await pyodideReady;
    } else {
      this.pyodide = await window.loadPyodide({
        indexUrl: "https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js",
      });
    }

    ////

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
    //await micropip.install('sys');
    await micropip.install("cryptography");

    this.init_done = true;
    this.dw = new wallet(this);
    this.net = new network();
    this.service = new service();
    this.node_peer_list = null;
    //console.log("FINISHED INIT 1");

    await this.dw.init();
    console.log("Phase 6");

    return true;
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
      console.log("data");
      console.log(data);
      console.log("password");
      console.log(data);
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
        console.log("ENDING TIMER FOR " + func.name);
        clearInterval(intervalId);
      }
    }, sec * 1000); // Multiply by 1000 to convert sec to ms
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
      console.log("DOING PING");
      resp = await this.do_ping(port, name, wallet_user);
      console.log(resp);
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
    //console.log("this.nodes",this.nodes);
    for (const n of this.nodes) {
      if (n.self_id === this.self_id) {
        found = true;
      } else {
        if ("test_id" in n.connect_data.meta) {
          this.node_peer_list.push(n);
          //console.log('passed inspection' + n.self_id);
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

  async initial_connect(
    target_url = "https://dev.paxfinancial.ai/data/query",
    target_user,
    api_key
  ) {
    if (api_key === undefined) {
      api_key = this.dw.pubk(target_user);
    }

    this.primary_session_id = await this.net.connect(
      {
        type: "tcpip",
        url: target_url,
        port: 5000,
        api_key: api_key,
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
