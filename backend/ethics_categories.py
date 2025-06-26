"""
Thomas De Sa - 2025-06-02

Dict of categories and corresponding keywords for categorizing news headlines into ethical categories
"""
ETHICS_CATEGORIES = {
    "labor": [
        "strike", "union", "layoff", "wage", "gig", "picket", "overtime", "worker"
    ],
    "environment": [
        "pollution", "carbon", "climate", '"oil spill"', "recycle", "greenhouse", "deforestation"
    ],
    "privacy": [
        '"data breach"', "GDPR", "hack", "phishing", "spyware", "PII", "encryption", "tracking", "surveillance"
    ],
    "governance": [
        "fraud", "bribery", "lawsuit", "corruption", "whistleblower", "SEC", "scandal", "audit"
    ],
    "diversity": [
        "discrimination", "gender", "race", "DEI", "harassment", "bias", "equality", "inclusion"
    ],
    "human rights": [
        'child labor', 'forced labor', "genocide", "torture", "slavery", "detention", "repression", "censorship"
    ],
    "consumer safety": [
        "recall", "FDA", "toxicity", "defect", "contamination", 'side effect', 'unsafe product'
    ],
    "animal welfare": [
        'animal testing', "cruelty", "fur", "zoo", 'factory farming', "endangered", 'animal abuse'
    ]
}
