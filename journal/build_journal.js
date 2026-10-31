// Builds the "Chapter by Chapter" journal as A5 PDFs.
//   node journal/build_journal.js
// Outputs (in journal/output/):
//   chapter-by-chapter-sample-filled.pdf  – example month filled in
//   chapter-by-chapter-printable-blank.pdf – blank pages to print and sell
//   previews/*.png                          – one image per page

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

const DIR = __dirname;
const OUT = path.join(DIR, 'output');
const FONT = (f) => 'file://' + path.join(DIR, 'fonts', f);

// ---------- palette (from the hand-made journal) ----------
const C = {
  pink: '#FF7A8A',
  pinkSoft: '#FFB3C1',
  yellow: '#F7F33C',
  green: '#5BCB32',
  greenDark: '#3FAE27',
  olive: '#A8C928',
  orange: '#FF9F45',
  peach: '#FFC59A',
  red: '#E5262E',
  ink: '#262422',
  paper: '#FFFEFA',
};

// Myself = everything on the MYSELF (extras) page
const fillMyself = () => {
  const t = [...demo.extrasA.items, ...demo.extrasB.items].reduce((x, [, v]) => x + v, 0);
  demo.budget.find(([n]) => n === 'Myself')[2] = Math.round(t * 100) / 100;
};
const money = (n) =>
  '$ ' + n.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const spaced = (w) => w.split('').map((ch) => (ch === ' ' ? '&nbsp;&nbsp;' : ch)).join('<i>•</i>');
const hand = (v, filled) => (filled && v !== undefined && v !== '' ? `<span class="hw">${v}</span>` : '');

// ---------- demo data for the filled sample ----------
const demo = {
  month: 'AUGUST',
  chapter: '8',
  theme: ['my birthday', 'month'],
  earnings: [['Pay I', 1237.86], ['Pay II', 1222.18], ['Other', 0], ['Tax', 0]],
  savingsGoal: '20',
  savings: [['Savings', 400], ['Emergency', 100]],
  budget: [
    ['Rent', 978, 978],
    ['Groceries', 250, 202.72],
    ['Bus / Transit', 0, 0],
    ['Phone', 95, 92.35],
    ['Laundry', 20, 12],
    ['Family', 200, 201.99],
    ['Friends & gifts', 60, 45],
    ['Myself', 300, null], // filled from the MYSELF page total
  ],
  accounts: [['Savings', 1991.77], ['Chequing', 92.35], ['Credit card', -140.2]],
  extrasA: { title: 'Uber, food & clothes', items: [['Uber', 22.97], ['Food out', 28.26], ['Fair / carnival', 30], ['Shoppers', 10.87], ['Dollarama', 21.67]] },
  extrasB: { title: 'Work & home', items: [['French class', 25], ['Sports', 10.5], ['PDF app', 4.32], ['Toolbox', 36.48]] },
  bills: [
    ['Rent', '1st', 978, true], ['Phone', '10th', 92.35, true], ['Credit card', '15th', 140.2, true],
    ['Internet', '20th', 55, false], ['Streaming', '22nd', 16.99, false], ['Gym', '28th', 25, false],
  ],
  habits: {
    groups: [['SOUL', 2, C.yellow], ['BODY', 2, C.green], ['HOME', 1, C.pink], ['GROWTH', 2, C.orange], ['MINE', 1, C.pinkSoft]],
    names: ['prayer', 'me time 1hr', 'gym', 'skincare', 'declutter 15', 'creative 1hr', "tomorrow's ready", ''],
    probs: [0.9, 0.55, 0.5, 0.8, 0.6, 0.45, 0.7, 0],
  },
  tracker: { goals: ['2.5L', '80g', '7K', '8 hr'] },
  memories: ['beach day', 'coffee w/ mom', 'first drive!', 'new plant', 'sunset walk', 'bday cake', 'painted', 'movie night', 'library', 'farmers mkt', 'friends bbq', 'sang karaoke'],
  wins: ['Saved 20% even in birthday month', 'Prayed every single day', 'A memory photo almost every day'],
  lesson: 'Uber adds up fast — plan rides ahead',
  next: 'Walk more, read 15 min a day',
};

