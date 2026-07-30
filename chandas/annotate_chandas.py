#!/usr/bin/env python3
"""Annotate every sloka of the Bhagavata Purana corpus with its chanda (metre).

Runs the Chandojnanam engine (chanda/chanda.py, by Hrishikesh Terdalkar) over
data/bhagavata_purana.json and writes:

  chandas/bhagavata_purana_chandas.json   the full corpus with chandas added
  chandas/chandas_viewer_data.json        a lean flat payload for index.html

The engine is fed each sloka's pada lines joined by newline, which is the shape
identify_from_text() expects.

Identification is tiered, because the engine raises IndexError rather than
reporting failure when no line matches a known metre:

  exact  verse=True, fuzzy=False   the metre was matched outright
  fuzzy  verse=True, fuzzy=True    nearest metre by edit distance, flagged
  none   verse=False               no metre, but laghu-guru and gana are kept

The `match` field records which tier produced the answer, so a fuzzy guess is
never mistaken for a definite identification. Laghu-guru and gana come from the
line-level analysis, which never fails, so prosodic data is retained even where
the metre is unidentified.

Usage:
    python chandas/annotate_chandas.py [--limit N]
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "chandas"))

from chanda import Chanda  # noqa: E402  (needs the path set above)

DATA_PATH = ROOT / "chandas" / "chanda" / "data"
CORPUS_IN = ROOT / "data" / "bhagavata_purana.json"
CORPUS_OUT = ROOT / "chandas" / "bhagavata_purana_chandas.json"
VIEWER_OUT = ROOT / "chandas" / "chandas_viewer_data.json"


def line_prosody(line_results):
    """Pull laghu-guru and gana strings out of the engine's line results."""
    guru_laghu, gana = [], []
    for lr in line_results:
        result = lr["result"]
        guru_laghu.append("".join(result["display_lg"]))
        gana.append(result["display_gana"])
    return guru_laghu, gana


def chanda_names(verse_results):
    """Metre name(s) for each verse the engine returned.

    A sloka of 5 or 6 padas comes back as two verse entries, because the engine
    groups four lines to a verse. Reading only the first would silently discard
    the remainder, so every entry is collected.
    """
    names = []
    for verse in verse_results:
        if verse.get("chanda"):
            names.append(" / ".join(verse["chanda"][0]))
    return names


def identify(engine, lines):
    """Identify the metre of one sloka. Returns a dict, never raises.

    Falls back through the tiers described in the module docstring.
    """
    text = "\n".join(lines)

    for match, fuzzy in (("exact", False), ("fuzzy", True)):
        try:
            result = engine.identify_from_text(text, verse=True, fuzzy=fuzzy)
        except Exception:                      # noqa: BLE001  (engine raises IndexError)
            continue
        names = chanda_names(result["result"]["verse"])
        if not names:
            continue
        guru_laghu, gana = line_prosody(result["result"]["line"])
        return {
            "chanda": " | ".join(names) if len(names) > 1 else names[0],
            "chanda_parts": names if len(names) > 1 else None,
            "match": match,
            "guru_laghu": guru_laghu,
            "gana": gana,
        }

    # No metre found. Line-level analysis still works, so keep the prosody.
    try:
        result = engine.identify_from_text(text, verse=False, fuzzy=False)
        guru_laghu, gana = line_prosody(result["result"]["line"])
    except Exception:                          # noqa: BLE001
        guru_laghu, gana = [], []

    return {
        "chanda": None,
        "chanda_parts": None,
        "match": "none",
        "guru_laghu": guru_laghu,
        "gana": gana,
    }


def annotate(limit=None):
    corpus = json.loads(CORPUS_IN.read_text(encoding="utf-8"))
    engine = Chanda(data_path=str(DATA_PATH))

    records = [r for sk in corpus["skandhas"]
               for ad in sk["adhyayas"]
               for r in ad["slokas"]]
    if limit:
        records = records[:limit]

    stats = collections.Counter()
    started = time.time()

    for i, rec in enumerate(records, 1):
        if rec["text"] is None:                # vachana-only record, no verse
            rec["chandas"] = {"chanda": None, "chanda_parts": None,
                              "match": "not_applicable",
                              "guru_laghu": [], "gana": []}
            stats["not_applicable"] += 1
            continue

        lines = [p["devanagari"] for p in rec["text"]["padas"]]
        rec["chandas"] = identify(engine, lines)
        stats[rec["chandas"]["match"]] += 1

        if i % 2000 == 0:
            print(f"  {i:>6,}/{len(records):,} ...", flush=True)

    elapsed = time.time() - started
    print(f"annotated {len(records):,} records in {elapsed:.1f}s "
          f"({elapsed / max(len(records), 1) * 1000:.1f} ms each)")
    return corpus, records, stats


