def validate_text(text: str) -> None:
    if not text.strip():
        raise ValueError("Text cannot be empty")

    if len(text) > 500:
        raise ValueError("Text cannot exceed 500 characters")