// Repeatable pseudo-random so the filled sample looks the same each build
fillMyself();
let seed = 7;
const rnd = () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);

// ---------- shared CSS ----------
const css = `
@font-face{font-family:Gaegu;src:url(${FONT('Gaegu-Bold.ttf')});font-weight:700}
@font-face{font-family:Patrick;src:url(${FONT('PatrickHand.ttf')})}
@font-face{font-family:Caveat;src:url(${FONT('Caveat.ttf')})}
@font-face{font-family:Fredoka;src:url(${FONT('Fredoka.ttf')})}
@font-face{font-family:Gochi;src:url(${FONT('GochiHand.ttf')})}
@page{size:148mm 210mm;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:Patrick,sans-serif;color:${C.ink};-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:148mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.band{position:absolute;inset:4mm;border-radius:2.5mm}
.panel{position:absolute;left:10mm;right:10mm;top:21mm;bottom:10mm;background-color:${C.paper};
  background-image:radial-gradient(circle,#c4beb3 0.22mm,transparent 0.3mm);background-size:5mm 5mm;background-position:2.5mm 2.5mm;
  border:0.45mm solid ${C.ink};border-radius:0.6mm}
.title{position:absolute;left:0;right:0;top:7.5mm;text-align:center;font-family:Gaegu;font-weight:700;font-size:25pt;letter-spacing:0.5mm;line-height:1}
.title i{font-style:normal;font-size:12pt;vertical-align:middle;margin:0 1.4mm;position:relative;top:-0.6mm}
.pad{position:absolute;inset:6mm 7mm}
.hw{font-family:Gochi;font-size:12.5pt;color:#24305E}
.red{color:${C.red};font-family:Patrick;font-size:19pt;letter-spacing:0.5mm}
.hl{display:inline-block;padding:0.4mm 2.2mm;border-radius:0.6mm;font-size:11pt;letter-spacing:0.4mm}
.line{border-bottom:0.3mm solid #8d877d}
.small{font-size:8.5pt;color:#6b655c;letter-spacing:0.3mm}
.foot{position:absolute;left:0;right:0;bottom:5.2mm;text-align:center;font-size:6.5pt;color:#8d877d;letter-spacing:0.6mm}
table{border-collapse:collapse;table-layout:fixed}
`;

const page = (bandColor, title, inner, opts = {}) => `
<section class="page">
  <div class="band" style="background:${bandColor}"></div>
  ${title ? `<div class="title">${spaced(title)}</div>` : ''}
  <div class="panel" style="${opts.panelStyle || ''}">${inner}</div>
  <div class="foot">CHAPTER BY CHAPTER</div>
</section>`;

// Concentric "August-style" frames
function rings(colors, center) {
  let html = '';
  const step = 5.2;
  colors.forEach((col, i) => {
    const inset = 4 + i * step;
    html += `<div style="position:absolute;inset:${inset}mm;border-radius:${Math.max(3, 10 - i)}mm;background:${col};
      box-shadow:inset 0 0 0 0.35mm ${C.ink}, inset 0 0 0 0.75mm ${col}, inset 0 0 0 1.05mm ${C.ink}"></div>`;
  });
  const last = 4 + colors.length * step;
  return html + `<div style="position:absolute;inset:${last}mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">${center}</div>`;
}
const RING_COLORS = [C.green, C.olive, C.green, C.olive, C.peach, C.orange, C.yellow, C.peach, C.yellow];
const outlined = (txt, size) =>
  `<div style="font-family:Fredoka;font-size:${size}pt;line-height:1;color:${C.yellow};-webkit-text-stroke:0.55mm ${C.ink};
   paint-order:stroke fill;text-shadow:0.8mm 0.8mm 0 ${C.ink};letter-spacing:1mm">${txt}</div>`;

