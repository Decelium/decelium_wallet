import Core from "../../../../decelium_wallet/decelium_wallet/core.js";

class Session {
  static instances = null;
  static selected = null;

  static selectInstance(session_id) {
    Session.selected = session_id;
  }

  static getInstance(session_id = null) {
    if (session_id == null) session_id = Session.selected;
    if (session_id == null)
      throw new Error("No active session targeted or selected");

    if (!Session.instances) {
      Session.instances = {};
    }
    if (!Object.keys(Session.instances).includes(session_id)) {
      Session.instances[session_id] = "placeholder";
      Session.instances[session_id] = new Session(session_id);
    }
    return Session.instances[session_id];
  }

  constructor(session_id) {
    if (!Object.keys(Session.instances).includes(session_id)) {
      throw new Error("Use getInstance to create a new session");
    }

    this.py_loaded = null;
    this.data = {
      networkId: "",
      private_key: "",
      port: 5000,
      // Logs
      logs: [],
      messages: [],
      // network connection
      initial_connection_status: false,
      connection_interval: null,
      connection_status: null,
      should_stop_connection: false,
      // Propagator
      cpu_balance: null,
      propagator_interval: null,
      propagator_status: false,
      propagator_error: false,
    };

    this.decelium = null;
  }

  keys() {
    return Object.keys(this.data);
  }
  data() {
    return this.data;
  }

  get(prop) {
    return this.data[prop];
  }

  set(prop, value) {
    this.data[prop] = value;
    return true;
  }

  init() {
    if (this.py_loaded == null) {
      this.py_loaded = new Promise(async (resolve, reject) => {
        try {
          this.decelium = new Core();
          await this.decelium.init();
          resolve(true);
        } catch (error) {
          console.error("An error occurred during initialization:", error);
          window.location.reload();
          resolve(false);
        }
      });
    }
    return this.py_loaded;
  }

  handleError(err, errorMsg) {
    console.error(err);
    this.data["logs"].push(
      `${new Date().toISOString()} ERROR: ${errorMsg ? errorMsg : err}`
    );
    return { error: errorMsg ? errorMsg : err };
  }

  log_message(args, val) {
    console.log("--loggin message--");
    console.log(args, val);

    const log_messages = JSON.stringify([args, val]);

    this.data["logs"].push(
      `${new Date().toISOString()} INFO: ${JSON.stringify(log_messages)}`
    );

    const message = {};

    message.sender = "system";
    message.receiver = this.data.networkId;
    message.query = JSON.stringify(args);
    message.response = JSON.stringify(val);

    this.data["messages"].push(message);
  }

  /**
   * @brief Requires a wallet; used in propagator nodes to create and send node ping messages with contact info.
   * @returns
   */
  async runPropagator() {
    if (this.decelium === false) console.error("There is no decelium");

    if (this.data["propagator_status"]) return;
    this.data["propagator_status"] = true;
    this.data["propagator_error"] = false;

    this.data.propagator_interval = setInterval(async () => {
      try {
        /**
         * @brief Generate a JSON transaction (the node ping message).
         * @returns Api_key, connect_data, name...
         */
        const q = await this.decelium.gen_node_ping(
          this.data["port"],
          this.data["networkId"],
          "admin"
        );

        /**
         * @brief Sign the JSON transaction (node ping message) locally.
         */
        const qSigned = await this.signRequest(q);

        if (qSigned?.error) {
          this.data["logs"].push(
            `${new Date().toISOString()} ERROR: ${JSON.stringify(qSigned)}`
          );
          this.data["propagator_error"] = true;

          return { error: `Error (qSinged): ${JSON.stringify(qSigned)}` };
        }

        if ("__sigs" in qSigned === false) {
          this.data["logs"].push(
            `${new Date().toISOString()} ERROR: ${JSON.stringify(qSigned)}`
          );
          this.data["propagator_error"] = true;

          return { error: `There is no __sigs : ${JSON.stringify(qSigned)}` };
        }

        /**
         * @brief Send the signed JSON transaction (node ping message) to the Decelium network for communication among nodes.
         * @returns connect_data, dir_names, editors, executors, self_id....
         */
        const resp = await this.decelium.net.node_ping(qSigned);

        if (resp?.error) {
          this.data["logs"].push(
            `${new Date().toISOString()} ERROR: ${JSON.stringify(resp)}`
          );
          this.data["propagator_error"] = true;

          return { error: `Error (resp): ${JSON.stringify(resp)}` };
        }

        const balance = await this.getBalance(this.data["api_key"]);

        if (balance?.error) {
          this.data["logs"].push(
            `${new Date().toISOString()} ERROR: ${JSON.stringify(resp)}`
          );
          this.data["propagator_error"] = true;

          return { error: `Error (resp): ${JSON.stringify(resp)}` };
        }

        this.data["cpu_balance"] = balance;

        return balance;
      } catch (err) {
        console.log(err);

        this.data["logs"].push(
          `${new Date().toISOString()} ERROR: ${JSON.stringify(err.message)}`
        );
        this.data["propagator_error"] = true;

        return { error: err.message };
      }
    }, 60000);

    return this.data.propagator_interval;
  }

