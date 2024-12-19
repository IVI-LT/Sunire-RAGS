## Goals ##
- Add Rags implementation to server.py
- Apply to dockercompose ot alternative.

**Frontend**
 - frontend/index.html should be an overlay
 - frontend/src/ contains sends the queries to servers.py

## Instructions ##
The api/crag_impl.ipynb contians the general jist of needs to be added to the servers.
 - Load all data.
 - Put them into a  retriever.
 - Find releavent docs, and rank them using a binary yes or no
 - If there is a relevant docs, provide context and ask LLM usrs questions.
 - If no docs, use a websearch.

