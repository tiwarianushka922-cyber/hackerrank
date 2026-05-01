import os
import pandas as pd
import glob

def load_tickets(csv_path):
    """
    Load support tickets from a CSV file.
    Expects columns like 'issue_text' or 'issue' and optionally 'ticket_id'.
    """
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found.")
        return pd.DataFrame()
        
    df = pd.read_csv(csv_path)
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Handle missing ticket_id
    if 'ticket_id' not in df.columns:
        df['ticket_id'] = [f"TKT-{i+1000}" for i in range(len(df))]
        
    # Standardize issue text column
    if 'issue_text' not in df.columns:
        if 'issue' in df.columns:
            df['issue_text'] = df['issue']
        else:
            print("Error: Could not find 'issue' or 'issue_text' column in CSV.")
            return pd.DataFrame()
            
    return df

def load_corpus(corpus_dir):
    """
    Load all documents from the corpus directory.
    Splits text into paragraph chunks to create a searchable index.
    Returns a list of dictionaries: [{'doc_id': str, 'text': str, 'source': str}]
    """
    documents = []
    
    if not os.path.exists(corpus_dir):
        print(f"Warning: Corpus directory '{corpus_dir}' not found. Creating empty dir.")
        os.makedirs(corpus_dir, exist_ok=True)
        return documents

    # Search for text files
    file_paths = glob.glob(os.path.join(corpus_dir, '**', '*.txt'), recursive=True)
    file_paths.extend(glob.glob(os.path.join(corpus_dir, '**', '*.md'), recursive=True))
    
    doc_id_counter = 1
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic chunking by double newline (paragraphs)
        chunks = [chunk.strip() for chunk in content.split('\n\n') if len(chunk.strip()) > 30]
        
        source_name = os.path.basename(file_path)
        for chunk in chunks:
            documents.append({
                'doc_id': f"DOC-{doc_id_counter}",
                'text': chunk,
                'source': source_name
            })
            doc_id_counter += 1
            
    return documents