  stopPropagator() {
    this.data["propagator_status"] = false;
    this.data["propagator_error"] = false;
    clearInterval(this.data["propagator_interval"]);
  }

  async startMonitor() {
    try {
      await this.monitorNetwork();
      this.data.connection_interval = setInterval(async () => {
        await this.monitorNetwork();
      }, 30000);
    } catch (err) {
      return { error: err.message };
    }
  }

  stopMonitor() {
    this.data["connection_status"] = false;
    clearInterval(this.data.connection_interval);
  }

  /**
   * @brief Monitor the network to check for connection status
   * @returns {object} - dir_name, editors, file_type, self_id, parent_id....
   */
  async monitorNetwork() {
    try {
      const connected = await this.connectToNetwork();

      if (connected?.error) {
        return connected.error;
      }

      // Verify connection
      // list the entities at a give path,
      // and checks if the connection is valid when provided with an API key.
      const res = await this.decelium.net.list({
        path: "/",
        api_key: this.data["api_key"],
      });

      if (!Array.isArray(res)) {
        console.log({ res });

        this.data["connection_status"] = false;
        this.data["logs"].push(
          `${new Date().toISOString()} ERROR: ${JSON.stringify(res)}`
        );

        return { error: `could not connect network: ${res}` };
      } else {
        this.data["connection_status"] = true;

        return res;
      }
    } catch (err) {
      this.data["connection_status"] = false;

      this.data["logs"].push(
        `${new Date().toISOString()} ERROR: ${JSON.stringify(err.message)}`
      );

      return { error: err.message };
    }
  }

  /**
   * @brief Connect to the network if not connected.
   * @returns {boolean} - True if connected
   */
  async connectToNetwork(register = "undefined") {
    // TODO, this should be parameterized in the future, as in the future apps can choose to connect and reconnect to different networks and even have multiple sessions

    if (register === "undefined") {
      if (!this.data["api_key"])
        throw new Error("connectToNetwork(): No API Key in session");
    }

    if (!this.data["networkId"])
      throw new Error("connectToNetwork(): No NetworkId Key in session");

    try {
      if (!this.data["initial_connection_status"]) {
        const connected = await this.decelium.initial_connect(
          this.data["networkId"],
          "admin",
          this.data["api_key"] ?? "undefined"
        );

        if (!connected) {
          this.handleError(connected, "Could not connect to the netowrk");
          return { error: "Could not connect to the netowrk" };
        }

        // set True if conencted
        this.set("initial_connection_status", true);
        return connected;
      } else return true;
    } catch (err) {
      return this.handleError(err?.message);
    }
  }

  /**
   * @brief Retrieve the CPU balance.
   * @param {string} api_key - The user's API key.
   * @param {*} self_id - The user's Object Id.
   * @returns {number} CPU balance
   */
  async getBalance(api_key) {
    try {
      const balance = await this.decelium.net.balance({
        api_key,
        self_id: api_key,
        symbol: "CPU",
        contract_id: process.env.REACT_APP_CPU_CONTRACT,
      });
      if (balance?.error) {
        return this.handleError(balance, "Could not retrieve balance.");
      }

      this.data["cpu_balance"] = balance;

      return balance;
    } catch (err) {
      return this.handleError(err);
    }
  }

