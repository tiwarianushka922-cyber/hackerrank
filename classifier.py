import re

# Strict Output Schema Constants
ALLOWED_TYPES = ['product_issue', 'feature_request', 'bug', 'invalid']
ALLOWED_PRODUCTS = ['HackerRank', 'Claude', 'Visa', 'Out of Scope']

PRODUCT_KEYWORDS = {
    'HackerRank': ['hackerrank', 'code', 'assessment', 'test', 'compiler', 'interview', 'screen', 'greenhouse', 'workday'],
    'Claude': ['claude', 'anthropic', 'api', 'prompt', 'model', 'chat', 'project', 'artifact', 'token'],
    'Visa': ['visa', 'card', 'payment', 'charge', 'fraud', 'merchant', 'credit', 'debit', 'transaction']
}

TYPE_KEYWORDS = {
    'product_issue': ['login', 'password', 'access', 'sso', 'locked', 'account', 'billing', 'charge', 'invoice', 'how to', 'help'],
    'bug': ['bug', 'crash', 'error', 'failing', 'down', 'broken', 'not working'],
    'feature_request': ['feature', 'add', 'would like to see', 'request', 'idea']
}

PROMPT_INJECTION_KEYWORDS = [
    'ignore instructions', 'system prompt', 'unrestricted', 'pretend', 'bypass', 'jailbreak', 'forget previous'
]

def detect_prompt_injection(issue_text):
    """Returns True if malicious text is detected."""
    issue_lower = issue_text.lower()
    for kw in PROMPT_INJECTION_KEYWORDS:
        if kw in issue_lower:
            return True
    return False

def identify_product_area(issue_text, company_val=None):
    """
    Classify product area based on keyword hits or provided company.
    If company is None or unknown, infer from text.
    """
    if company_val and isinstance(company_val, str):
        comp = company_val.strip()
        # Direct match check
        for p in ['HackerRank', 'Claude', 'Visa']:
            if comp.lower() == p.lower():
                return p
    
    # Infer from text if company is missing/invalid
    issue_lower = issue_text.lower()
    scores = {product: 0 for product in ['HackerRank', 'Claude', 'Visa']}
    for product, keywords in PRODUCT_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', issue_lower):
                scores[product] += 1
                
    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0:
        return best_match
        
    return "Out of Scope"

def identify_request_type(issue_text):
    """Classify request type strictly to allowed values."""
    if detect_prompt_injection(issue_text):
        return 'invalid'
        
    issue_lower = issue_text.lower()
    
    # Fraud gets mapped to product_issue but triggers escalation later
    if any(kw in issue_lower for kw in ['fraud', 'stolen', 'unauthorized', 'suspicious', 'hack', 'compromised']):
        return 'product_issue'
        
    scores = {req_type: 0 for req_type in ['product_issue', 'bug', 'feature_request']}
    for req_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', issue_lower):
                scores[req_type] += 1
                
    best_match = max(scores, key=scores.get)
    if scores[best_match] > 0:
        return best_match
        
    # Default fallback
    return 'product_issue'
