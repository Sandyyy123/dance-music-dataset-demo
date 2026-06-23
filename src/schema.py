"""
Canonical schema for the dance -> song -> genre -> culture dataset.

Every row links ONE dance/viral move to its signature song(s) and the
cultural context that produced or popularized it. The schema is designed
so the same structure works for a CSV export, a JSON export, and a
relational table that a downstream app can ingest directly.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


# The ordered list of columns. Used by both the CSV writer and the
# JSON writer so the two exports never drift apart.
COLUMNS = [
    "dance_id",
    "dance_name",
    "aka",            # alternate / regional names, pipe-separated
    "category",       # hip-hop / pop / reggae-dancehall / latino / african / viral-challenge
    "origin_region",
    "origin_year",
    "signature_song",
    "song_artist",
    "song_year",
    "genre",
    "platform",       # where it went viral: TikTok / Instagram / club / music-video
    "key_moves",      # short description of the defining movement(s)
    "cultural_context",
    "popularity_tier",  # 1 = global phenomenon, 2 = strong regional, 3 = niche/emerging
    "sources",        # pipe-separated reference URLs / notes
]


@dataclass
class DanceRecord:
    dance_id: str
    dance_name: str
    aka: List[str] = field(default_factory=list)
    category: str = ""
    origin_region: str = ""
    origin_year: Optional[int] = None
    signature_song: str = ""
    song_artist: str = ""
    song_year: Optional[int] = None
    genre: str = ""
    platform: str = ""
    key_moves: str = ""
    cultural_context: str = ""
    popularity_tier: int = 3
    sources: List[str] = field(default_factory=list)

    def to_flat(self) -> dict:
        """Flatten list fields to pipe-joined strings for CSV output."""
        d = asdict(self)
        d["aka"] = "|".join(self.aka)
        d["sources"] = "|".join(self.sources)
        return d

    def to_json_obj(self) -> dict:
        """Keep list fields as real lists for JSON output."""
        return asdict(self)


def validate(record: DanceRecord) -> List[str]:
    """Return a list of validation problems (empty list = valid)."""
    problems = []
    if not record.dance_id:
        problems.append("missing dance_id")
    if not record.dance_name:
        problems.append("missing dance_name")
    if record.popularity_tier not in (1, 2, 3):
        problems.append(f"popularity_tier must be 1-3, got {record.popularity_tier}")
    if record.category and record.category not in {
        "hip-hop", "pop", "reggae-dancehall", "latino", "african", "viral-challenge"
    }:
        problems.append(f"unknown category: {record.category}")
    return problems
