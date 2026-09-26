# Gibbon study layout

## Scene and theme

Design assumption: Eric reviews a few cards in daylight on a laptop or phone, with quiet space to read Gibbon after answering. A near-white, subtly green neutral surface supports that scene; Anki night mode supplies a dark version for evening review.

## Colour

Restrained neutral palette with green used for links, disclosures, and focus. Tokens live in `anki-layout/styling.css`, with OKLCH light colours and hex compatibility fallbacks. Night mode preserves the original image colours.

## Typography

System sans for prompts, answers, captions, and controls. Georgia for quotations, without italics or ornamental quote marks. Desktop: 25px question, 21px answer, 22px quotation. Phone: 22px, 19px, 20px. Secondary captions are smaller and must not carry facts needed to answer the question.

## Layout and interaction

740px maximum reading width. Single column, answer first, wrapped image rows, quotation, then disclosures. Portrait wells use contain sizing to preserve the whole picture. A single image has a 330px maximum width and is centered; image captions and enlargement controls are centered too. Quotations sit in a softly tinted inset with 24px outer margins and 26px horizontal padding on desktop. Phones use 16px inner padding and no extra outer margins to keep prose readable. No animation or external resources. Native disclosures work with keyboard and touch; visible focus marks interactive controls.

## Source of truth

The templates and CSS in `anki-layout/` define the proposal. The generated preview shares those exact templates and styles. `scripts/build_anki_preview.mjs` reads current card text and image metadata; it does not revise cards or package a deck.
