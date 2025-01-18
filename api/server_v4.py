### 3rd Attempt more graph oriented

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
from typing import List
from typing_extensions import TypedDict
from langgraph.graph import END, StateGraph, START
from websearch import WebSearch
from sklearn.metrics.pairwise import cosine_similarity
import requests



class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    question: str
    generation: str
    web_search: str
    documents: List[str]

def setup_retriever():
    ### Create Index using an the data folder:
    file_url = open('api/data/urls/links.txt')
    ### Create Index using an the data folder:
    # Open and read the URL file
    with file_url as file_url:
        url_txt = file_url.read()

    # Split the content into a list of URLs and filter out empty lines
    urls = [url for url in url_txt.split("\n") if url.strip()]


    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]


    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=40
    )

    doc_splits = text_splitter.split_documents(docs_list)


    #add in common questions txt files
    # use the common questions text file
    
    # file_url = "api/data/text_docs/common_questions.txt"

    # with open(file_url, "r") as txtfile:
    #     qa_docs = [line.strip() for line in txtfile]

    # doc_splits.extend([{"text": qa} for qa in qa_docs])

    vectorstore = FAISS.from_documents(documents=doc_splits, 
                                        embedding = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")
                                        )
    retriever = vectorstore.as_retriever()

    return retriever

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

def setup_grader():
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
    return retrieval_grader 

def setup_rewriter():
    ### Converts the question to something simpler for the model
    
    # system = """You a question re-writer that converts an input question to a better version that is optimized \n 
    #  for web search. Look at the input and try to reason about the underlying semantic intent / meaning."""
    system = """You a question re-writer that converts an input question to a simpler version that is easier \n 
     for web search. Look at the input and try to find key words that contain semantic intent / meaning. \n
     The response should be just one sentence long."""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()

    return question_rewriter


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # calls retriever
    documents = retriever.get_relevant_documents(question)
    return {"documents": documents, "question": question}

def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    # print("got the generation")
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    top_docs = documents[:2]


    for d in top_docs:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search = "Yes"
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}

### gets the cosine similarities
def calculate_cosine_similarity(question, chunk):
    score = cosine_similarity([question], chunk)    
    return  score[0]

# google search, requires api key and one to build a custom search id: https://programmablesearchengine.google.com/controlpanel/all 
# returns top 3 
def google_search(query, API_KEY, SEAERCH_ID):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEAERCH_ID}&q={query}&start={1}"
    # print("URL:", url)
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        # print("RESULT:",results)

        searches =  results['items']
        urls = []

        try:
            searches = results['items']
            for item in searches[:5]:
                urls.append(item['link'])
        except KeyError:
            print("No items found in the results.")
            return None
        return urls
    else:
        return None
    
def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    ## this works
    ### load 3 urls based on question 
    # web = WebSearch(question)
    # search_urls =web.pages[:3]

    ## more secure/less reliable
    ### websearch using google api (problems with question)
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine = os.getenv("GOOGLE_SEARCH_ID")
    urls = google_search(question,api_key,search_engine)

    ### simpler but not as accurate - throws just urls into documents - sometimes the llm may not have access to these urls
    documents.append(urls)

    # ## convert to texts 
    # search_docs =[WebBaseLoader(url).load() for url in search_urls]
    # search_docs_list =[item for sublist in search_docs for item in sublist]

    # ### add loaded urls to base_retriever, possibly better on frontend
    # urls = [docs.metadata['source']  for docs in search_docs_list]
    # urls = list(dict.fromkeys(urls))

    # docs = [WebBaseLoader(url).load() for url in urls]
    # docs_list = [item for sublist in docs for item in sublist]

    # text_splitter =RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    #     chunk_size=200, chunk_overlap=40
    # )
    # doc_splits = text_splitter.split_documents(docs_list)
    # retriever.add_documents(doc_splits)
    search_docs = []
    ### add urls to text file, then if this is a brand new url add it to the retriever in text form:
    for url in urls:
        new_url = add_url_to_file(url, "api/data/urls/links.txt")
        if new_url == True:
            search_docs.append(WebBaseLoader(url).load())

    search_docs_list =[item for sublist in search_docs for item in sublist]

    text_splitter =RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=40
    )
    doc_splits = text_splitter.split_documents(search_docs_list)
    retriever.add_documents(doc_splits)

    return {"documents": documents, "question": question}

# adds the urls to links.txt and checks if the url was not in the list
def add_url_to_file(url, file_path):
    with open(file_path, 'r') as file:
        existing_urls = set(file.read().splitlines())

    # Check if the URL is already in the file
    if url not in existing_urls:
        # Add the new URL to the set
        existing_urls.add(url)
        # Write the updated URLs back to the file
        with open(file_path, 'w') as file:
            for url in existing_urls:
                file.write(url + '\n')
        return True
    else:
        return False

def decide_to_generate(state):
    """
    Determines wether to re-generate the question

    Args:
        state (dict): The current graph state

    Returns:
        str : Binary decision
    """
    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    web_search = state["web_search"]
    state["documents"]

    if web_search == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"

### the model 
load_dotenv()

model = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0,
    max_tokens=320,
    # top_k=50,
    together_api_key= os.getenv("TOGETHER_API_KEY")
)

### API Keys ###
import getpass

# (optional) LangSmith to inspect inside your chain or agent.
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

### retriever 
retriever = setup_retriever()

### choosing a simpler llm for grading and rewriting
llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0,
)

### used to grade the document 
retrieval_grader = setup_grader()

### used to rewrite the question
question_rewriter = setup_rewriter()

### The chain:
prompt = hub.pull("rlm/rag-prompt")

# Chain
rag_chain = (
    prompt
    | model
    | StrOutputParser()
)
# have multiple models to choose from - websearch

### Current Graph
###                                                -> No ->  Websearch ->
# Question -> Retriever -> Grader (Any Relevant docs)                     Answer
###                                                -> Yes              -> 

workflow = StateGraph(GraphState)

# Define nodes from graph
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)
workflow.add_node("web_search_node", web_search)

# Build Graph
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "web_search_node")
workflow.add_edge("web_search_node", "generate")
workflow.add_edge("generate", END)

# Compile
crags = workflow.compile()


app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt")

    def generate():
            inputs = {"question": str(prompt)}

            print(inputs)

            try:
                for output in crags.stream(inputs):
                    print("Output:", output)
                    if 'generate' in output:
                        generation_value = output['generate']['generation']
                        print("Generation Value:", generation_value)
                        yield generation_value.encode('utf-8')
            except Exception as e:
                print("Error during streaming:", e)
                yield f"Error: {e}".encode('utf-8')

    # Needed for typing response
    return Response(generate(), content_type='text/plain; charset=utf-8')
    
    #return "jsonify(response_text.strip())"

if __name__ == "__main__":
    PORT = 9020
    app.run(port=PORT, debug=True)


# from pprint import pprint
 
# # Run
# inputs = {"question": "Is Cryosurgery Invasive?"}
# for output in crags.stream(inputs):
#     for key, value in output.items():
#         # Node
#         pprint(f"Node '{key}':")
#         # Optional: print full state at each node
#         # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
#     pprint("\n---\n")

# # Final generation
# pprint(value["generation"])



### TO-DO list ###

## append relevant docs - appends to retriever and to links.txt
# aim to be more dynamic (appending the urls)

# restrict the number of tokens used
## use a more expensive model

# commonly asked questions text documents
