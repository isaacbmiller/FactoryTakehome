TODO: Add description, details, and demo video

# Add webhook to linear
# Set up proxy for local development

I chose to use ngrok because it is free and easy, but you can use any other proxy service, as long as it forwards traffic to your local port 3000.

You can make an ngrok account [here](https://dashboard.ngrok.com/signup).

```bash
brew install ngrok

ngrok config add-authtoken <token>

ngrok http --domain=<your domain here> 3000
```

In separate terminal

```bash
# Install dependencies
pip install -r requirements.txt

# Run the flask server
python run.py
```

# TODO

- [x] Finish developing the chain according to the linear fields
- [x] Convert the chain into GraphQL schema to use with linear api
- [ ] Clean up code
- [ ] Add error handling with LangChain
- [ ] Add tests
  - [ ] Test endpoints
  - [ ] Evaluate prompts using langsmith(still on waitlist :/)
- [ ] Figure out how to share without deploying
- [ ] Dockerize and deploy to AWS
