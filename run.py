"""This is the main entrypoint for the application. It is used to capture the webhook from Linear, 
and update the issue with the generated ticket details"""

from flask import Flask, request
from app.api.linear_consumer import consume_linear_webhook

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    '''Index page, mostly useful to check if proxy is working'''
    return 'Hello World'

@app.route('/linear-consumer', methods=['POST'])
def linear_consumer():
    '''Consume Linear webhook, and update issue'''
    data = request.get_json()
    return consume_linear_webhook(data)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
