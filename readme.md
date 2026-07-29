# Śrīmad Bhāgavata Purāṇa: verse-aligned corpus

A single JSON record of the **complete Bhāgavata Purāṇa**: the Devanāgarī text sloka by
sloka with its structure intact, plus **two independent English translations** aligned to
every verse.

```
12 skandhas  →  335 adhyāyas  →  14,088 ślokas  →  pādas
```

The four hierarchy levels are named `skandha`, `adhyaya`, `sloka` and `pada` throughout the
JSON. Because `sloka` is the verse *number*, the verse *text* lives under `text`.

## Files

| Path | What it is |
|---|---|
| [`notebooks/bhagavata_purana_pipeline.ipynb`](notebooks/bhagavata_purana_pipeline.ipynb) | The pipeline: downloads, parses, scrapes, validates, writes the JSON |
| `data/bhagavata_purana.json` | **The deliverable**, full nested corpus |
| `data/bhagavata_purana_flat.jsonl` | One sloka per line, keyed `skandha`/`adhyaya`/`sloka` |
| `data/raw/` | Cached upstream pages, so re-runs make no network requests |

## Quick start

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
```

```bash
./.venv/bin/jupyter notebook notebooks/bhagavata_purana_pipeline.ipynb
```

Reading the result:

```python
import json, pandas as pd

corpus = json.load(open("data/bhagavata_purana.json"))
df = pd.read_json("data/bhagavata_purana_flat.jsonl", lines=True)

print(df.loc[df.id == "10.14.8", ["devanagari", "translation_tagare"]].to_dict("records"))

# nested access
sk10 = next(s for s in corpus["skandhas"] if s["skandha"] == 10)
a14  = next(a for a in sk10["adhyayas"] if a["adhyaya"] == 14)
v8   = next(v for v in a14["slokas"] if v["sloka"] == 8)
print(v8["text"]["devanagari"])
```

## Structure and IDs

Every sloka has a stable ID `<skandha>.<adhyaya>.<sloka>`, so `10.14.8` is skandha 10,
adhyāya 14, śloka 8, matching the canonical reference used across the literature.

```jsonc
{
  "id": "1.1.6",
  "skandha": 1, "adhyaya": 1, "sloka": 6,
  "type": "sloka",                   // or "vachana_only"
  "vachana": {                       // separated out, NOT part of the verse
    "type": "speaker",
    "devanagari": "ऋषय ऊचुः ।",
    "iast": "ṛṣaya ūcuḥ |",
    "itrans": "R^iShaya UchuH |"
  },
  "text": {
    "devanagari": "त्वया खलु पुराणानि सेतिहासानि चानघ\nआख्यातान्यप्यधीतानि धर्मशास्त्राणि यान्युत",
    "iast": "…", "itrans": "…",
    "devanagari_flat": "…",          // same text as one line
    "iast_flat": "…",
    "padas": [                       // pāda (quarter-line) granularity preserved
      { "pada": 1, "devanagari": "…", "iast": "…", "itrans": "…" },
      { "pada": 3, "devanagari": "…", "iast": "…", "itrans": "…" }
    ]
  },
  "translations": {
    "tagare":       { "text": "…", "ref": "6", "grouped": false, "source": "https://…" },
    "anand_aadhar": { "text": "…", "ref": "6", "grouped": false, "source": "https://…" }
  }
}
```

Nesting mirrors the same names: `corpus.skandhas[].adhyayas[].slokas[]`, with
`adhyaya_count` and `sloka_count` on each level. Records may also carry `variants`
(other-edition readings) and `anomalies` (source irregularities). See below.

### Vachanas are tagged, not discarded

Speaker attributions and prose lead-ins such as `śrī-śuka uvāca`, `rājovāca`,
`ṛṣaya ūcuḥ` and `tatrāyaṃ ślokaḥ` are **not** verse text. The source encodes them as
pāda `0`, so the pipeline lifts all **1,332** of them into a separate `vachana` field on the record they
introduce, typed `speaker` (1,323) or `lead_in` (9). The `text` field is verse only.

There were no `atha prathamo'dhyāyaḥ` / `iti … skandhaḥ` headings to strip in the first
place: the sanskritdocuments ITRANS edition carries no running headers, encoding the
structure purely in an 8-digit numeric line prefix `SSCCVVVP`
(skandha, adhyāya, śloka, pāda). The notebook verifies that this reading recovers exactly
the canonical 12 / 335 structure.

Two edge cases are represented explicitly rather than papered over:

* `type: "vachana_only"`: one slot (`4.21.45`) is a dangling `maitreya uvācha |` at the
  end of an adhyāya with no verse attached, so its `text` is `null`.
* The work-level `|| OM namo bhagavate vāsudevāya ||` and `|| OM tatsat ||` sit outside the
  verse numbering and live under `work.invocation` / `work.colophon`. (A naive parser
  silently appends the latter to 12.13.23.)
* `variants` holds 8 readings that the source printed under a number the main text also
  uses, marked `##vedabase ...##`; keeping them out of `text` stops two different verses
  being spliced together. 18 records carry `anomalies` noting such irregularities.

## Sources

| Role | Source | Edition |
|---|---|---|
| Sanskrit | [sanskritdocuments.org](https://sanskritdocuments.org/doc_purana/bhagpur.itx) | ITRANS e-text, converted to Devanāgarī + IAST |
| Translation A | [wisdomlib.org](https://www.wisdomlib.org/hinduism/book/the-bhagavata-purana) | **G. V. Tagare**, *The Bhāgavata Purāṇa* (Motilal Banarsidass, AITM), the standard academic translation |
| Translation B | [bhagavata.org](https://bhagavata.org) | **Anand Aadhar**, *Śrīmad Bhāgavatam*, 3rd revised ed. |

Where a translator groups verses (`4-5`), the same text is attached to each verse of the
range, with `grouped: true` and `ref` recording the range. Nothing is re-indexed or shifted
to force alignment; per-adhyāya coverage is reported in the notebook so residual
divergences stay visible rather than hidden.

### Licensing

* The Sanskrit e-text is volunteer-prepared and distributed for **personal study and
  research**, not commercial reposting.
* Translation B is **CC BY-NC-SA 3.0**.
* Translation A is Tagare's copyrighted translation as hosted by wisdomlib, collected here
  for **non-commercial research** on the same footing as the source text.

Every translation carries its `source` URL so any excerpt stays attributable. Do not
redistribute the translation fields commercially.

### A note on em dashes

Code, comments and documentation in this repo use no em dashes. Scraped translation text
and adhyāya titles are left exactly as published, so Tagare's em dashes survive inside
`translations.tagare.text` and `adhyayas[].titles.tagare`. The regexes that match verse
ranges spell dash characters as `\u2013` / `\u2014` escapes rather than literals, so they
still match ranges written with an en or em dash.
