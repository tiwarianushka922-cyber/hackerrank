def decide_action(request_type, product_area, issue_text, top_retrieval_score):
    """
    Decide status (replied/escalated) and generate a justification string.
    """
    issue_lower = issue_text.lower()
    
    # 1. Prompt Injection / Invalid queries
    if request_type == 'invalid':
        return 'replied', 'Request contained malicious or invalid instructions (prompt injection).'
        
    # 2. Out of Scope Queries
    if product_area == 'Out of Scope':
        # If it's a completely random question, just reply that it's out of scope
        return 'replied', 'Query is completely outside the supported domains (HackerRank, Claude, Visa).'
        
    # 3. High-risk keywords requiring mandatory escalation
    high_risk_keywords = ['fraud', 'stolen', 'unauthorized', 'suspicious', 'billing', 'charge', 'refund', 'login', 'password', 'locked']
    if any(kw in issue_lower for kw in high_risk_keywords):
        return 'escalated', 'Mandatory escalation due to sensitive/high-risk topic detection (fraud/billing/access).'
        
    # 4. Low confidence / Insufficient info
    CONFIDENCE_THRESHOLD = 0.05
    if top_retrieval_score < CONFIDENCE_THRESHOLD:
        return 'escalated', f'Escalated due to insufficient knowledge base context (score: {top_retrieval_score:.3f}).'
        
    # 5. Default Reply
    return 'replied', 'Sufficient context found in corpus to provide a safe, automated reply.'