// ---------- pages ----------
function cover() {
  return `<section class="page">${rings(RING_COLORS, `
    <div style="font-family:Caveat;font-size:17pt;margin-bottom:3mm">one month = one chapter</div>
    ${outlined('CHAPTER', 34)}
    <div style="font-family:Gaegu;font-weight:700;font-size:20pt;margin:2mm 0">— by —</div>
    ${outlined('CHAPTER', 34)}
    <div style="margin-top:6mm;font-size:11pt;letter-spacing:0.8mm">MONEY <i style="font-style:normal">•</i> HABITS <i style="font-style:normal">•</i> LIFE</div>
    <div style="margin-top:2mm;font-family:Caveat;font-size:14pt">a hand-drawn style budget & habit journal</div>
  `)}</section>`;
}

function howTo() {
  const steps = [
    [C.green, 'Month opener', 'Colour it in. A fresh start.'],
    [C.pink, 'Chapter page', 'What is this month about?'],
    [C.yellow, 'Summary', 'Earned – saved – spent = left'],
    [C.yellow, 'Budget', 'Planned vs. spent, by category'],
    [C.yellow, 'Myself', 'Everything I spend on me'],
    [C.pinkSoft, 'Bills & due dates', 'Never miss a payment'],
    [C.pink, 'Habits + tracker', 'Colour a box, log a memory'],
    [C.green, 'Chapter close', 'Wins, lessons, next month'],
  ];
  const rows = steps.map(([c, t, d], i) => `
    <div style="display:flex;align-items:center;gap:3mm;margin-bottom:3.2mm">
      <div style="width:7mm;height:7mm;border-radius:50%;background:${c};border:0.35mm solid ${C.ink};display:flex;align-items:center;justify-content:center;font-size:10pt">${i + 1}</div>
      <div><div style="font-size:12pt;letter-spacing:0.5mm">${t.toUpperCase()}</div><div class="small">${d}</div></div>
    </div>`).join('');
  return page(C.pinkSoft, 'HOW IT WORKS', `<div class="pad">
    <div style="font-family:Caveat;font-size:15pt;margin-bottom:4mm">Each month is a new chapter. Fill these pages in order:</div>
    ${rows}
    <div style="margin-top:4mm;border:0.4mm dashed ${C.ink};border-radius:2mm;padding:3mm;text-align:center;background:#fff">
      <div class="small">THE ONE FORMULA</div>
      <div style="font-size:13pt;margin-top:1mm">EARNED <b>−</b> SAVED <b>−</b> SPENT <b>=</b> <span style="color:${C.red}">REMAINING</span></div>
    </div></div>`);
}

function opener(filled) {
  const center = filled
    ? `${outlined(demo.month, 40)}<div style="font-family:Caveat;font-size:18pt;margin-top:5mm">chapter ${demo.chapter}</div>`
    : `<div style="width:85mm;border-bottom:0.5mm solid ${C.ink};height:22mm"></div>
       <div class="small" style="color:${C.ink};margin-top:1.5mm">MONTH</div>
       <div style="font-family:Caveat;font-size:18pt;margin-top:6mm">chapter ______</div>`;
  return `<section class="page">${rings(RING_COLORS, center)}</section>`;
}

