from __future__ import annotations
import json
import os
import sys
import urllib.error
import urllib.request

from .pattern import Pattern
from .randomize import randomize

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

KNOWN_FIELDS = {"bpm", "bars", "beats_per_bar", "steps_per_beat",
                "hits", "seed", "style"}

SYSTEM_PROMPT = """You are a drum pattern composer. Given a description, return ONLY a JSON object matching this schema:

{
  "bpm": integer 60-200,
  "bars": integer 1-8,
  "beats_per_bar": 4,
  "steps_per_beat": 4,
  "hits": {
    "kick": [step indices],
    "snare": [step indices],
    "hihat": [step indices]
  },
  "style": "short label"
}

Step indices are 16th notes. Valid range: 0 to (bars * 16 - 1).
Every hit index must be inside that range. Kick must include step 0.

Return raw JSON only — no markdown fences, no prose, no explanation."""


def _detect_provider():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _extract_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        nl = t.find("\n")
        t = t[nl + 1:] if nl != -1 else t
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
        t = t.strip()
    i, j = t.find("{"), t.rfind("}")
    if i == -1 or j == -1 or j < i:
        raise ValueError("response contained no JSON object")
    return json.loads(t[i:j + 1])


def _http_post(url, headers, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"network error: {e.reason}")


def _call_anthropic(user_text, prior_error=None):
    model = os.environ.get("MAJESTIC_BEATS_MODEL", DEFAULT_ANTHROPIC_MODEL)
    msg = user_text if not prior_error else (
        f"{user_text}\n\nYour previous attempt was invalid: {prior_error}. "
        "Return ONLY the JSON object, no markdown."
    )
    resp = _http_post(
        ANTHROPIC_URL,
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        body={
            "model": model,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": msg}],
        },
    )
    return resp["content"][0]["text"]


def _call_openai(user_text, prior_error=None):
    model = os.environ.get("MAJESTIC_BEATS_MODEL", DEFAULT_OPENAI_MODEL)
    msg = user_text if not prior_error else (
        f"{user_text}\n\nYour previous attempt was invalid: {prior_error}. "
        "Return ONLY the JSON object, no markdown."
    )
    resp = _http_post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        body={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
        },
    )
    return resp["choices"][0]["message"]["content"]


_CALLERS = {"anthropic": _call_anthropic, "openai": _call_openai}


def pattern_from_prompt(text, *, seed=None, fallback_style="boom-bap",
                        fallback_bpm=100):
    provider = _detect_provider()
    if provider is None:
        raise RuntimeError(
            "no API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY."
        )
    call = _CALLERS[provider]

    last_err = None
    for _ in range(2):
        try:
            raw = call(text, prior_error=last_err)
            data = _extract_json(raw)
            data = {k: v for k, v in data.items() if k in KNOWN_FIELDS}
            pat = Pattern.from_dict(data)
            if seed is not None:
                pat.seed = seed
            return pat
        except Exception as e:
            last_err = str(e)

    print(f"warning: AI generation failed ({last_err}); "
          f"falling back to randomizer", file=sys.stderr)
    return randomize(bpm=fallback_bpm, bars=4, style=fallback_style, seed=seed)
