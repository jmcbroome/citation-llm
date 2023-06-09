# citation_llm
Repository containing code exploring the use of citation context information extracted from academic and scientific work for Retrieval-Augmented Generation (RAG).

## Concept

### Background 

One of the major challenges for modern Large Language Models (LLMs) is hallucination. As learned knowledge is stored as implicit weights, rather than as explicit memory, attempts to retrieve citations for factual statements or effective references for ideas are often met with scrambled, unrelated, or entirely fictional names and book titles. Additionally, any given LLM may not have been trained on the relevant material, or it may not have been commonly referenced enough in the training data to be learned implicitly.

Retrieval-Augmented Generation (RAG) techniques attempt to address these challenges by providing these models with an explicit memory. Most generally, a set of documents is digested into embeddings and made available to the LLM instance. On the user's query, a semantic search is performed and the most relevant context is extracted from the documents. This context is included in the prompt for completion, and the overall completion is more accurate and of higher quality.

### Citation Context and RAG

In this repository, I explore a specific approach to RAG with the aim of enhancing factuality in answering scientific and academic questions and providing real references for further reading and research on the part of the user.

We may consider that a given academic document- be it a book or a manuscript- consists of some set of statements that it supports. In an ideal world, we would have some process to extract all relevant scientific knowledge from a manuscript and present it to the model, but this is extremely challenging to implement.

However, for many documents, there already exist cases where researchers have read, understood, and highlighted citeable statements- when they cited that original document in their own work.

For a document with sufficient citations, instead of parsing the original document, we can instead extract the statements for which that document was cited from other academic documents, and develop an understanding of what that document supports from this set of citations. Some researchers have explored this area for citation context sentiment analysis, but to my knowledge this approach has not been applied for RAG for scientific queries to LLMs.

### Implementation and Dataset

Collecting citation context data in and of itself is a significant undertaking, though tools like GROBID are available for parsing large numbers of documents. For our purposes, we instead rely on the [Citation-Context Dataset (C2D)](https://ordo.open.ac.uk/articles/dataset/Citation-Context_Dataset_C2D_/6865298/1), which contains 53 million citations from more than 2 million scientific and academic works from before August 2018. While these raw citation strings contain many errors, LLMs are generally effective at understanding poorly formatted text, so we minimally remove only entries with non-unicode characters or missing reference information.

Once cleaned up, we extract a set of unique citation contexts from the dataset, along with all associated references for each context. We compute an embedding for each context and store the embedding in a [FAISS](https://github.com/facebookresearch/faiss) vectorstore, as well as storing the raw text and reference information in an associated SQlite relational database. This step is largely handled by [txtai](https://github.com/neuml/txtai). The database can then be loaded and accessed through the simple Flask webapp we provide here.

### Querying

Beyond working programmatically with database requests and tools like [llama-cpp-python](https://github.com/abetlen/llama-cpp-python), I have written a simple extension for the popular [text-generation-webui](https://github.com/oobabooga/text-generation-webui). Simply clone this repository into the extensions folder of your installation of the webui and include citation_llm in your `--extensions` argument. Set the url (IP and port) for your database connection (loaded with context_app.py) and the relevant parameters, and all input will include citation context searching and returns.

### Drawbacks and Considerations

Notably, this approach only allows for comprehensive representation of works with many citations, as it understands and represents scientific knowledge through references to it. Recent or obscure work will be poorly represented or understood. Creating a custom citation dataset is possible, but will still only be capable of representing heavily cited work. Even for heavily cited works, some key statements or facts may go unrepresented due to their niche relevance. However, we believe this approach overall will be effective for general scientific or academic questions and will provide real references for further reading.

### Reproduction

To construct the database, obtain the [dataset](https://ordo.open.ac.uk/articles/dataset/Citation-Context_Dataset_C2D_/6865298/1). Uncompress the tarball and process the raw file with `python3 fix_data.py`- note that while the extension is csv, it is actually tab-separated, binary, and contains a number of non-UTF-8 characters, making it impractical to parse as-is. Once the fixed dataset is obtained, reformat it with `combine_statements.py` to collapse duplicate statements and store them alongside all the references they are supported by. Once the simplified table is available, run `create_database.py`- note that this script can be stopped prematurely to save a partial database, and resumed from a specific step to create a database excluding all the statements before that index. It can take up to several days to process all the available data.

The database can be loaded and with `context_app.py`, which creates a local web server that can be queried with curl or other similar approaches.

```
python3 context_app.py
curl -X POST -H "Content-Type: application/json" -d '{"query":"What species is most closely related to humans?"}' localhost:5000/context
```

