import logging
import pandas as pd
import re
from loader import load_tickets, load_corpus
from classifier import identify_product_area, identify_request_type
from retriever import TFIDFRetriever
from decision import decide_action
from generator import generate_response

def setup_logging():
    logging.basicConfig(
        filename='app.log',  # Renamed so it doesn't conflict with your AI Chat Transcript 'log.txt'
        filemode='w',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def split_requests(issue_text):
    """Split text into sentences to process multiple requests."""
    # Simple split by punctuation usually found between requests
    sentences = re.split(r'(?<=[.!?])\s+', issue_text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]

def main():
    setup_logging()
    logging.info("Starting Advanced Offline RAG Support Triage Agent...")

    corpus_dir = "corpus"
    csv_path = "support_tickets/support_tickets.csv"
    output_path = "support_tickets/output.csv"

    logging.info(f"Loading corpus documents from '{corpus_dir}/'...")
    documents = load_corpus(corpus_dir)
    
    logging.info(f"Loading tickets from '{csv_path}'...")
    tickets_df = load_tickets(csv_path)
    if tickets_df.empty: return

    logging.info("Initializing TF-IDF Retriever...")
    retriever = TFIDFRetriever()
    retriever.fit(documents)

    results = []

    logging.info("Starting ticket processing pipeline...")
    for idx, row in tickets_df.iterrows():
        company_val = row.get('company', None)
        issue_text = str(row.get('issue_text', '')).strip()

        if not issue_text:
            results.append({
                'status': 'escalated',
                'product_area': 'Unknown',
                'response': "Escalated: Empty issue provided.",
                'justification': "Empty input text.",
                'request_type': 'invalid'
            })
            continue

        # Classify
        req_type = identify_request_type(issue_text)
        prod_area = identify_product_area(issue_text, company_val)
        
        # Multi-request retrieval logic
        sub_requests = split_requests(issue_text)
        if not sub_requests: sub_requests = [issue_text]
        
        all_retrieved = []
        max_score = 0.0
        
        for req in sub_requests:
            docs = retriever.search(req, top_k=2)
            all_retrieved.extend(docs)
            if docs and docs[0]['score'] > max_score:
                max_score = docs[0]['score']
                
        # Remove duplicates
        unique_docs = {d['document']['text']: d for d in all_retrieved}.values()
        sorted_docs = sorted(list(unique_docs), key=lambda x: x['score'], reverse=True)

        # Decide
        status, justification = decide_action(req_type, prod_area, issue_text, max_score)

        # Generate
        response = generate_response(status, req_type, prod_area, sorted_docs)

        logging.info(f"[{status.upper()}] {prod_area} | {req_type} -> {justification}")

        results.append({
            'status': status,
            'product_area': prod_area,
            'response': response,
            'justification': justification,
            'request_type': req_type
        })

    logging.info(f"Writing strictly formatted results to '{output_path}'...")
    output_df = pd.DataFrame(results)
    # Ensure exact column order
    output_df = output_df[['status', 'product_area', 'response', 'justification', 'request_type']]
    output_df.to_csv(output_path, index=False)
    logging.info("Pipeline complete.")

if __name__ == "__main__":
    main()
