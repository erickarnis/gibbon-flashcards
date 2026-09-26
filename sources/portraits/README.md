# Portraits for Volumes I–II

Open [the local gallery](../../images/index.html). It works offline and can be filtered by name, chapter, image availability, and type of depiction.

## Scope

The index follows the **reader-supplied Mueller abridgment, Chapters I–XXVI**, in `sources/passages-volumes-1-2.json`. It does not claim coverage of passages omitted from the abridgment, a different edition's notes, or the whole unabridged work. It includes minor named officials, authors, later historical comparisons, biblical people, and named legendary human figures. Gods, personified abstractions, places, ethnic groups, and families named only collectively are excluded.

Names were collected from a capitalized-name sweep of the supplied text, then manually resolved. This is a best-effort index, not a validated scholarly concordance. Name aliases and extraction anchors are recorded. Explicit anchor lists disambiguate repeated names; for other entries, automatically matched occurrences can include namesakes and titles. The references establish where to review an identification and are not exact individual mention counts.

The inventory distinguishes namesakes such as the two Tacituses, two Galluses, two Dalmatiuses, three Constantines, and the historian Sallust versus Julian's adviser. The emperor Maximinus's son is also included as a useful family identification even though the supplied passage calls him only the emperor's son. Gibbon's conflicting accounts of Priscus and Pap's mother are recorded as qualifications; the source text and cards have not been corrected by this image task.

## Selection

Reader preference: use busts or portrait heads instead of coins where a useful sculptural representation is available. On 26 September 2026, 13 coin images were replaced by sculpture photographs, including Gordian I. Disputed attributions are labelled; Charlemagne's reliquary is explicitly a later imagined likeness. Shapur I uses a close view of his ancient statue. Original coin selections and their metadata remain in `../../images/superseded-coins/` and `superseded-coins.json`. Coins remain selected when no suitable sculpture was found or the proposed identification was too weak (for example, the heavily restored Volusianus bust).

The practical preference was:

1. A clearly identified ancient portrait with a visible face.
2. An identified ancient coin, relief, mosaic, or other representation.
3. A later traditional or imagined depiction when an ancient portrait was not readily available.
4. A visible gap when search results showed the wrong person, a map, an inscription, or an unrelated illustration.

Wikipedia's image lists were used to discover candidates; **the Commons image-description pages supply the image provenance and reuse metadata**. Default images were reviewed and obvious mismatches rejected. Extra Commons and web searches filled selected gaps. This was a bounded search to control AI and research cost, not an exhaustive comparison of every photograph on the internet. No paid APIs or image-generation service were used. The downloaded files are existing source images or source-generated thumbnails; no portraits were generated or reconstructed.

Initial image requests were up to 1600 pixels wide, or the available source dimensions when smaller. When original-file delivery was repeatedly rate-limited, remaining images used the official thumbnail service at a standard size below the original (typically 500, 960, or 1280 pixels wide; smaller for small originals). Wikimedia can round a thumbnail request to a standard larger size. Small originals are flagged. Full-size source URLs are kept for later use. Contact sheets were used for visual review; no cropping or retouching was applied to the delivered files.

**An ancient object is not automatically a certain likeness.** Some sculptures are tentative identifications, Roman copies of earlier works, idealized images, or posthumous representations. These cases are labelled where identified. Later engravings resembling coins are not presented as ancient coins. Group scenes remain group scenes: the gallery does not imply that every figure is the named person.

## Files

- `../../images/people/`: one selected image per successfully illustrated person.
- `../../images/index.html`: offline gallery.
- `people.tsv`: editable identity and source-anchor inventory.
- `manifest.json`: complete catalogue, including gaps, image URLs, selection notes, dimensions, checksums, and raw rights metadata.
- `credits.csv`: readable reuse register, one row per person.
- `overrides.json`: deliberate image replacements and rejected false matches.
- `cache/`: source API responses and supplementary search results for audit and reproducibility.
- `download-records.json`: which source file was actually downloaded for each person.
- `coverage.md`: final counts and unresolved entries.

## Reuse notes

Alexander the Great and Julius Caesar now use the exact Britannica CDN images selected by the reader. Their image-specific public reuse rights and photographic credits have not been verified; the register marks this explicitly instead of retaining the replaced files' licences. Caesar's sculpture is Ferrucci's Renaissance work (circa 1512–14), labelled as a later depiction. The Met offers public-domain images of that object, but the precise rights of the selected Britannica file remain unverified. The previous selections and metadata are retained in `../../images/superseded-portraits/` and `superseded-before-britannica.json`.

The collection is local and has not been published or packaged for Anki. **Personal-use collection does not change a source's stated reuse terms.** Restrictions are recorded now so they can be checked if publication is later proposed.

Each downloaded image has a source page and licence label. Creator credits, licence links, and source restrictions are recorded where supplied. Five images lack a creator credit in the retrieved metadata and are explicitly flagged in the register. Preserve this information with the image. The licence applies to the photograph or reproduction as recorded by its source; it should not be inferred solely from the age of the depicted object.

- **CC BY:** preserve the creator credit, provide the exact licence link, and identify modifications.
- **CC BY-SA:** the above conditions plus the licence's ShareAlike terms for adaptations.
- **Public domain / CC0 / PDM-owner:** record the source's assertion and provenance. A public-domain label on Commons is not an independent worldwide rights clearance.
- **Attribution / Copyrighted free use:** custom permissions; consult the saved metadata and live source page for the precise terms before publication.
- Other source restrictions, if provided, appear in the `restrictions` field. A blank field means the API supplied no restriction, not that a complete legal review found none.

The register is a snapshot of the source metadata. Preserve source links and check them again when preparing a public release. Metadata text is retained for audit, not offered under a new project-wide licence.

## Reproduce or continue

The scripts use Python's standard library for collection and Pillow for image validation and contact sheets. Run from the project root using an available Python environment:

```
python scripts/collect_portraits.py inventory
python scripts/collect_portraits.py pages
python scripts/collect_portraits.py metadata
python scripts/collect_portraits.py download
# If original-file delivery is rate-limited, after metadata:
python scripts/use_portrait_thumbnails.py
python scripts/collect_portraits.py download
python scripts/build_portrait_gallery.py
```

`pages` uses cached batches; if changing the inventory, archive or clear `cache/pages-*.json` first so the batches match the revised inventory. Selection overrides live in `overrides.json`. After changing a selection, rerun pages, metadata, download, and the gallery builder. Metadata is cached. Download records prevent confusing an old file with a changed selection.

Respect HTTP 429 and Retry-After pauses. The downloader stops and checkpoints when rate-limited. Supplementary searches must also pause on a rate-limit response. A failed search is not evidence that no portrait exists.
