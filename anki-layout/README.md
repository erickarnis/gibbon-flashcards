# Gibbon card layout

Open [the interactive preview](preview.html). It uses seven examples from the current Markdown cards and the existing portrait catalogue. Choose an example, reveal its answer, try phone width or night mode, and enlarge a picture. Rebuild with `node scripts/build_anki_preview.mjs` from the repository root.

## Study order

1. **Question:** one prompt, with no topic title, portrait, date badge, or quotation that might reveal the answer.
2. **Answer:** the current A field, with its existing emphasis. This may be a direct Gibbon quotation, with a short factual introduction where needed. Grade recall of the meaning, not exact wording.
3. **Pictures:** named, uncropped images in reading order. One image stays modest in size; pairs and groups of four use two columns; larger groups use three columns on desktop and two on phones. Rows wrap without horizontal scrolling. “Enlarge” opens the image inline, using the full card width on current browsers.
4. **Gibbon:** visible literary passage in serif type. Exact quotation wording is not required recall.
5. **More context:** optional disclosure, separate from the answer.
6. **Sources and image credits:** separate disclosures preserve provenance without crowding the review.

Only useful image qualifications appear beneath names, including later or uncertain depictions. `portrait-captions.json` holds concise overrides; selection notes stay in the source catalogue. Long quotations retain their full wording and scroll with the card. Missing sections disappear completely. No slideshow, image-count ceiling, or automatic cropping. For very large collections, keep only images useful to this particular question.

## Templates and fields

Use a single forward card type. [front.html](front.html), [back.html](back.html), and [styling.css](styling.css) are the proposed Anki Front Template, Back Template, and Styling. They use HTML/CSS and native disclosures, without JavaScript or external fonts. The preview controls are separate and do not belong in Anki.

| Field | Content |
| --- | --- |
| StableID | Existing hidden card ID; retain for later updates, not shown |
| Question | Q, converted from Markdown to HTML |
| Answer | A, converted from Markdown to HTML |
| Images | Zero or more complete figure elements, described below |
| Gibbon | Additional quotation; empty when the quotation is already the answer |
| More | Optional historical context |
| Sources | Source links and readable citations |
| ImageCredits | Creator, source page, exact licence link, restrictions and qualifications from the catalogue |
| PromptImages | Empty by default; reserved for deliberately authored visual questions |

Never put answer-identifying captions or metadata in PromptImages. For a future visual question, explicitly include any picture needed for explanation in Images too: the back does not repeat PromptImages. No visual-question cards have been authored in this task.

The Images field contains repeated elements of this form. Media paths below are illustrative filenames for a future Anki collection, not the preview's relative paths:

```html
<figure>
  <div class="image-frame">
    <img src="gibbon-nerva.jpg" alt="Portrait head of Nerva">
  </div>
  <figcaption>
    <strong>Nerva</strong>Adopting emperor
    <span class="depiction">Ancient portrait head; attribution per source.</span>
  </figcaption>
  <details class="picture-zoom">
    <summary>Enlarge</summary>
    <img src="gibbon-nerva.jpg" alt="Portrait head of Nerva">
  </details>
</figure>
```

## Packaging boundary and compatibility

The preview demonstrates the layout. The reader authorised packaging on 26 September 2026; `../scripts/build_anki.py` now exports this template and a selective portrait mapping into `../dist/Gibbon-Volumes-I-II.apkg`. The 28 September revision updates card prose and captions. Original source images are unchanged; Nerva is re-encoded only in the package. The generated build report records the exported mapping.

Export requirements (implemented by the builder): copy images into Anki media with stable, collision-free filenames; rewrite both image references in each figure; convert Markdown to HTML; preserve IDs; convert local Markdown source links into useful Anki-accessible citations or bundled source material. Do not copy the preview's `../images/` or local Markdown links into an imported deck. Preserve all image credit metadata and the current review decisions.

The template follows the official Anki documentation for [field replacements](https://docs.ankiweb.net/templates/fields.html), [conditional sections](https://docs.ankiweb.net/templates/generation.html), and [styling and night mode](https://docs.ankiweb.net/templates/styling.html). The card uses `.nightMode` and `.night_mode`. Hex colours provide a fallback for clients without OKLCH; clients without CSS `:has()` retain the gallery and inline enlargement but do not expand an enlarged figure across the whole grid. Native client testing in Anki Desktop, AnkiMobile, and AnkiDroid remains necessary before release.

The body must not use CSS containment: it prevents its background from painting the viewport below short questions. Container queries instead use `.gibbon-card`, and `body.card` fills at least the viewport. This fix was reproduced and checked with the actual exported HTML, at phone width in light and dark themes.
