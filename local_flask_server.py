from flask import send_from_directory,Flask, Response
app = Flask(__name__)
app.config.from_object(__name__)

'''
########## TODO: Finish proxy implementation (if needed)

#import sys
#sys.path.append('../../FinancialAlgorithm')
#sys.path.append('../../')
from PaxFinancialAPI import PaxFinancialAPIClass

#password_sha = hashlib.sha224(session_code.encode('utf-8')).hexdigest()
#print(password_sha)

#pq = paxdk.PaxFinancialAPI.PaxFinancialAPI(url_version='http://34.214.236.190:5000')
pq = paxdk.PaxFinancialAPI.PaxFinancialAPIClass(url_version='dev.paxfinancial.ai')
#############

@app.route('/data/query/<path:path>')
def api_proxy(path):
    api_key = "pkey-a0f8540cacc41427ae251101ce1dc1f612068ffcbe9801f27294251a"
    session_code = 'ses-d6ff065d-2fd3-44e7-bf96-158f90782786'
    pq.purge_logs({'api_key':session_code},remote=False)
    
    return send_from_directory('/app/projects/', path)
'''

@app.route('/<path:path>')
def send_report(path):
    return send_from_directory('/app/projects/', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)