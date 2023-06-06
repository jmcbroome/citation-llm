import argparse
import logging
from flask import Flask, request, jsonify
from txtai.embeddings import Embeddings

app = Flask(__name__)

def load_db(path):
    logging.info("Loading embedding database: %s", path)
    db = Embeddings()
    db.load(path)
    logging.info("Database loaded successfully.")
    return db

def get_query_context(query, minscore = 0, retmax = 1):
    sql = f"select text, reference, score from txtai where similar('{query}') and score > {minscore}"
    return db.search(sql,retmax)

def combine_search_results(rvec, include_score = False):
    text = ["The following is a set of snippets containing relevant information to the user's query."]
    references = ["References:"]
    for rd in rvec:
        text.append(rd['text'])
        reftext = rd['reference']
        if include_score:
             reftext += f"; (Score: {rd['score']})"
        references.append(reftext)
    return {"context":"\n".join(text), "references":"\n".join(references)}

def parse_arguments():
    parser = argparse.ArgumentParser(description="Flask app with database path and logging level options")
    parser.add_argument("-d", "--database", required=True, help="Path to the embedding database folder.")
    parser.add_argument("-l", "--loglevel", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser.parse_args()

@app.route('/context', methods=['POST'])
def hello():
    query = request.json.get('query')  # Assuming request data is in JSON format
    if query:
        logging.info("Searching for context for query: %s", query)
        raw_results = get_query_context(query, request.json.get("minscore",0), request.json.get("retmax",1))
        return jsonify(combine_search_results(raw_results, request.json.get("include_score",False)))
    else:
        logging.error("User passed malformed request missing query parameter: %s", query)
        return "Malformed request- please provide a 'query' parameter."

if __name__ == '__main__':
    args = parse_arguments()
    logging.basicConfig(level=args.loglevel)
    db = load_db(args.database)
    app.run(host="0.0.0.0")