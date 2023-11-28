from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

@app.route('/linear-consumer', methods=['POST'])
def linear_consumer():
    data = request.get_json()
    print(data)  # Print the received data to the console
    return 'Data received', 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)