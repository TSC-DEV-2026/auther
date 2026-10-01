import pytest

from app.core.exceptions import AppError
from app.core.redirects import resolve_redirect


def test_origem_allowlisted():
    assert resolve_redirect("http://localhost:5174/reset-password") == "http://localhost:5174"


def test_origem_fora_da_lista():
    with pytest.raises(AppError) as caught:
        resolve_redirect("https://evil.example/reset-password")
    assert caught.value.status_code == 400