function chapterPage(filled) {
  const hearts = [[12, 10, -12], [58, 6, 8], [96, 22, 18], [6, 92, -20], [70, 104, 10], [98, 128, 14], [16, 150, -8], [104, 70, 0]];
  const heartSvg = (x, y, r) => `<svg style="position:absolute;left:${x}mm;top:${y}mm;width:20mm;height:18mm;transform:rotate(${r}deg)" viewBox="0 0 40 36">
    <path d="M20 33 C6 23 2 16 2 10 C2 5 6 2 11 2 C15 2 18 4 20 8 C22 4 25 2 29 2 C34 2 38 5 38 10 C38 16 34 23 20 33Z"
      fill="none" stroke="${C.pinkSoft}" stroke-width="7" stroke-linejoin="round"/>
    <path d="M20 33 C6 23 2 16 2 10 C2 5 6 2 11 2 C15 2 18 4 20 8 C22 4 25 2 29 2 C34 2 38 5 38 10 C38 16 34 23 20 33Z"
      fill="none" stroke="${C.pink}" stroke-width="3" stroke-linejoin="round"/></svg>`;
  const lines = filled
    ? [`<span style="font-family:Caveat;font-size:20pt">${demo.theme[0]}</span>`, `<span style="font-family:Caveat;font-size:24pt">ch. ${demo.chapter}</span>`, `<span style="font-family:Caveat;font-size:26pt">finance</span>`]
    : ['', `<span style="font-family:Caveat;font-size:20pt;color:#8d877d">ch. ____</span>`, ''];
  return page(C.pink, '', `
    ${hearts.map((h) => heartSvg(...h)).join('')}
    <div style="position:absolute;left:50%;top:50%;width:100mm;height:100mm;margin:-50mm 0 0 -50mm;border:0.4mm solid ${C.ink};border-radius:50%"></div>
    <div style="position:absolute;left:50%;top:50%;width:84mm;margin:-27mm 0 0 -42mm">
      ${lines.map((l) => `<div class="line" style="height:18mm;display:flex;align-items:flex-end;justify-content:center;padding-bottom:1mm">${l}</div>`).join('')}
    </div>
    ${filled ? '' : `<div class="small" style="position:absolute;left:0;right:0;bottom:4mm;text-align:center">this chapter is about…</div>`}
  `, { panelStyle: 'top:10mm' });
}

function summary(filled) {
  const earnTotal = demo.earnings.reduce((s, [, v]) => s + v, 0);
  const saveTotal = demo.savings.reduce((s, [, v]) => s + v, 0);
  const expenses = demo.budget.filter(([n]) => n !== 'Myself').reduce((s, r) => s + r[2], 0);
  const myself = demo.budget.find(([n]) => n === 'Myself')[2];
  const spendTotal = expenses + myself;
  const remaining = earnTotal - saveTotal - spendTotal;

  const row = (label, val) => `<div style="display:flex;align-items:flex-end;height:8.6mm;font-size:12pt;letter-spacing:0.6mm">
      <div style="width:33mm">${label.toUpperCase()}</div><div style="width:5mm">–</div>
      <div class="line" style="flex:1;height:7mm;padding-left:2mm">$ ${filled ? hand(val.toFixed(2), true) : ''}</div></div>`;
  const total = (v) => `<div style="height:13mm;display:flex;align-items:center;justify-content:flex-end;border-bottom:0.4mm solid ${C.ink};margin-bottom:3mm">
      <span class="red">${filled ? money(v) : '$'}</span>${filled ? '' : `<span style="display:inline-block;width:38mm"></span>`}</div>`;
  const section = (side, rows, t, extra = '') => `<div style="position:relative;padding-left:7mm">
      <div style="position:absolute;left:-1mm;top:0;bottom:3mm;writing-mode:vertical-rl;transform:rotate(180deg);text-align:center;font-size:8pt;letter-spacing:1mm;color:#6b655c">${side}</div>
      ${extra}${rows}${total(t)}</div>`;

  const savingRows = filled ? demo.savings : [['', 0], ['', 0]];
  return page(C.yellow, 'SUMMARY', `<div class="pad" style="top:4mm">
    ${section('EARNINGS', (filled ? demo.earnings : [['Pay I'], ['Pay II'], ['Other'], ['Tax']]).map(([l, v]) => row(l, v || 0)).join(''), earnTotal)}
    ${section('SAVINGS', savingRows.map(([l, v]) => row(l || '', v)).join(''), saveTotal,
      `<div class="small" style="margin-bottom:1mm">goal: ${filled ? hand(demo.savingsGoal, true) : '____'} % of what I earn</div>`)}
    ${section('SPENDING', [['Expenses', expenses], ['Myself', myself]].map(([l, v]) => row(l, v)).join(''), spendTotal)}
    <div style="margin-top:1mm;border:0.4mm solid ${C.ink};border-radius:2mm;background:${C.yellow};padding:2mm 3mm;display:flex;justify-content:space-between;align-items:center">
      <div><div style="font-size:11pt;letter-spacing:0.6mm">REMAINING</div><div class="small" style="color:${C.ink}">earned − saved − spent</div></div>
      <div class="red" style="font-size:18pt">${filled ? money(remaining) : '$ ________'}</div>
    </div></div>`);
}

