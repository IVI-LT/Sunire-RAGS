import os
from dotenv import load_dotenv, find_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_together import TogetherEmbeddings
from langchain_community.llms import Together


load_dotenv()

# client = Together(api_key = os.getenv("TOGETHER_API_KEY"))

#load model
model = Together(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0,
    max_tokens=320,
    top_k=50,
    together_api_key= os.getenv("TOGETHER_API_KEY")
)

# knowledge
urls = [
    "https://www2.hse.ie/conditions/skin-cancer-melanoma/",
    "https://www2.hse.ie/conditions/non-melanoma-skin-cancer/",
]

#### togetherAI  + LANGCHAIN


retriever = vectorstore.as_retriever()

model = Together(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.7,
    max_tokens=128,
    top_k=50,
    together_api_key="..."
)

# Provide a template following the LLM's original chat template.
template = """<s>[INST] Answer the question in a simple sentence based only on the following context:
{context}

Question: {question} [/INST] 
"""
prompt = ChatPromptTemplate.from_template(template) 

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

input_query = "What are some recent highlights of Together AI?"
output = chain.invoke(input_query)

print(output)
