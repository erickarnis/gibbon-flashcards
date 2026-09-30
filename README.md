# Gibbon — Flashcards for Volumes I–II

Markdown flashcards for Edward Gibbon’s *The Decline and Fall of the Roman Empire*, edited and abridged by Hans-Friedrich Mueller (Modern Library, 2003; eISBN 978-0-307-41976-7).

The collection covers **Chapters I–XXVI**, the first two volumes as marked in this edition: the empire of the Antonines, the third-century crisis, Constantine and Christianity, Julian, Adrianople, and **Theodosius’s Gothic settlement of 382**. It follows the supplied abridgment; it does not reconstruct every passage omitted from the unabridged work.

**Status: Anki package revised on 28 September 2026 after mobile review.** All 277 original cards have been reviewed. The revision merges nine repeated cards, adds 13 cards for missing connections and memorable passages, and brings the collection to **281 cards with 157 checked Gibbon quotations**. All **32 literary highlights** appear on linked cards. The Anki package contains all 281 cards in two volume subdecks.

## Study files

| File | Coverage | Cards |
| --- | --- | ---: |
| [Narrative connections](00-narrative-connections.md) | Five sequences and comparisons across the volumes | 5 |
| [Opening emperors](01-opening-emperors.md) | Nerva through Marcus Aurelius; I–III and the opening of IV | 37 |
| [Empire and constitution](01b-empire-and-constitution.md) | Army, citizenship, public works, and Augustus; I–III | 18 |
| [Commodus to Gallienus](02-commodus-to-gallienus.md) | IV–X; Gallienus’s death from XI | 67 |
| [Restoration and Christianity](03-restoration-and-christianity.md) | Claudius, Aurelian, Tetrarchy, Constantine, early Christianity; XI–XVI | 68 |
| [Constantine to the Gothic settlement](04-constantine-to-adrianople.md) | XVII–XXVI; Volume II | 86 |
| **Total** | **Volumes I–II** | **281** |

Read the files in this order. Numbering restarts in each file, so feedback can identify the file and card number. Stable hidden IDs preserve each card’s identity through later revisions.

[**Literary highlights: 32 passages, each linked to its card**](LITERARY-HIGHLIGHTS.md) collects the most memorable selected prose with context and source links. The [timeline and regional guide](ORIENTATION.md) provides a reference for the whole narrative.

## What counts as a correct answer

Recall the substance of **A**, including a year when the question asks for one. Exact literary wording is never required. **More** holds worthwhile historical colour. **A** uses Gibbon’s own words when they directly answer the question, with necessary context added separately. **Gibbon** holds an additional literary passage; unquoted connecting prose is newly written. Speeches and anecdotes are identified as reports where appropriate, and Gibbon’s interpretations are distinguished from factual claims.

Dates are AD unless marked BC. Adoption, designation as heir, joint rule, and sole accession are kept distinct. Reigns continuing beyond the volume boundary are not extended into later volumes simply to supply a death card.

## Sources and review

Each card has source links. The supplied text is preserved with **L anchors**, which identify extraction lines rather than printed pages. Clear chronology errors are corrected in the answers; substantial uncertainty remains visible in the claim itself. Source comparisons and selection decisions are kept outside the study text.

- [Mobile corrections and quotation cleanup, 28 September](sources/revision-2026-09-28.md)
- [Revision record: changes and verification](sources/revision-2026-09-26.md)
- [Original card-by-card review](REVIEW-2026-09-26.md)
- [Card guidelines](CARD-GUIDELINES.md)
- [Settled reader decisions](sources/editorial-notes.md)
- [Source files and review notes](sources/README.md)
- [Opening companion review](sources/review-01b.md)
- [Chapters IV–X review](sources/review-02.md)
- [Chapters XI–XVI review and coverage map](sources/review-03.md)
- [Chapters XVII–XXVI review and coverage map](sources/review-04.md)

Run `node scripts/check-cards.mjs` from this folder to check card structure, numbering, unique IDs, exact duplicate questions, preserved source anchors, quotation wording and brackets, retired IDs, and the presence of every literary highlight on its linked card. Historical accuracy and the quality of a question still require editorial reading; the checker does not replace that review.

## Anki deck

Open [Gibbon-Volumes-I-II.apkg](dist/Gibbon-Volumes-I-II.apkg) in Anki to import:

- **Gibbon — Decline and Fall::Volume I** — 192 cards, Chapters I–XVI.
- **Gibbon — Decline and Fall::Volume II** — 89 cards, Chapters XVII–XXVI.

Connection cards go in the volume where their narrative concludes. The church-power connection spans both volumes and belongs in Volume II. Each note generates one forward card. Stable note IDs support later updates without creating a new identity for each card.

The existing layout includes 157 checked quotations and 91 bundled portraits, selected from people explicitly named in questions and answers. Pictures appear only after revealing the answer, with identity qualifications and source credits. The mapping is recorded in [the build report](dist/anki-build-report.json). It is intentionally selective; not every person has a picture. Local source links become readable edition, chapter, and extraction-line citations; external links remain clickable. The ebook and full source text are not bundled.

To rebuild, create a Python virtual environment, install `scripts/requirements-anki.txt`, run `node scripts/check-cards.mjs`, then run `python scripts/build_anki.py`. The generated package and report are in the ignored `dist/` folder.

The 28 September update removes repeated paraphrases, makes the Terminus legend visible before the joke, removes portrait-selection commentary, repairs the full-screen background, and re-encodes Nerva as a baseline JPEG. Forty answers now use the checked quotation directly (32 alone, eight with a factual introduction); 117 retain a separate literary passage.

**Updating an existing deck:** import this package into the same collection without deleting the old deck. Allow note and note-type updates if prompted. An isolated test using Anki’s 26.9.3 backend imported the original package, assigned a review schedule, then imported the update. All 281 note/card identities and the schedule were preserved; text, style, and media updated successfully. It did not touch the reader’s collection. If you use AnkiWeb, complete media syncing before reviewing on another device.

Validation checks counts, identities, volume assignments, required fields, media references, image decoding, ZIP integrity, and SQLite integrity. Actual exported cards were checked in a browser at phone width in light and dark modes. The original Nerva file loaded in the desktop browser; the reported iOS failure could not be reproduced there, so the baseline-JPEG repair still needs confirmation on the phone. No native mobile UI was available for testing. The original ebook is untouched.

To repeat the isolated import test, install `scripts/requirements-anki-test.txt`, then run `python scripts/test_anki_import.py path/to/previous-package.apkg`. Run `python scripts/preview_anki_package.py` to render the actual exported fields and media into `dist/qa/` for browser checks.