def build_viewer_payload(corpus):
    """Flatten to the minimum the viewer needs, so the page loads quickly."""
    rows = []
    for sk in corpus["skandhas"]:
        for ad in sk["adhyayas"]:
            title = ad["titles"]["tagare"] or ad["titles"]["anand_aadhar"]
            for rec in ad["slokas"]:
                ch = rec["chandas"]
                rows.append({
                    "id": rec["id"],
                    "skandha": rec["skandha"],
                    "adhyaya": rec["adhyaya"],
                    "sloka": rec["sloka"],
                    "adhyaya_title": title,
                    "chanda": ch["chanda"],
                    "match": ch["match"],
                    "vachana": (rec["vachana"] or {}).get("devanagari"),
                    "padas": [p["devanagari"] for p in rec["text"]["padas"]] if rec["text"] else [],
                    "guru_laghu": ch["guru_laghu"],
                    "gana": ch["gana"],
                })
    return rows


def report(corpus, records, stats):
    print("\nmatch tiers:")
    for k in ("exact", "fuzzy", "none", "not_applicable"):
        if stats[k]:
            print(f"  {k:<16} {stats[k]:>6,}  ({stats[k] / len(records):.1%})")

    named = collections.Counter(
        r["chandas"]["chanda"] for r in records if r["chandas"]["chanda"])
    print(f"\ndistinct metres identified: {len(named)}")
    for name, n in named.most_common(15):
        print(f"  {n:>6,}  {name}")

    by_skandha = collections.defaultdict(collections.Counter)
    for sk in corpus["skandhas"]:
        for ad in sk["adhyayas"]:
            for r in ad["slokas"]:
                if "chandas" in r:     # absent for the tail of a --limit run
                    by_skandha[sk["skandha"]][r["chandas"]["match"]] += 1
    print(f"\n{'skandha':>8} {'slokas':>7} {'exact':>7} {'fuzzy':>7} {'none':>6}")
    for s in sorted(by_skandha):
        c = by_skandha[s]
        total = sum(c.values())
        print(f"{s:>8} {total:>7,} {c['exact']:>7,} {c['fuzzy']:>7,} {c['none']:>6,}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=None,
                    help="annotate only the first N records (for a quick check)")
    args = ap.parse_args()

    corpus, records, stats = annotate(limit=args.limit)

    corpus["structure"]["levels"] = ["skandha", "adhyaya", "sloka", "pada"]
    corpus["chandas"] = {
        "engine": "Chandojnanam (chanda.py) by Hrishikesh Terdalkar",
        "engine_upstream": "https://github.com/hrishikeshrt/chandojnanam",
        "engine_license": "AGPL-3.0",
        "vendored_from": "https://github.com/imradhe/chanda",
        "match_tiers": {
            "exact": "matched outright (verse=True, fuzzy=False)",
            "fuzzy": "nearest metre by edit distance (verse=True, fuzzy=True)",
            "none": "no metre matched; laghu-guru and gana still recorded",
            "not_applicable": "record has no verse text (vachana-only)",
        },
        "counts": dict(stats),
    }

    if not args.limit:
        CORPUS_OUT.write_text(
            json.dumps(corpus, ensure_ascii=False, indent=1), encoding="utf-8")
        VIEWER_OUT.write_text(
            json.dumps(build_viewer_payload(corpus), ensure_ascii=False),
            encoding="utf-8")
        for p in (CORPUS_OUT, VIEWER_OUT):
            print(f"wrote {p.relative_to(ROOT)}  {p.stat().st_size / 1e6:.1f} MB")

    report(corpus, records, stats)


if __name__ == "__main__":
    main()
