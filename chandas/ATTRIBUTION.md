# Attribution and licence of the vendored engine

`chanda/chanda.py` and the metre definition files in `chanda/data/` are **not original to
this repository**. They are the Chandojñānam metre identification engine.

| | |
|---|---|
| Project | Chandojñānam |
| Author | Hrishikesh Terdalkar |
| Upstream | https://github.com/hrishikeshrt/chandojnanam |
| Web version | https://sanskrit.iitk.ac.in |
| Licence | **AGPL-3.0** |
| Copied here from | https://github.com/imradhe/chanda |

The file is unmodified. Only a small `chanda/__init__.py` was added so it can be imported as
a package from `annotate_chandas.py`.

## What the licence implies

AGPL-3.0 is a strong copyleft licence. Two consequences worth being deliberate about:

1. Distributing this repository while it contains AGPL-3.0 code means the combined work is
   subject to AGPL-3.0 terms, and recipients are entitled to the corresponding source.
2. The AGPL's network clause extends that obligation to users who interact with the software
   over a network, so deploying the viewer together with a server-side use of this engine
   would trigger it. The viewer in this directory is static and does not run the engine, so
   serving `index.html` alone does not.

The `imradhe/chanda` repository this was copied from carries no `LICENSE` file, so the
position there is unstated. This note exists so the provenance is at least explicit here.
Choosing a licence for this repository is a decision for its owner; nothing in this file
should be read as having made that choice.

An alternative that avoids the question entirely is to depend on the engine rather than
vendor it, installing it from upstream and importing it, leaving no AGPL code in this tree.
