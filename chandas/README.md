# Chandas annotation of the Bhāgavata Purāṇa

Metre (chanda) identification for all 14,088 slokas of the corpus in this repo, using the
Chandojñānam engine, plus a DataTables HTML viewer.

This mirrors what the [`imradhe/chanda`](https://github.com/imradhe/chanda) repo does for the
Rāmāyaṇa, adapted to the Bhāgavata corpus and its `skandha` / `adhyaya` / `sloka` hierarchy.

## Files

| Path | What it is |
|---|---|
| `annotate_chandas.py` | Runs the engine over `../data/bhagavata_purana.json` |
| `bhagavata_purana_chandas.json` | 46 MB, the annotated corpus (full corpus plus a `chandas` block per sloka) |
| `chandas_viewer_data.json` | 9.6 MB, lean flat payload the viewer fetches |
| `index.html` | The viewer |
| `chanda/` | Vendored Chandojñānam engine and its metre definition CSVs |
| `ATTRIBUTION.md` | Provenance and licence of the vendored engine |

## Running it

```bash
./.venv/bin/pip install python-Levenshtein sanskrit-text indic_transliteration
```

```bash
./.venv/bin/python chandas/annotate_chandas.py
```

It takes about 16 seconds for the whole corpus, roughly 1.1 ms per sloka. Pass
`--limit N` for a quick check without writing the output files.

## Viewing it

The page fetches JSON, so it needs to be served over HTTP rather than opened as a file:

```bash
python3 -m http.server 8765 --directory chandas
```

Then open `http://localhost:8765/index.html`.

The viewer gives you Skandha / Chanda / Match filters, a free-text search, and a
transliteration dropdown covering IAST, ITRANS, Harvard-Kyoto, SLP1, Velthuis and nine
Indic scripts, applied on hover over the Text and Chanda columns.

## Results

| Match tier | Slokas | Share |
|---|---|---|
| `exact` | 12,430 | 88.2% |
| `fuzzy` | 1,143 | 8.1% |
| `none` | 515 | 3.7% |
| `not_applicable` | 1 | the single vachana-only record, which has no verse |

**122 distinct metres** were identified. The twenty most common:

| Chanda | Slokas |
|---|---|
| अनुष्टुभ् | 10,306 |
| वसन्ततिलका / सिंहोन्नता / सिंहोद्धता / उद्धर्षिणी | 684 |
| वंशस्थ / वंशस्थविल / वंशस्तनित | 476 |
| इन्द्रवज्रा | 348 |
| इन्द्रवंशा | 303 |
| इन्द्रवंशा / वंशस्थ / वंशस्थविल / वंशस्तनित | 242 |
| उपेन्द्रवज्रा | 224 |
| इन्द्रवज्रा / उपेन्द्रवज्रा | 198 |
| नाराचिका | 87 |
| वंशस्थ / वंशस्थविल / वंशस्तनित / इन्द्रवंशा | 64 |
| वक्त्र | 43 |
| मन्दाक्रान्ता | 34 |
| नर्दटक / नर्कुटक | 28 |
| औपच्छन्दसिक / पुष्पिताग्रा | 27 |
| पञ्चचामर / प्रमाणिका / नगस्वरूपिणी | 27 |
| उपेन्द्रवज्रा / इन्द्रवज्रा | 26 |
| भुजङ्गसङ्गता | 21 |
| मालिनी | 21 |
| मदनललिता | 20 |
| स्वागता | 20 |

A `/` separated label means the engine could not disambiguate between metres with identical
laghu-guru patterns. That is a genuine ambiguity in the pattern, not a failure.

### Per skandha

| Skandha | Slokas | exact | fuzzy | none |
|---|---|---|---|---|
| 1 | 813 | 734 | 75 | 4 |
| 2 | 391 | 341 | 49 | 1 |
| 3 | 1,413 | 1,267 | 140 | 6 |
| 4 | 1,446 | 1,296 | 146 | 3 |
| 5 | 660 | 130 | 84 | **446** |
| 6 | 851 | 728 | 98 | 25 |
| 7 | 750 | 695 | 53 | 2 |
| 8 | 933 | 849 | 82 | 2 |
| 9 | 965 | 921 | 41 | 3 |
| 10 | 3,936 | 3,686 | 238 | 12 |
| 11 | 1,366 | 1,270 | 92 | 4 |
| 12 | 565 | 513 | 45 | 7 |

Skandha 5 is the obvious outlier, with 446 of 660 slokas unmatched. That is the expected
result rather than a defect: much of skandha 5 is **gadya** (prose), which has no metre. It
is a useful sanity check that the pipeline is behaving.

## Record shape

Each sloka in `bhagavata_purana_chandas.json` gains a `chandas` block alongside the fields
documented in the top-level readme:

```jsonc
{
  "id": "1.1.3",
  "skandha": 1, "adhyaya": 1, "sloka": 3,
  "text": { "padas": [ ... ], "devanagari": "...", ... },
  "chandas": {
    "chanda": "द्रुतविलम्बित / हरिणप्लुत / हरिणप्लुता",
    "chanda_parts": null,      // set when a sloka spans more than one verse group
    "match": "exact",          // exact | fuzzy | none | not_applicable
    "guru_laghu": ["लललगललगललगलग", "लललगललगललगलग", "लललगललगललगलग", "लललगललगललगलग"],
    "gana": ["नभभर", "नभभर", "नभभर", "नभभर"]
  }
}
```

`guru_laghu` and `gana` have one entry per pāda line.

## Choices worth knowing about

**Tiered identification instead of error strings.** The engine raises `IndexError` rather
than reporting failure when no line matches a known metre. The Rāmāyaṇa run recorded that as
the metre, leaving 556 records whose `chanda` field literally contains
`"Error: list index out of range"`. Here identification instead falls through three tiers:

1. `verse=True, fuzzy=False` gives `match: "exact"`
2. `verse=True, fuzzy=True` gives `match: "fuzzy"`, a nearest match by edit distance that
   should be read as a suggestion, not a determination
3. otherwise `chanda: null` with `match: "none"`

Line-level analysis never fails, so `guru_laghu` and `gana` are recorded even in tier 3. A
metre being unidentifiable does not cost you the prosody.

**All verse groups are read.** The engine groups four lines to a verse, so a sloka of five or
six pādas comes back as two verse entries. Reading only `verse_results[0]`, as the Rāmāyaṇa
script did, silently discards the rest. Those slokas get a `/` joined `chanda` and a populated
`chanda_parts`. Three records in the corpus are affected.

**`restructure.py` is deliberately not ported.** That script merges single-pāda slokas into
the following sloka to repair a Rāmāyaṇa segmentation artifact. The Bhāgavata corpus is
already segmented by the source edition's own numbering, so running it would corrupt the
structure.

**The annotated corpus duplicates the base corpus.** `bhagavata_purana_chandas.json` is the
full corpus plus annotations, which is self-contained and matches the shape of
`slokas_with_chanda.json` in the chanda repo, at the cost of 46 MB that largely repeats
`../data/bhagavata_purana.json`. If repo size matters more than self-containment, the
annotations alone keyed by `id` would be a few MB.