function budget(filled) {
  const rows = filled ? [...demo.budget, ['', '', ''], ['', '', '']] : Array(11).fill(['', '', '']);
  const planned = demo.budget.reduce((s, r) => s + r[1], 0);
  const spent = demo.budget.reduce((s, r) => s + r[2], 0);
  const tr = rows.map(([n, p, s]) => {
    const over = filled && typeof s === 'number' && s > p;
    return `<tr style="height:9mm">
      <td class="line" style="font-size:12pt;letter-spacing:0.6mm">${n ? n.toUpperCase() : ''}</td>
      <td class="line" style="text-align:right;padding-right:2mm">${filled && p !== '' ? hand(p.toFixed(2), true) : ''}</td>
      <td class="line" style="text-align:right;padding-right:2mm">${filled && s !== '' ? `<span class="hw" style="${over ? `background:${C.pinkSoft};padding:0 1mm` : ''}">${s.toFixed(2)}</span>` : ''}</td></tr>`;
  }).join('');
  const acc = (filled ? demo.accounts : [['', ''], ['', ''], ['', '']]).map(([n, v]) => `
    <div style="display:flex;align-items:flex-end;height:8mm;font-size:12pt;letter-spacing:0.6mm">
      <div class="line" style="width:40mm;height:7mm">${n ? n.toUpperCase() : ''}</div><div style="width:6mm;text-align:center">–</div>
      <div class="line" style="flex:1;height:7mm">$ ${filled ? hand(v.toFixed(2), true) : ''}</div></div>`).join('');
  return page(C.yellow, 'BUDGET', `<div class="pad" style="top:4mm">
    <table style="width:100%">
      <colgroup><col style="width:52%"><col style="width:24%"><col style="width:24%"></colgroup>
      <tr><td class="small">CATEGORY</td><td class="small" style="text-align:right;padding-right:2mm">PLANNED</td><td class="small" style="text-align:right;padding-right:2mm">SPENT</td></tr>
      ${tr}
    </table>
    <div style="height:15mm;display:flex;align-items:center;justify-content:center;gap:2mm;border-bottom:0.4mm solid ${C.ink};border-top:0.4mm solid ${C.ink};margin-top:2mm">
      <span class="red">${filled ? money(spent) : '$ ______'}</span><span style="font-size:18pt;color:#8d877d">/</span>
      <span style="font-size:17pt;letter-spacing:0.5mm">${filled ? money(planned) : '$ ______'}</span>
    </div>
    <div class="small" style="text-align:center;margin-top:0.8mm">spent / planned · <span style="background:${C.pinkSoft};padding:0 1mm">pink</span> = went over</div>
    <div class="small" style="margin-top:4mm">ACCOUNT BALANCES · end of month</div>
    ${acc}</div>`);
}

