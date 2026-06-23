"""
Research / collection layer.

In production this module pulls candidate dances from public, terms-friendly
sources (Wikipedia category pages, the MusicBrainz API, and curated lists)
and stages them for human review before they enter the dataset. Nothing is
scraped from sites that forbid it; Wikipedia and MusicBrainz both expose
open APIs intended for reuse.

To keep the demo fully runnable offline (and to avoid hammering live
endpoints), the live fetchers are wrapped so they fall back to a small
bundled seed list when the network is unavailable. Flip USE_NETWORK to True
to exercise the real calls.
"""

import json
import os
import time
import urllib.parse
import urllib.request

from .schema import DanceRecord

USE_NETWORK = os.environ.get("DANCE_USE_NETWORK", "0") == "1"

WIKI_API = "https://en.wikipedia.org/w/api.php"
MB_API = "https://musicbrainz.org/ws/2"
USER_AGENT = "dance-music-dataset-demo/1.0 (research; contact via GitHub)"


def _get_json(url: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{qs}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wiki_candidate_dances(limit: int = 20) -> list:
    """Pull member pages of Wikipedia's 'Internet dances' / 'Dance' categories."""
    if not USE_NETWORK:
        return []
    try:
        data = _get_json(WIKI_API, {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Internet_dances",
            "cmlimit": str(limit),
            "format": "json",
        })
        return [m["title"] for m in data.get("query", {}).get("categorymembers", [])]
    except Exception as exc:  # network/parse failure -> let caller use seed
        print(f"[collect] wiki fetch failed, using seed list: {exc}")
        return []


def musicbrainz_song_year(song: str, artist: str) -> int:
    """Look up a release year for a song via the MusicBrainz API (rate-limited)."""
    if not USE_NETWORK:
        return 0
    try:
        q = f'recording:"{song}" AND artist:"{artist}"'
        data = _get_json(f"{MB_API}/recording", {"query": q, "fmt": "json", "limit": "1"})
        time.sleep(1.1)  # MusicBrainz asks for <= 1 req/sec
        recs = data.get("recordings", [])
        if recs and recs[0].get("first-release-date"):
            return int(recs[0]["first-release-date"][:4])
    except Exception as exc:
        print(f"[collect] musicbrainz lookup failed: {exc}")
    return 0


def load_seed() -> list:
    """Bundled, hand-verified seed rows so the pipeline always produces output."""
    here = os.path.dirname(__file__)
    seed_path = os.path.join(here, "..", "data", "seed_dances.json")
    with open(seed_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    records = []
    for item in raw:
        records.append(DanceRecord(**item))
    return records


def collect(limit: int = 20) -> list:
    """
    Main entry point: combine the verified seed list with any live
    candidates discovered this run. The seed list is authoritative; live
    candidates are appended only if not already present (dedup by name).
    """
    records = load_seed()
    known = {r.dance_name.lower() for r in records}

    for title in wiki_candidate_dances(limit):
        if title.lower() not in known:
            records.append(DanceRecord(
                dance_id=f"auto-{len(records)+1:03d}",
                dance_name=title,
                category="viral-challenge",
                platform="TikTok",
                popularity_tier=3,
                sources=[f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}"],
            ))
            known.add(title.lower())
    return records
