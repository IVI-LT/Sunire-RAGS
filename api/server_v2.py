from flask import Flask, request, Response
from flask_cors import CORS
import os
from dotenv import load_dotenv, find_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_together import TogetherEmbeddings
from langchain_together import ChatTogether
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


### Create Index using an the data folder:
file_url = open('data/urls/links.txt')
url_txt = file_url.read()
urls = url_txt.split("\n")

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=300, chunk_overlap=50
)

doc_splits = text_splitter.split_documents(docs_list)

vectorstore = FAISS.from_documents(documents=doc_splits, 
                                    embedding = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
                                    )

retriever = vectorstore.as_retriever()


### the model 
load_dotenv()

model = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0,
    max_tokens=320,
    # top_k=50,
    together_api_key= os.getenv("TOGETHER_API_KEY")
)

### The chain:
prompt = hub.pull("rlm/rag-prompt")

# Chain
rag_chain = (
    {"context": retriever , "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt")

    # Create a completion using Together API
    def generate():

        # stream = client.chat.completions.create(
        #     model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        #     # Use:   Llama-3.2 free option, vision free ...
        #     #model = "meta-llama/Llama-Vision-Free",
        #     messages=[{"role": "user", "content": prompt}],
        #     stream=True,
        # )

        stream = rag_chain.invoke(prompt)

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