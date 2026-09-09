import hashlib
import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Tracking query parameters to strip during canonicalization
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "ref_src",
    "source",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "trk",
    "trackingId",
    "trk_source",
    "_hsenc",
    "_hsmi",
}


def normalize_canonical_url(url: str) -> str:
    """
    Normalizes a URL to its canonical form:
    1. Strip leading/trailing whitespace.
    2. Lowercase scheme and domain (host).
    3. Remove fragments (#...).
    4. Remove tracking query parameters while preserving structural ones.
    5. Sort query parameters alphabetically.
    6. Remove trailing slash on path (unless it's just '/').
    """
    if not url:
        return ""

    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Normalize path
    path = parsed.path
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    # Filter and sort query parameters
    query_params = []
    for k, v in parse_qsl(parsed.query, keep_blank_values=False):
        if k.lower() not in TRACKING_PARAMS:
            query_params.append((k, v))
    query_params.sort(key=lambda x: x[0])
    query = urlencode(query_params)

    # Reconstruct without fragment
    return urlunparse((scheme, netloc, path, parsed.params, query, ""))


def compute_content_hash(text: str) -> str:
    """
    Computes a deterministic SHA-256 hash over normalized raw content.
    Collapses variable whitespace to detect substantive text changes.
    """
    if not text:
        return hashlib.sha256(b"").hexdigest()

    # Normalize whitespace
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_dedupe_key(
    source_name: str,
    source_listing_id: Optional[str] = None,
    canonical_url: Optional[str] = None,
    content_hash: Optional[str] = None,
) -> str:
    """
    Computes primary deduplication key according to TECH_STACK.md Section 9:
    Priority:
      1. (source_name, source_listing_id) if stable ID exists
      2. canonical_url
      3. content identity fingerprint
    """
    source_clean = source_name.lower().strip()

    if source_listing_id and source_listing_id.strip():
        clean_id = source_listing_id.strip()
        return f"{source_clean}:id:{clean_id}"

    if canonical_url and canonical_url.strip():
        norm_url = normalize_canonical_url(canonical_url)
        url_hash = hashlib.sha256(norm_url.encode("utf-8")).hexdigest()[:24]
        return f"{source_clean}:url:{url_hash}"

    if content_hash:
        return f"{source_clean}:fp:{content_hash[:24]}"

    raise ValueError("Cannot compute dedupe key without source_listing_id, canonical_url, or content_hash.")
