def generate_response(status, request_type, product_area, retrieved_docs):
    """
    Generates a safe response based on status and edge-cases.
    """
    if request_type == 'invalid':
        return "Your request could not be processed due to invalid or unsupported instructions."
        
    if product_area == 'Out of Scope':
        return "I'm sorry, but your query is outside the scope of my supported domains (HackerRank, Claude, Visa)."

    if status == 'escalated':
        return "Your request has been escalated to our human support team. They will contact you shortly."
        
    if not retrieved_docs:
        return "I'm sorry, I couldn't find any relevant information to help with your query. Escalating to human support."
        
    # Extractive Generation for valid replies
    response_parts = []
    
    # We take the top 1 or 2 most relevant chunks
    for res in retrieved_docs[:2]:
        text = res['document']['text']
        source = res['document']['source']
        clean_text = " ".join(text.split())
        response_parts.append(f"{clean_text} (Source: {source})")
        
    return " ".join(response_parts)
