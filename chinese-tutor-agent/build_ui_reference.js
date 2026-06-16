/* Build ai-atlas-ui-reference.html — 10 màn tĩnh trong khung phone, KHÔNG logic JS.
   Render mỗi scr*() với state mẫu, nhúng kết quả tĩnh vào grid. Dùng làm reference UI. */
const fs = require('fs');

const src = fs.readFileSync('ai-atlas.html', 'utf-8');

// 1. Lấy CSS (giữ nguyên design system)
const css = src.match(/<style>([\s\S]*?)<\/style>/)[1];

// 2. Lấy JS, eval trong sandbox để gọi các hàm render
const jsBlocks = src.match(/<script>([\s\S]*?)<\/script>/g).map(b => b.replace(/<\/?script>/g, ''));
let js = jsBlocks.join('\n');

// stub DOM/browser APIs mà code đụng (chỉ cần để các hàm render chạy, không cần thật)
const sandbox = {
  document: {
    getElementById: () => ({ style:{}, classList:{add(){},remove(){}}, querySelector:()=>({style:{},classList:{add(){},remove(){}}}), innerHTML:'', value:'', textContent:'', appendChild(){}, addEventListener(){} }),
    createElement: () => ({ style:{}, classList:{add(){}}, querySelector:()=>({}), appendChild(){}, innerHTML:'' }),
    createTextNode: (t) => t,
  },
  window: { speechSynthesis:{ getVoices:()=>[], speak(){}, cancel(){}, onvoiceschanged:null }, AudioContext:function(){}, addEventListener(){} },
  localStorage: { getItem:()=>null, setItem(){}, },
  location: { hash:'' },
  speechSynthesis: { getVoices:()=>[], speak(){}, cancel(){} },
  setTimeout: ()=>{}, setInterval: ()=>{}, requestAnimationFrame: ()=>{},
  console,
};

// chạy JS trong vm với sandbox, expose các hàm render + data + state S
const vm = require('vm');
const ctx = vm.createContext(sandbox);
// bọc để bắt lỗi init (render() ở cuối sẽ fail vì DOM stub — bỏ qua)
const wrapped = js.replace(/\nrender\(\);?\s*$/,'\n/* skip boot render */');
try { vm.runInContext(wrapped, ctx); } catch(e){ /* init code có thể lỗi, kệ — ta chỉ cần các hàm */ }

// 3. Chuẩn bị state mẫu — set qua runInContext vì let/const không expose ra ctx
vm.runInContext(`
  S.city='chengdu';
  S.known=new Set(['山','口','人','火','锅','辣','茶','吃','喝','水','我','爱','你','好','日','月','木']);
  S.collected=new Set(['chengdu','shanghai']);
  S.cityProgress={chengdu:42,shanghai:18,beijing:0,hangzhou:0,xian:0,guilin:0};
  S.streak=12; S.xp=2840; S.decodeIdx=5;
  curTone=2; curSyl='ma'; pinyinInitial='b'; toneScore=82; toneSim=false; recording=false;
`, ctx);

// 4. Render từng màn — gọi hàm qua runInContext
function safe(fn, ...args){
  try {
    const argStr = args.map(a=>JSON.stringify(a)).join(',');
    return vm.runInContext(`(typeof ${fn}==='function') ? ${fn}(${argStr}) : '__NA__'`, ctx) || '__NA__';
  } catch(e){ return `<div style="padding:40px;color:#c0392b">[${fn} lỗi: ${e.message}]</div>`; }
}

// lesson: render shell rồi fill bằng renderLesson với data mẫu (vì bản gốc async)
let lessonHtml = safe('scrLessonShell');
const lessonData = { hanzi:'我爱辣火锅', pinyin:'wǒ ài là huǒ guō', vi:'Tôi thích lẩu cay', newChar:'辣', newPin:'là', newVi:'cay', story:'Hẻm Chengdu, hơi nồi lẩu bốc lên giữa lồng đèn đỏ.' };
// thay phần lessonBody loading bằng nội dung bài học tĩnh (gọi renderLesson cần DOM — render thủ công)
// đơn giản: chèn 1 placeholder bài học vào shell
lessonHtml = lessonHtml.replace(/MÂY đang soạn[\s\S]*?<\/div><\/div>/,
  `<div class="eyebrow eb-gold">Bài học sinh tại chỗ</div>
   <div class="han" style="font-size:38px;letter-spacing:4px;text-align:center;margin:14px 0">我 爱 <span style="color:var(--gold);border-bottom:2px dotted var(--gold)">辣</span> 火 锅</div>
   <div class="pin" style="color:var(--gold);text-align:center">wǒ ài là huǒ guō</div>
   <div style="text-align:center;font-size:13px;color:var(--ivory);margin-top:6px">Tôi thích lẩu cay</div></div>`);

const screens = [
  ['01 · Onboard',     safe('scrOnboard'),    'onboard'],
  ['02 · City Pick',   safe('scrCityPick'),   ''],
  ['03 · Seed',        safe('scrSeed'),       ''],
  ['04 · Atlas',       safe('scrAtlas'),      ''],
  ['05 · City Detail', safe('scrCityDetail'), ''],
  ['06 · Lesson',      lessonHtml,            'lesson'],
  ['07 · Tone',        safe('scrTone'),       ''],
  ['08 · Pinyin',      safe('scrPinyin'),     ''],
  ['09 · Decode',      safe('scrDecode'),     ''],
  ['10 · Progress',    safe('scrProgress'),   ''],
];

