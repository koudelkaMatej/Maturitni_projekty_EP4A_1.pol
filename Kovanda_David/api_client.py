# -*- coding: utf-8 -*-
"""HTTP klient pro komunikaci s lokálním Flask backendem."""

from typing import Tuple, Any, Dict
import requests

BASE_URL = "http://127.0.0.1:5000/api"


def _headers(token: str = ""):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api_get(path: str, token: str = "") -> Tuple[bool, Any]:
    try:
        resp = requests.get(f"{BASE_URL}{path}", headers=_headers(token), timeout=5)
    except Exception:
        return False, "API není dostupné"
    if resp.status_code >= 400:
        try:
            msg = resp.json().get("error", resp.text)
        except Exception:
            msg = resp.text
        return False, msg
    try:
        return True, resp.json()
    except Exception:
        return False, "Neplatná odpověď API"


def api_post(path: str, data: Dict[str, Any], token: str = "") -> Tuple[bool, Any]:
    try:
        resp = requests.post(f"{BASE_URL}{path}", json=data, headers=_headers(token), timeout=5)
    except Exception:
        return False, "API není dostupné"
    if resp.status_code >= 400:
        try:
            msg = resp.json().get("error", resp.text)
        except Exception:
            msg = resp.text
        return False, msg
    try:
        return True, resp.json()
    except Exception:
        return False, "Neplatná odpověď API"
