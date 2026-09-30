// Validate Markdown structure, source anchors, and quotation fidelity.
// Run from the repository root: node scripts/check-cards.mjs
import fs from 'node:fs';
import path from 'node:path';

const files = fs.readdirSync('.').filter(f => /^\d.*\.md$/.test(f)).sort();
const ids = new Set();
const questions = new Map();
const errors = [];
const warnings = [];
const summary = [];
const cardQuotes = new Map();
const normalize = s => s.replace(/\s+/g, ' ').trim();
const sourceMap = new Map([
  ['sources/mueller-opening.md', JSON.parse(fs.readFileSync('sources/passages.json', 'utf8'))],
  ['sources/mueller-volumes-1-2.md', JSON.parse(fs.readFileSync('sources/passages-volumes-1-2.json', 'utf8'))],
]);

for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  const cards = text.split(/(?=^### \d+\.)/m).slice(1);
  let quoted = 0;
  const chapters = new Set();
  for (const [i, card] of cards.entries()) {
    const label = `${file}:${i + 1}`;
    if (!card.startsWith(`### ${i + 1}. `)) errors.push(`${label}: nonsequential heading`);
    const foundIds = [...card.matchAll(/<!-- ID: ([\w-]+) -->/g)];
    if (foundIds.length !== 1) errors.push(`${label}: expected one stable ID`);
    for (const [, id] of foundIds) {
      if (ids.has(id)) errors.push(`${label}: duplicate ID ${id}`);
      ids.add(id);
      if (!card.includes(`<a id="${id}"></a>`)) errors.push(`${label}: missing stable link anchor`);
    }
    for (const field of ['Q', 'A', 'Sources']) {
      if ([...card.matchAll(new RegExp(`^\\*\\*${field}:\\*\\* .+`, 'gm'))].length !== 1)
        errors.push(`${label}: expected one nonempty ${field} field`);
    }
    const question = normalize(card.match(/^\*\*Q:\*\* (.+)$/m)?.[1] ?? '');
    if (questions.has(question)) errors.push(`${label}: duplicate question (${questions.get(question)})`);
    questions.set(question, label);
    const localLinks = [...card.matchAll(/\]\(([^)]+\.md)(?:#([^)]+))?\)/g)];
    const sourceTexts = [];
    for (const [, target, anchor] of localLinks) {
      const resolved = path.normalize(path.join(path.dirname(file), target));
      if (!fs.existsSync(resolved)) errors.push(`${label}: missing ${resolved}`);
      if (sourceMap.has(resolved) && anchor) {
        const passage = sourceMap.get(resolved)[anchor.replace(/^L/, '')];
        if (!passage) errors.push(`${label}: missing ${resolved}#${anchor}`);
        else {
          sourceTexts.push(normalize(passage.text));
          chapters.add(passage.chapter);
        }
      }
    }
    if (!sourceTexts.length && !/\*\*Sources:\*\*.*https?:\/\//.test(card))
      errors.push(`${label}: no source reference`);
    const answerField = card.match(/^\*\*A:\*\* (.+)$/m)?.[1] ?? '';
    const quoteField = card.match(/^\*\*Gibbon:\*\* (.+)$/m)?.[1]
      ?? answerField.match(/“.+”/)?.[0];
    if (quoteField) {
      quoted++;
      for (const [, id] of foundIds) cardQuotes.set(id, {file, text: normalize(quoteField)});
      let brackets = 0;
      for (const char of quoteField) {
        if (char === '[') brackets++;
        if (char === ']') brackets--;
        if (brackets < 0) break;
      }
      if (brackets !== 0) errors.push(`${label}: unfinished or unmatched quotation bracket`);
      const match = quoteField.match(/^“([\s\S]+)”(?:\s*.*)?$/);
      if (!match) { errors.push(`${label}: quotation must use outer curly quotes`); continue; }
      const quote = normalize(match[1]);
      if (!sourceTexts.some(t => t.includes(quote))) {
        // Marked omissions may join passages; all retained parts must occur in order.
        const chunks = quote.split(/\s*(?:\[…\]|\[\.\.\.\]|…|\.{3})\s*/).filter(Boolean);
        const combined = sourceTexts.join(' ');
        let cursor = 0;
        const matches = chunks.every(chunk => {
          const at = combined.indexOf(chunk, cursor);
          if (at < 0) return false;
          cursor = at + chunk.length;
          return true;
        });
        if (chunks.length > 1 && matches) warnings.push(`${label}: marked omission; review its context manually`);
        else errors.push(`${label}: quotation differs from cited source`);
      }
    }
    const answer = card.match(/^\*\*A:\*\* (.+)$/m)?.[1] ?? '';
    if (answer.split(/\s+/).length > 80) warnings.push(`${label}: answer exceeds 80 words`);
  }
  summary.push({file, cards:cards.length, quotations:quoted, chapters:[...chapters].join(', ')});
}
let highlights = 0;
if (fs.existsSync('LITERARY-HIGHLIGHTS.md')) {
  const text = fs.readFileSync('LITERARY-HIGHLIGHTS.md', 'utf8');
  for (const section of text.split(/^## /m).slice(1)) {
    const quote = section.match(/^> (.+)$/m)?.[1];
    const line = section.match(/#L(\d+)/)?.[1];
    if (!quote || !line || !sourceMap.get('sources/mueller-volumes-1-2.md')[line]?.text.includes(quote))
      errors.push('LITERARY-HIGHLIGHTS.md: missing or mismatched excerpt in ' + section.split('\n')[0]);
    const cardLink = section.match(/^\*\*Card:\*\* \[[^\n]+\]\(([^#\n]+)#([\w-]+)\)/m);
    const card = cardLink && cardQuotes.get(cardLink[2]);
    if (!card || card.file !== cardLink[1] || !card.text.includes(normalize(quote ?? '')))
      errors.push('LITERARY-HIGHLIGHTS.md: excerpt missing from its linked card in ' + section.split('\n')[0]);
    highlights++;
  }
}
if (fs.existsSync('sources/retired-card-ids.json')) {
  const retired = new Set();
  for (const entry of JSON.parse(fs.readFileSync('sources/retired-card-ids.json', 'utf8'))) {
    if (retired.has(entry.retired) || ids.has(entry.retired) || !ids.has(entry.retained))
      errors.push(`Invalid card merger: ${entry.retired} -> ${entry.retained}`);
    retired.add(entry.retired);
  }
}
console.table(summary);
console.log(highlights + ' literary highlights checked.');
for (const warning of warnings) console.log(`REVIEW: ${warning}`);
for (const error of errors) console.error(`ERROR: ${error}`);
console.log(`${summary.reduce((n,s)=>n+s.cards,0)} cards; ${summary.reduce((n,s)=>n+s.quotations,0)} quotations; ${errors.length} errors; ${warnings.length} review notes.`);
process.exitCode = errors.length ? 1 : 0;
