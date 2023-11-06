import sys
from flask import Flask, send_from_directory, Response
# Check if the directory is passed as command line argument
if len(sys.argv) > 1:
    root_dir = sys.argv[1]
else:
    print("Please provide the directory as a command line argument.")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)#, static_folder=root_dir)
app.config.from_object(__name__)
import os

# Define routes
@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:u_path>', methods=['GET', 'POST'])
def index(u_path="/"):
    return "hello"
    '''
    full_path =os.getcwd()+root_dir+ u_path
    # Check if the file exists
    if os.path.isfile(full_path):
        # Send the file
        return send_from_directory(os.getcwd()+root_dir, u_path)
    else:
        # Return the path for debugging
        return Response(f"File not found at: {full_path}", status=404)
    '''
    
# Main entry point
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
