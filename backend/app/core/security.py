import re
from typing import Tuple, List

class SecurityGatekeeper:
    """
    Production Prompt Injection Defense & Data Sanitizer.
    Enforces DATA != INSTRUCTION boundary on external retrieved text.
    """
    
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"system\s+prompt",
        r"disregard\s+above",
        r"reveal\s+(the\s+)?secret",
        r"you\s+are\s+now\s+a",
        r"bypass\s+safety",
        r"do\s+anything\s+now",
        r"DAN\s+mode"
    ]

    @classmethod
    def sanitize_retrieved_text(cls, raw_text: str) -> Tuple[str, bool, List[str]]:
        """
        Sanitizes text retrieved from untrusted web sources.
        Returns: (sanitized_text, is_clean, detected_attacks)
        """
        detected = []
        sanitized = raw_text
        
        for pattern in cls.INJECTION_PATTERNS:
            matches = re.findall(pattern, sanitized, flags=re.IGNORECASE)
            if matches:
                detected.append(f"Pattern match: '{pattern}'")
                # Neutralize matching suspicious string
                sanitized = re.sub(pattern, "[FLAGGED_INJECTION_REMOVED]", sanitized, flags=re.IGNORECASE)

        is_clean = len(detected) == 0
        
        # Enforce secure XML container wrapping for instruction isolation
        wrapped_text = f"<untrusted_retrieved_data trust_level='unverified'>\n{sanitized}\n</untrusted_retrieved_data>"
        
        return wrapped_text, is_clean, detected
