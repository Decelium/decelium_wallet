//import * as IPFS from 'ipfs-core';
import ipfsClient from 'ipfs-http-client';
//import * as IPFS from 'ipfs-core/src/index.js';
import { helloWorld } from './hello';

//import Core from "../../../../decelium_wallet/core.js";
document.getElementById('hello-message').innerText = helloWorld();