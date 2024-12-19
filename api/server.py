
# using together.ai

from flask import Flask, request, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv, find_dotenv
from together import Together

load_dotenv()

client = Together(api_key = os.getenv("TOGETHER_API_KEY"))


app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt")

    # Create a completion using Together API
    def generate():
        stream = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            # Use:   Llama-3.2 free option, vision free ...
            #model = "meta-llama/Llama-Vision-Free",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Response_text in typed form
        for chunk in stream:
            response_text = chunk.choices[0].delta.content or ""
            yield response_text

    # Needed for typing response
    return Response(generate(),  content_type='text/plain')
    
    #return "jsonify(response_text.strip())"


if __name__ == "__main__":
    PORT = 5000
    app.run(host="0.0.0.0", port=PORT, debug=True)

#for chunk in stream:
#  print(chunk.choices[0].delta.content or "", end="", flush=True)