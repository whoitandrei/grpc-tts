import pytest

from api_service.app.validation import validate_text


def test_validate_text_accepts_supported_language():
    validate_text("Hello", "en")


@pytest.mark.parametrize(
    ("text", "language", "message"),
    [
        ("", "en", "Text cannot be empty"),
        ("   ", "en", "Text cannot be empty"),
        ("x" * 501, "en", "Text cannot exceed 500 characters"),
        ("Hello", "ru", "Only EN are supported now"),
    ],
)
def test_validate_text_rejects_invalid_input(text: str, language: str, message: str):
    with pytest.raises(ValueError, match=message):
        validate_text(text, language)
