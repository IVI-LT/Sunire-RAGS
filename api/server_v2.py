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
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field


### Create Index using an the data folder:
file_url = open('data/urls/links.txt')
url_txt = file_url.read()
urls = url_txt.split("\n")

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=200, chunk_overlap=50
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


# CRAGS implementation
### load the retriever for relevant docs
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

# LLM with function call
llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0,
)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader

### Check if the documents are relevant
### using a LLM to determine its worth
def get_rel_docs(prompt):

    docs = retriever.get_relevant_documents(prompt)

    rel_docs = ''

    for i in range(min(3, len(docs))):
        doc_txt = docs[i].page_content
        final = retrieval_grader.invoke({"question": prompt, "document": doc_txt}) 
        print("final " + str(final)) 
        if(str(final) == "binary_score='yes'" ):
            rel_docs=doc_txt
            # print(final)
            break

    return rel_docs


### If there is not relevant top 3 docs then switch to a websearch ###
def CRAG(prompt):
    rel_docs = get_rel_docs(prompt)
    stream = rag_chain.invoke({"context": rel_docs, "question": prompt})

    #### NEED TO IMPLEMENT WEBSEARCH
    # if(rel_docs != ''):
    #     #print("here")
    #     stream = rag_chain.invoke({"context": rel_docs, "question": question})
    # else:
    #     stream = web_search(question)
    return stream


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

        stream = CRAG(prompt)

        # Response_text in typed form
        for chunk in stream:
            response_text = chunk or ""
            yield response_text

    # Needed for typing response
    return Response(generate(),  content_type='text/plain')
    
    #return "jsonify(response_text.strip())"

if __name__ == "__main__":
    PORT = 5000
    app.run(host="0.0.0.0", port=PORT, debug=True)

#for chunk in stream:
#  print(chunk.choices[0].delta.content or "", end="", flush=True)