import re
import logging

logger = logging.getLogger(__name__)

# Pattern sets for dynamic intent detection (no hardcoded questions)
PATTERNS = {
    "COMPARISON": [
        r"\bdifference\b", r"\bversus\b", r"\bvs\.?\b", r"\bcompare\b", r"\bcomparison\b",
        r"\bbetter\b", r"\binstead of\b", r"\bor\b.*\bwhich\b"
    ],
    "HOWTO": [
        r"\bhow (do|can|to|should|would) i\b", r"\bhow to\b", r"\bstep(s)?\b",
        r"\bguide\b", r"\bprocedure\b", r"\bconfigure\b", r"\bset up\b",
        r"\bcreate\b", r"\binstall\b", r"\bregister\b", r"\bdeploy\b", r"\bpush\b"
    ],
    "TROUBLESHOOTING": [
        r"\bwhy (is|does|did|my)\b", r"\bfail(ed|s|ing)?\b", r"\berror\b",
        r"\bstuck\b", r"\btroubleshoot\b", r"\bfix\b", r"\bdebug\b", r"\bissue\b",
        r"\bproblem\b", r"\bnot working\b", r"\blogs?\b"
    ],
    "CONFIG_CODE": [
        r"\.gitlab-ci\.yml\b", r"\byaml\b", r"\bsyntax\b", r"\bexample\b",
        r"\bcode\b", r"\bscript\b", r"\bcommand\b", r"\bcli\b", r"\bfile\b"
    ],
    "API_AUTH": [
        r"\bapi\b", r"\brest\b", r"\btoken\b", r"\bauthentication\b", r"\bauthorize\b",
        r"\bendpoint\b", r"\bheader\b", r"\baccess token\b", r"\bdeploy token\b"
    ],
    "SECURITY": [
        r"\bsast\b", r"\bdast\b", r"\bsecurity\b", r"\bvulnerab(ility|ilities)\b",
        r"\bsecret detection\b", r"\bcontainer scanning\b", r"\blicense scanning\b"
    ],
    "DEFINITION": [
        r"\bwhat (is|are)\b", r"\bdefine\b", r"\bmeaning\b", r"\boverview\b",
        r"\bconcept\b", r"\bdescription\b", r"\bexplain\b"
    ]
}

def detect_query_intent(query: str) -> str:
    """
    Dynamically classifies a user question into a functional technical intent category.
    Returns one of: COMPARISON, HOWTO, TROUBLESHOOTING, CONFIG_CODE, API_AUTH, SECURITY, DEFINITION, GENERAL.
    """
    q_lower = query.strip().lower()
    
    for intent, regex_list in PATTERNS.items():
        for pattern in regex_list:
            if re.search(pattern, q_lower):
                logger.info(f"Detected intent '{intent}' for query: '{query}'")
                return intent

    # If query is short (4 words or fewer without question mark), default to DEFINITION overview
    words = q_lower.split()
    if len(words) <= 4 and "?" not in q_lower:
        return "DEFINITION"
        
    return "GENERAL"