// 5. Tab bar tĩnh (cho các màn có tab)
const TABS = vm.runInContext('JSON.stringify(typeof TABS!=="undefined"?TABS:[])', ctx);
const tabsArr = JSON.parse(TABS);
const tabbarHtml = tabsArr.map(t => `<button class="${t.s==='atlas'?'active':''}"><span class="ic">${t.ic}</span>${t.label}</button>`).join('');

// 6. Lắp trang reference
const DARK = new Set(['onboard','lesson','camera']);
const phones = screens.map(([title, html, key]) => {
  const dark = DARK.has(key);
  const showTab = !['onboard','citypick','seed'].includes(key) && key!=='';
  return `
  <div class="phone-wrap">
    <div class="phone-title">${title}</div>
    <div class="phone" style="background:${dark?'var(--navy)':'var(--ivory)'}">
      <div class="statusbar" style="color:${dark?'var(--ivory)':'var(--navy)'}"><span>9:41</span><span>●●● ⓦ ▮</span></div>
      <div class="view">${html}</div>
      ${showTab||key===''?`<div class="tabbar ${dark?'dark':''}">${tabbarHtml}</div>`:''}
    </div>
  </div>`;
}).join('\n');

const out = `<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI ATLAS · UI Reference (10 màn tĩnh)</title>
<style>
${css}
/* ===== reference layout ===== */
body{background:#15110d;display:block;padding:40px 20px}
.ref-header{max-width:1400px;margin:0 auto 30px;color:var(--ivory)}
.ref-header h1{font-family:var(--font-disp);font-size:32px;font-weight:900;letter-spacing:-1px}
.ref-header p{color:var(--stone);font-size:14px;margin-top:6px;max-width:700px;line-height:1.5}
.ref-tokens{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.tok{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.05);padding:8px 12px;font-size:12px;color:var(--ivory)}
.tok .sw{width:18px;height:18px;border:1px solid rgba(255,255,255,.2)}
.grid{display:flex;flex-wrap:wrap;gap:30px;justify-content:center;max-width:1400px;margin:0 auto}
.phone-wrap{display:flex;flex-direction:column;align-items:center}
.phone-title{color:var(--gold);font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;font-family:var(--font-body)}
.phone{width:300px;height:640px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 14px 50px rgba(0,0,0,.5);position:relative}
.phone .statusbar{height:36px;min-height:36px;display:flex;align-items:center;justify-content:space-between;padding:0 18px;font-size:12px;font-weight:600}
.phone .view{flex:1;overflow:hidden;position:relative;transform-origin:top left}
.phone .tabbar{height:54px;min-height:54px;display:flex;border-top:1px solid var(--line);background:var(--ivory)}
.phone .tabbar.dark{background:var(--navy);border-top-color:rgba(255,255,255,.08)}
.phone .tabbar button{flex:1;border:none;background:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:8px;color:var(--stone);text-transform:uppercase}
.phone .tabbar button .ic{font-size:16px}
.phone .tabbar button.active{color:var(--red)}
.phone .tabbar.dark button{color:rgba(247,242,234,.45)}
.phone .tabbar.dark button.active{color:var(--gold)}
/* thu nhỏ nội dung vừa khung 300px (gốc 390px) */
.phone .view > .scr{ transform:scale(.77); transform-origin:top left; width:130%; }
</style></head>
<body>
<div class="ref-header">
  <h1>AI ATLAS — UI Reference</h1>
  <p>10 màn hình tĩnh (không logic JS) để tham chiếu khi xây bộ UI khác. Design system: editorial luxury — Midnight Navy / Imperial Red / Champagne Gold, bo góc 0, font Inter Tight (headline) + Noto Serif SC (chữ Hán). CSS đầy đủ nằm trong &lt;style&gt; của file này.</p>
  <div class="ref-tokens">
    <span class="tok"><span class="sw" style="background:#0D1726"></span>Midnight Navy #0D1726</span>
    <span class="tok"><span class="sw" style="background:#B33A2E"></span>Imperial Red #B33A2E</span>
    <span class="tok"><span class="sw" style="background:#D4B27A"></span>Champagne Gold #D4B27A</span>
    <span class="tok"><span class="sw" style="background:#2D7466"></span>Jade #2D7466</span>
    <span class="tok"><span class="sw" style="background:#F7F2EA"></span>Ivory #F7F2EA</span>
    <span class="tok"><span class="sw" style="background:#8E8576"></span>Stone #8E8576</span>
  </div>
</div>
<div class="grid">
${phones}
</div>
</body></html>`;

fs.writeFileSync('ai-atlas-ui-reference.html', out);
console.log('Tạo ai-atlas-ui-reference.html:', Math.round(out.length/1024), 'KB');
console.log('Số màn render:', screens.length);
// báo màn nào render lỗi/n/a
screens.forEach(([t,h]) => { if(h.includes('lỗi:')||h.includes('n/a')) console.log('  ⚠️', t, '→', h.match(/\[.*?\]/)?.[0]); });