function extras(filled) {
  const col = (data, color, defaultTitle) => {
    const items = filled ? data.items : [];
    const total = items.reduce((s, [, v]) => s + v, 0);
    let lis = '';
    for (let i = 0; i < 12; i++) {
      const it = items[i];
      lis += `<div class="line" style="height:8.4mm;display:flex;align-items:flex-end;font-size:10.5pt;letter-spacing:0.3mm;padding-bottom:0.6mm">
        <span style="width:5mm">${i + 1}.</span><span style="flex:1">${it ? it[0].toUpperCase() : ''}</span>
        <span>${it ? `= ${hand('$' + it[1].toFixed(2), true)}` : '= $&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}</span></div>`;
    }
    return `<div style="flex:1;padding:0 2mm">
      <div style="text-align:center;margin-bottom:2mm"><span class="hl" style="background:${color}">${filled ? data.title.toUpperCase() : '&nbsp;'.repeat(36)}</span></div>
      ${lis}
      <div style="height:14mm;display:flex;align-items:center;justify-content:center;border-bottom:0.4mm solid ${C.ink}"><span class="red">${filled ? money(total) : '$'}</span></div>
    </div>`;
  };
  return page(C.yellow, 'MYSELF', `<div class="pad" style="display:flex;top:5mm;left:3mm;right:3mm;bottom:12mm">
      ${col(demo.extrasA, C.pink)}
      <div style="width:0.4mm;background:${C.ink};margin:0 1mm"></div>
      ${col(demo.extrasB, C.green)}
    </div>
    <div class="small" style="position:absolute;bottom:5mm;left:0;right:0;text-align:center">both totals together = MYSELF on your budget page</div>`);
}

function bills(filled) {
  const rows = filled ? [...demo.bills, ...Array(8).fill(null)] : Array(14).fill(null);
  const tr = rows.map((b) => `<tr style="height:8.6mm">
      <td class="line" style="font-size:11.5pt;letter-spacing:0.5mm">${b ? b[0].toUpperCase() : ''}</td>
      <td class="line" style="text-align:center">${b ? hand(b[1], true) : ''}</td>
      <td class="line" style="text-align:right;padding-right:2mm">${b ? hand('$' + b[2].toFixed(2), true) : ''}</td>
      <td class="line" style="text-align:center"><span style="display:inline-block;width:4.5mm;height:4.5mm;border:0.35mm solid ${C.ink};border-radius:1mm;background:${b && b[3] ? C.green : '#fff'};vertical-align:middle"></span></td></tr>`).join('');
  return page(C.pinkSoft, 'BILLS', `<div class="pad" style="top:4mm">
    <table style="width:100%">
      <colgroup><col style="width:40%"><col style="width:20%"><col style="width:26%"><col style="width:14%"></colgroup>
      <tr><td class="small">BILL</td><td class="small" style="text-align:center">DUE</td><td class="small" style="text-align:right;padding-right:2mm">AMOUNT</td><td class="small" style="text-align:center">PAID</td></tr>
      ${tr}
    </table>
    <div class="small" style="margin-top:4mm;text-align:center">colour the box green when it's paid</div></div>`);
}

function cellFill(filled, prob, color) {
  return filled && rnd() < prob ? `background:${color}` : '';
}

function habits(filled) {
  const H = demo.habits;
  const n = H.names.length;
  const dayW = 10, colW = (122 - dayW) / n;
  const groupRow = H.groups.map(([g, k, c]) => `<td colspan="${k}" style="border:0.3mm solid ${C.ink};text-align:center;font-size:8.5pt;letter-spacing:0.5mm;height:7mm;background:${c}">${g}</td>`).join('');
  // habit names print in both editions; the last column is left for the owner's own habit
  const names = H.names.map((nm) => `<td style="border:0.3mm solid ${C.ink};height:25mm;position:relative">
      <div style="position:absolute;left:2.2mm;bottom:2mm;transform:rotate(-62deg);transform-origin:left bottom;white-space:nowrap;font-size:9pt;letter-spacing:0.2mm">${nm || '<span style="color:#aaa">__________</span>'}</div></td>`).join('');
  const colColors = [];
  H.groups.forEach(([, k, c]) => { for (let i = 0; i < k; i++) colColors.push(c); });
  let body = '';
  for (let d = 1; d <= 31; d++) {
    body += `<tr style="height:4.2mm"><td style="border:0.25mm solid ${C.ink};text-align:center;font-size:8.5pt">${d}</td>` +
      colColors.map((c, i) => `<td style="border:0.25mm solid ${C.ink};${cellFill(filled, H.probs[i], c)}"></td>`).join('') + '</tr>';
  }
  return page(C.pink, 'HABITS', `
    <table style="position:absolute;left:3mm;top:3mm;width:122mm">
      <colgroup><col style="width:${dayW}mm">${`<col style="width:${colW}mm">`.repeat(n)}</colgroup>
      <tr><td></td>${groupRow}</tr>
      <tr><td style="border:0.3mm solid ${C.ink};font-size:8pt;text-align:center;vertical-align:bottom;padding-bottom:1mm">DAY</td>${names}</tr>
      ${body}
    </table>
    <div class="small" style="position:absolute;left:0;right:0;bottom:2mm;text-align:center">colour the box when it's done · last column is yours</div>`);
}