  /**
   * @brief Connect to the network without using a wallet.
   * @param {object} query - An object representing the user info.
   * Data varies depending on the login type, one of ['password', 'object_id', 'api_key', 'private_key'].
   * @returns {bool} - connected or not.
   */
  async connectWithoutWallet(apikey) {
    // console.log("Inside connectWithoutWallet ");
    // console.log(userInfo);

    if (apikey) {
      console.log("setting api key 2 " + apikey);
      this.set("api_key", apikey);
    } else {
      throw new Error("Must pass userInfo with an api_key field");
    }

    try {
      const connected = await this.connectToNetwork();

      if (connected?.error) {
        //return connected.error;
        return false;
      }

      // Find entities in the filesystem, for the current user
      const listData = await this.decelium.net.list({
        path: "/",
        api_key: this.data["api_key"],
      });

      if (!Array.isArray(listData) || listData.length === 0) {
        return this.handleError(listData, "Could not read from account");
      }
      if (listData?.error) {
        this.handleError(listData, "An error has occurred.");
        return false;
        //return this.handleError(listData, "An error has occurred.");
      }

      return true;
    } catch (err) {
      this.handleError(err);
      return false;
    }
  }

  /**
   * @brief Generate a wallet using a private key, create a public key, and store keys in the wallet.
   * Connect to network
   * @returns {boolean} - 'true' if the operation is successful
   */
  async connectWithWallet(privateKey) {
    if (privateKey) {
      this.set("private_key", privateKey);
    } else {
      throw new Error("Must pass userInfo with an private_key field");
    }

    try {
      // Send message to Session.js
      this.decelium.net.callback = this.log_message.bind(this);

      const user_data = await this.generateWallet(this.data["private_key"]);

      if (user_data.error) {
        return this.handleError(user_data.error);
      }

      Object.assign(this.data, user_data);

      /**
       * Connect to network and verify connection
       * @returns {boolean} true if connected
       */
      const connected = await this.monitorNetwork();

      if (connected.error) {
        return this.handleError(connected.error, "could not load the wallet");
      }

      return true;
    } catch (err) {
      if (err?.message.includes("No module named 'wallet'")) {
        return this.connect();
      }

      return this.handleError(err);
    }
  }

  /**
   * @brief Sign the JSON transaction (node ping message) locally.
   */
  async signRequest(q) {
    try {
      const qSigned = await this.decelium.dw.sign_request({
        q,
        user_ids: ["admin"],
      });

      if (qSigned.error) {
        console.log(qSigned);
        return this.handleError(qSigned.error);
      }

      return qSigned;
    } catch (err) {
      return this.handleError(err);
    }
  }

  // async generatePublicKey() {
  async generateWallet(privateKey) {
    if (!privateKey)
      throw new Error("Must pass userInfo with an private_key field");

    this.set("private_key", privateKey);

    try {
      /*
       * Generate Public Key using Private key
       * @returns Address, Api key, Private key, Version
       */
      let user_data = await this.decelium.dw.recover_user({
        private_key: this.data["private_key"],
      });

      if (user_data.error) {
        return this.handleError(
          user_data.error,
          "could not understand private key"
        );
      }

      /*
       * Generate wallet
       * @returns {boolean}
       */
      let loaded = await this.decelium.load_wallet("{}", "test_pass"); // Create an empty wallet
      if (!loaded) {
        return this.handleError(loaded, "could not load the wallet");
      }

      console.log("------loaded------", loaded);

      /*
       * Store keys using wallet
       * @returns Address, Api key, Private key, Version
       */
      let created = await this.decelium.dw.create_account({
        user: user_data,
        label: "admin",
      });

      if (!created.api_key) {
        return this.handleError(created, "could set up local secure account");
      }

      return user_data;
    } catch (err) {
      return this.handleError(err.message);
    }
  }
}

export default Session;
