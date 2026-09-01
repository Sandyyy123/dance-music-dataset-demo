> **⚠️ Proprietary — All Rights Reserved.** © 2026 Sandeep Grover. This repository is licensed to Sandeep Grover and may **not** be used, run, copied, modified, distributed, or used to train models without prior written permission. Public visibility does not grant a license. See [LICENSE](LICENSE).

---

# dance-music-dataset-demo

A small, runnable research-to-dataset pipeline that links **popular dances and
viral moves** to their **signature music**, **genre**, and **cultural context**.
Built as a working sample for a structured-dataset research engagement.

The goal of the real project: research and document a comprehensive list of
popular dances, viral trends, and iconic moves, then produce a clean structured
dataset that a downstream system can use to map each dance move to its
associated song and cultural background, across hip-hop, pop, reggae/dancehall,
latino, and African music.

## What it produces

Two synchronized exports from one canonical schema:

| File | Format | Use |
|------|--------|-----|
| `data/dance_music_dataset.csv` | flat, pipe-joined lists | spreadsheets, app import |
| `data/dance_music_dataset.json` | nested lists preserved | API / app ingestion |

### Schema (one row = one dance/move)

`dance_id, dance_name, aka, category, origin_region, origin_year,
signature_song, song_artist, song_year, genre, platform, key_moves,
cultural_context, popularity_tier, sources`

- **category**: hip-hop / pop / reggae-dancehall / latino / african / viral-challenge
- **popularity_tier**: 1 = global phenomenon, 2 = strong regional, 3 = niche/emerging
- **sources**: reference URLs so every row is traceable and reviewable

## Architecture

```
src/schema.py        canonical columns + DanceRecord dataclass + validation
src/collect.py       research layer: Wikipedia + MusicBrainz APIs, with an
                     offline seed fallback so it always runs
src/build_dataset.py validates every row, writes synchronized CSV + JSON,
                     prints a coverage summary
data/seed_dances.json  hand-verified starter rows across all 5 genres
```

Data sourcing uses **public, reuse-friendly APIs only** (Wikipedia and
MusicBrainz). No site that prohibits scraping is touched. Live lookups are
rate-limited (MusicBrainz at <= 1 request/second per their guidelines), and
every candidate is staged for human verification before it enters the dataset.

## Setup and run

```bash
git clone https://github.com/Sandyyy123/dance-music-dataset-demo.git
cd dance-music-dataset-demo
python -m src.build_dataset        # offline, uses the verified seed list
```

Enable the live research layer (Wikipedia + MusicBrainz):

```bash
DANCE_USE_NETWORK=1 python -m src.build_dataset
```

## How this scales to the full deliverable

The seed list ships with 8 representative rows spanning every genre the brief
names. The production run expands this to the agreed row count by pulling
candidate dances from Wikipedia dance categories and viral-trend trackers,
enriching release years via MusicBrainz, and routing each candidate through
the same `validate()` gate before export. Every row keeps its `sources` so the
client can audit provenance.

---

Author: Dr. Sandeep Grover. PhD in Data Science; structured-data research,
scraping, and dataset engineering.
