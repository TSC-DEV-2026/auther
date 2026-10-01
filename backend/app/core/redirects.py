from urllib.parse import urlparse

from app.core.config import settings
from app.core.exceptions import AppError


def resolve_redirect(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise AppError(400, "redirect_url não permitida")
    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    if origin not in settings.redirect_allowlist:
        raise AppError(400, "redirect_url não permitida")
    return origin
