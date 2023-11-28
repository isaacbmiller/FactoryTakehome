from flask import Flask, request
from app.chain.chain import generate_ticket_details
from app.models.update_issue import update_issue

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

@app.route('/linear-consumer', methods=['POST'])
def linear_consumer():
    data = request.get_json()
    if data["action"] != "create":
        return 'Data received', 200
    identifier = data["data"]["identifier"]
    description = data["data"]["title"]

    generated_ticket_details = generate_ticket_details(description)
    print(generated_ticket_details)
    # def update_issue(issue_id, title, description, priority):
    params = {
        "issue_id": identifier,
        "title": generated_ticket_details["title"],
        "description": generated_ticket_details["compiled_description"],
        "priority": generated_ticket_details["ticket_type"].priority,
    }

    issue = update_issue(**params)
    
    return 'Data received', 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)