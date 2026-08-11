import re

def clean_text(text: str) -> str:
    """
    Cleans raw document text by removing excessive blank lines, null bytes,
    and normalizing spaces while preserving markdown formatting like code blocks and headers.
    """
    if not text:
        return ""
    
    # Replace null characters
    text = text.replace("\x00", "")
    
    # Normalize carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Remove excessive blank lines (more than 2 consecutive newlines -> 2 newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Trim leading/trailing whitespace
    return text.strip()
