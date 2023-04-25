from flask import send_from_directory,Flask, Response
app = Flask(__name__,static_folder='BCSJAFNKNDJFBIGEABUINKDSNFVSAUFYVASBWIBUFBYDBUISDBSUBFUSAFYUFVSAHFSBJSADBYIAFWY')
app.config.from_object(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:u_path>', methods=['GET', 'POST'])
def index(u_path="/"):
    return send_from_directory('/app/', u_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)