function tracker(filled) {
  const heads = ['H₂O', 'Protein', 'Steps', 'Sleep', 'Memory made 📷'];
  const widths = [15, 15, 15, 15, 52];
  const goals = demo.tracker.goals;
  let body = '';
  for (let d = 1; d <= 31; d++) {
    const water = [2.5, 2, 1.5, 2.5, 3, 2][Math.floor(rnd() * 6)];
    const protein = [45, 60, 80, 90, 70, 85][Math.floor(rnd() * 6)];
    const steps = [3, 4.5, 6.5, 7, 8.5, 11][Math.floor(rnd() * 6)];
    const sleep = [6, 6.5, 7, 8, 8.5, 9][Math.floor(rnd() * 6)];
    const mem = rnd() < 0.8 ? demo.memories[Math.floor(rnd() * demo.memories.length)] : '';
    const vals = filled ? [water + 'L', protein + 'g', steps + 'K', sleep + ' hr', mem] : ['', '', '', '', ''];
    const hit = filled ? [water >= 2.5, protein >= 80, steps >= 7, sleep >= 8, !!mem] : [];
    const hiCol = [C.yellow, C.yellow, C.yellow, C.yellow, C.pinkSoft];
    body += `<tr style="height:4.2mm"><td style="border:0.25mm solid ${C.ink};text-align:center;font-size:8.5pt">${d}</td>` +
      vals.map((v, i) => `<td style="border:0.25mm solid ${C.ink};text-align:${i === 4 ? 'left;padding-left:1.5mm' : 'center'};font-family:Gochi;font-size:8pt;color:#24305E;white-space:nowrap;overflow:hidden;${hit[i] ? `background:${hiCol[i]}` : ''}">${v}</td>`).join('') + '</tr>';
  }
  return page(C.pink, 'TRACKER', `
    <table style="position:absolute;left:3mm;top:3mm;width:122mm">
      <colgroup><col style="width:10mm">${widths.map((w) => `<col style="width:${w}mm">`).join('')}</colgroup>
      <tr><td></td><td colspan="4" style="border:0.3mm solid ${C.ink};text-align:center;font-size:8.5pt;letter-spacing:0.5mm;height:7mm;background:${C.yellow}">NUMBERS</td>
          <td style="border:0.3mm solid ${C.ink};text-align:center;font-size:8.5pt;letter-spacing:0.5mm;background:${C.pinkSoft}">TODAY'S PICTURE</td></tr>
      <tr style="height:10mm"><td style="border:0.3mm solid ${C.ink};font-size:8pt;text-align:center">DAY</td>
        ${heads.map((h) => `<td style="border:0.3mm solid ${C.ink};text-align:center;font-size:10pt">${h}</td>`).join('')}</tr>
      <tr style="height:6.5mm;background:#fff"><td style="border:0.3mm solid ${C.ink};font-size:7pt;text-align:center">GOAL</td>
        ${heads.map((_, i) => `<td style="border:0.3mm solid ${C.ink};text-align:center;font-family:Gochi;font-size:8.5pt;color:#24305E;${i === 4 ? 'background:#eee9e0' : ''}">${filled && goals[i] ? goals[i] : ''}</td>`).join('')}</tr>
      ${body}
    </table>
    <div class="small" style="position:absolute;left:0;right:0;bottom:2mm;text-align:center">highlight when you hit your goal · one memory a day</div>`);
}

