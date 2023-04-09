import {useEffect} from 'react';
import {decelium_wallet} from '@decelium/decelium_wallet'

function App() {
    
  useEffect( () => {
      let dw = decelium_wallet;
      dw.init().then( () => {
        let gen_wallet = dw.commands.generate_a_wallet.run({ wallet_path: ".wallet1.dec"});
        document.getElementById("generate_wallet").value=JSON.stringify(gen_wallet);
        
        if (Object.keys(gen_wallet).length !== 0) throw new Error('Test failed: wallet is not empty');
        let gen_user = dw.commands.generate_user.run({wallet_path: ".wallet1.dec", wallet_user: "test_user", confirm:"confirm"});
        document.getElementById("generate_user").value=JSON.stringify(gen_user);
        if (!('test_user' in gen_user)) throw new Error('Test failed: test_user not in wallet');
        if (!('description' in gen_user['test_user'])) throw new Error('Test failed: description not in wallet.test_user');
        if (!('image' in gen_user['test_user'])) throw new Error('Test failed: image not in wallet.test_user');
        if (!('secrets' in gen_user['test_user'])) throw new Error('Test failed: secrets not in wallet.test_user');
        if (!('title' in gen_user['test_user'])) throw new Error('Test failed: title not in wallet.test_user');
        if (!('user' in gen_user['test_user'])) throw new Error('Test failed: user not in wallet.test_user');
        if (!('api_key' in gen_user['test_user']['user'])) throw new Error('Test failed: api_key not in wallet.test_user.user');
        if (!('private_key' in gen_user['test_user']['user'])) throw new Error('Test failed: private_key not in wallet.test_user.user');
        if (!('version' in gen_user['test_user']['user'])) throw new Error('Test failed: version not in wallet.test_user.user');

        let test_username = 'test_user' + String(Math.random());
        let user_id = dw.commands.create_user.run({wallet_path:'.wallet1.dec', wallet_user: 'test_user', dec_username: test_username, url_version: 'test.paxfinancial.ai', password:'passtest'});
        console.log(JSON.stringify(user_id));
        document.getElementById("user_id").value=JSON.stringify(user_id);
        if (!user_id.startsWith('obj-')) throw new Error('Test failed: user_id does not start with obj-');

        let fund_result=dw.commands.fund.run({wallet_path: "./test_wallet.dec", wallet_user: "test_user", url_version: "test.paxfinancial.ai"});
        if (fund_result!==true) throw new Error('Test failed: fund_result is not true');
        
        let balance=dw.commands.check_balance.run({wallet_path: "./test_wallet.dec", wallet_user: "test_user", url_version: "test.paxfinancial.ai"})
        if (balance!=200) throw new Error('Test failed: balance!=200');
              
      });
      
  },[]);   
    
  return (
    <div className="App">
        <form>
          <input type="text" id="generate_wallet" name="generate_wallet"/><br/>
          <textarea id="generate_user" name="generate_user" rows="10" cols="100"></textarea><br/>
          <input type="text" id="user_id" name="user_id"/><br/>    
        </form>    
    </div>
  );
}

export default App;
