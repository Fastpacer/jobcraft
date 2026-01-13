def dedupe_text(text: str) -> str:
    """
    Remove repeated lines from LLM output while preserving order.
    """
    seen = set()
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line not in seen:
            seen.add(line)
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)