function close(filled) {
  const lines = (arr, n) => Array.from({ length: n }, (_, i) =>
    `<div class="line" style="height:8.5mm;display:flex;align-items:flex-end;padding-bottom:0.6mm"><span style="width:6mm">${i + 1}.</span>${filled && arr[i] ? hand(arr[i], true) : ''}</div>`).join('');
  const moods = ['😣', '😕', '😐', '🙂', '😍'];
  return page(C.green, 'CHAPTER CLOSE', `<div class="pad" style="top:5mm">
    <span class="hl" style="background:${C.yellow}">3 WINS</span>${lines(demo.wins, 3)}
    <div style="height:5mm"></div>
    <span class="hl" style="background:${C.pink}">1 LESSON</span>${lines([demo.lesson], 2)}
    <div style="height:5mm"></div>
    <span class="hl" style="background:${C.green}">NEXT CHAPTER I WILL…</span>${lines([demo.next], 2)}
    <div style="height:6mm"></div>
    <div class="small" style="color:${C.ink}">MONEY MOOD THIS MONTH</div>
    <div style="display:flex;gap:4mm;margin-top:2mm">${moods.map((m, i) => `<div style="width:12mm;height:12mm;border-radius:50%;border:0.35mm solid ${C.ink};display:flex;align-items:center;justify-content:center;font-size:15pt;${filled && i === 3 ? `background:${C.yellow}` : 'background:#fff'}">${m}</div>`).join('')}</div>
    <div style="margin-top:6mm;display:flex;gap:3mm">
      <div style="flex:1;border:0.4mm solid ${C.ink};border-radius:2mm;padding:2mm;background:#fff"><div class="small">SAVED THIS CHAPTER</div><div class="red" style="font-size:16pt">${filled ? money(500) : '$'}</div></div>
      <div style="flex:1;border:0.4mm solid ${C.ink};border-radius:2mm;padding:2mm;background:#fff"><div class="small">BEST HABIT STREAK</div><div class="red" style="font-size:16pt;color:${C.greenDark}">${filled ? '31 days' : ''}</div></div>
    </div></div>`);
}

function build(filled) {
  seed = 7;
  const pages = [cover(), howTo(), opener(filled), chapterPage(filled), summary(filled), budget(filled), extras(filled), bills(filled), habits(filled), tracker(filled), close(filled)];
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${pages.join('')}</body></html>`;
}

(async () => {
  fs.mkdirSync(path.join(OUT, 'previews'), { recursive: true });
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ deviceScaleFactor: 2 });
  const p = await ctx.newPage();
  for (const [name, filled] of [['sample-filled', true], ['printable-blank', false]]) {
    const html = build(filled);
    const htmlPath = path.join(OUT, `chapter-by-chapter-${name}.html`);
    fs.writeFileSync(htmlPath, html);
    await p.goto('file://' + htmlPath);
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: path.join(OUT, `chapter-by-chapter-${name}.pdf`), width: '148mm', height: '210mm', printBackground: true, preferCSSPageSize: true });
    // one PNG per page for previews
    await p.setViewportSize({ width: 560, height: 794 });
    const sections = await p.$$('section.page');
    for (let i = 0; i < sections.length; i++) {
      await sections[i].screenshot({ path: path.join(OUT, 'previews', `${name}-${String(i + 1).padStart(2, '0')}.png`) });
    }
    fs.unlinkSync(htmlPath);
  }
  await browser.close();
  console.log('done');
})();
