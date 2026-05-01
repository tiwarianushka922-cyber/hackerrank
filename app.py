import os
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from loader import load_corpus
from classifier import identify_product_area, identify_request_type
from retriever import TFIDFRetriever
from decision import decide_action
from generator import generate_response

app = FastAPI()

# Mount the static directory to serve HTML/CSS/JS
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

# Initialize RAG on startup
corpus_dir = "corpus"
documents = load_corpus(corpus_dir)
retriever = TFIDFRetriever()
retriever.fit(documents)

@app.post("/api/triage")
async def process_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    if 'ticket_id' not in df.columns:
        df['ticket_id'] = [f"TKT-{i+1000}" for i in range(len(df))]
    if 'issue_text' not in df.columns:
        if 'issue' in df.columns:
            df['issue_text'] = df['issue']
        else:
            return JSONResponse({"error": "No 'issue' or 'issue_text' column found in CSV"}, status_code=400)

    results = []
    
    for idx, row in df.iterrows():
        ticket_id = row.get('ticket_id')
        issue_text = str(row.get('issue_text', ''))

        if not issue_text.strip():
            results.append({
                'ticket_id': ticket_id,
                'request_type': 'invalid',
                'product_area': 'Unknown',
                'decision': 'escalate',
                'response': "Escalated: Empty issue provided."
            })
            continue

        req_type = identify_request_type(issue_text)
        prod_area = identify_product_area(issue_text)
        
        retrieved_docs = retriever.search(issue_text, top_k=3)
        top_score = retrieved_docs[0]['score'] if retrieved_docs else 0.0
        
        decision, _ = decide_action(req_type, top_score)
        response = generate_response(decision, retrieved_docs)

        results.append({
            'ticket_id': ticket_id,
            'issue_text': issue_text,
            'request_type': req_type,
            'product_area': prod_area,
            'decision': decision.upper(),
            'response': response
        })

    return {"results": results}
