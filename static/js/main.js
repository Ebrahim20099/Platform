// =============================
// Navbar Scroll Effect
// =============================

const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {

    if (window.scrollY > 30) {

        navbar.style.background =
            "rgba(5, 10, 22, 0.97)";

        navbar.style.backdropFilter =
            "blur(15px)";

    } else {

        navbar.style.background =
            "#ffffff";

        navbar.style.backdropFilter =
            "none";
    }

});





const menuBtn = document.querySelector(".menu-btn");
const sidebar = document.querySelector(".sidebar");
const closeBtn = document.querySelector(".close-btn");
const overlay = document.querySelector(".overlay");


// Open Sidebar

menuBtn.addEventListener("click", function () {

    sidebar.classList.add("active");

    overlay.classList.add("active");

});


// Close Sidebar

closeBtn.addEventListener("click", function () {

    sidebar.classList.remove("active");

    overlay.classList.remove("active");

});


// Close when clicking Overlay

overlay.addEventListener("click", function () {

    sidebar.classList.remove("active");

    overlay.classList.remove("active");

});





// =============================
// Code Typing Effect
// =============================

const output = document.querySelector(".output-level span");

let level = 0;
const targetLevel = 105;

function animateLevel() {

    if (level < targetLevel) {

        level++;

        output.textContent = level;

        setTimeout(animateLevel, 15);

    }

}

setTimeout(animateLevel, 800);


 




const examples = {
  js: `console.log("👋 أهلاً يا حريف");

const name = "إبراهيم";
console.log(\`منصة المهندس \${name}\`);

const username = "طالب جديد";
console.log(\`أهلاً \${username}\`);

const a = 7;
const b = 5;
console.log("الناتج:", a + b);`,

  python: `print("👋 أهلاً يا حريف")

name = "إبراهيم"
print(f"منصة المهندس {name}")

username = "طالب جديد"
print(f"أهلاً {username}")

a = 7
b = 5
print("الناتج:", a + b)`
};

const codeEl = document.getElementById('code');
const codeHighlightEl = document.getElementById('codeHighlight');
const lineNumbersEl = document.getElementById('lineNumbers');
const consoleBody = document.getElementById('consoleBody');
const emptyMsg = document.getElementById('emptyMsg');
const countText = document.getElementById('countText');
const errorText = document.getElementById('errorText');
const statusText = document.getElementById('statusText');
const langSelect = document.getElementById('langSelect');
const langTag = document.getElementById('langTag');
const fileName = document.getElementById('fileName');
const runBtn = document.getElementById('runBtn');

let currentLang = 'js';
let pyodideInstance = null;
let pyodideLoading = false;

codeEl.value = examples.js;
updateHighlight();
updateLineNumbers();

function escapeHtml(value){
  return value.replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
}

function updateHighlight(){
  const source = codeEl.value;
  const language = currentLang;
  const pattern = language === 'python'
    ? /(#[^\n]*|'''[\s\S]*?'''|"""[\s\S]*?"""|'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|\b\d+(?:\.\d+)?\b|\b(?:and|as|assert|async|await|break|class|def|elif|else|except|False|for|from|if|import|in|is|None|not|or|pass|print|raise|return|True|try|while|with|yield)\b|\b[A-Za-z_$][\w$]*(?=\s*\())/g
    : /(\/\/[^\n]*|\/\*[\s\S]*?\*\/|'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`|\b\d+(?:\.\d+)?\b|\b(?:const|let|var|function|return|if|else|for|while|class|new|this|true|false|null|undefined|async|await|try|catch|throw|import|from|export)\b|\b[A-Za-z_$][\w$]*(?=\s*\())/g;
  let output = '';
  let lastIndex = 0;
  let match;
  while ((match = pattern.exec(source)) !== null){
    output += escapeHtml(source.slice(lastIndex, match.index));
    const token = match[0];
    let className = 'token-keyword';
    if (/^(\/\/|\/\*|#)/.test(token)) className = 'token-comment';
    else if (/^[`'\"]/.test(token)) className = 'token-string';
    else if (/^\d/.test(token)) className = 'token-number';
    else if (/^[A-Za-z_$]/.test(token) && !/^(const|let|var|function|return|if|else|for|while|class|new|this|true|false|null|undefined|async|await|try|catch|throw|import|from|export|and|as|assert|break|def|elif|except|False|in|is|None|not|or|pass|print|raise|True|with|yield)$/.test(token)) className = 'token-function';
    output += `<span class="${className}">${escapeHtml(token)}</span>`;
    lastIndex = pattern.lastIndex;
  }
  codeHighlightEl.innerHTML = output + escapeHtml(source.slice(lastIndex)) + '\n';
}

codeEl.addEventListener('input', updateHighlight);
codeEl.addEventListener('scroll', () => {
  codeHighlightEl.scrollTop = codeEl.scrollTop;
  codeHighlightEl.scrollLeft = codeEl.scrollLeft;
  lineNumbersEl.scrollTop = codeEl.scrollTop;
});

function updateLineNumbers(){
  const lines = codeEl.value.split('\n').length;
  let out = '';
  for(let i=1;i<=lines;i++) out += i + '\n';
  lineNumbersEl.textContent = out;
}
codeEl.addEventListener('input', updateLineNumbers);
codeEl.addEventListener('scroll', ()=>{ lineNumbersEl.scrollTop = codeEl.scrollTop; });

function arNum(n){
  const map = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩'};
  return String(n).split('').map(c=>map[c]!==undefined?map[c]:c).join('');
}

function addLine(text, type){
  const div = document.createElement('div');
  div.className = 'console-line ' + type;
  div.textContent = text;
  consoleBody.appendChild(div);
}

function resetConsole(){
  consoleBody.innerHTML = '';
}

function showEmptyIfNeeded(logCount, errCount){
  if(logCount===0 && errCount===0){
    consoleBody.appendChild(emptyMsg);
    emptyMsg.style.display='block';
  }
}

// ---------- Language switching ----------
langSelect.addEventListener('change', ()=>{
  currentLang = langSelect.value;
  codeEl.value = examples[currentLang];
  updateHighlight();
  updateLineNumbers();
  clearConsoleUI();

  if(currentLang === 'js'){
    langTag.textContent = 'JS';
    langTag.classList.remove('py');
    fileName.textContent = 'playground.js';
  } else {
    langTag.textContent = 'PY';
    langTag.classList.add('py');
    fileName.textContent = 'playground.py';
    ensurePyodide();
  }
});

function clearConsoleUI(){
  resetConsole();
  consoleBody.appendChild(emptyMsg);
  emptyMsg.style.display='block';
  emptyMsg.textContent = 'اكتب الكود واضغط «شغّل الكود» — النتيجة هتظهر هنا.';
  countText.textContent = '٠ نتائج';
  errorText.textContent = '٠ خطأ';
  statusText.textContent = 'جاهز';
}

// ---------- Pyodide (Python) ----------
function ensurePyodide(){
  if(pyodideInstance || pyodideLoading) return;
  pyodideLoading = true;
  statusText.textContent = 'جاري تحميل بايثون...';
  runBtn.disabled = true;

  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js';
  script.onload = async () => {
    try{
      pyodideInstance = await loadPyodide();
      statusText.textContent = 'جاهز';
    }catch(e){
      statusText.textContent = 'تعذّر تحميل بايثون';
    }
    pyodideLoading = false;
    runBtn.disabled = false;
  };
  script.onerror = () => {
    statusText.textContent = 'تعذّر تحميل بايثون (تحقق من الاتصال)';
    pyodideLoading = false;
    runBtn.disabled = false;
  };
  document.head.appendChild(script);
}

// ---------- Run JS ----------
function runJS(){
  resetConsole();
  let logCount = 0, errCount = 0;

  function fmt(arg){
    if(typeof arg === 'object' && arg !== null){
      try { return JSON.stringify(arg); } catch(e){ return String(arg); }
    }
    return String(arg);
  }

  const fakeConsole = {
    log: (...args) => { addLine(args.map(fmt).join(' '), 'log'); logCount++; },
    error: (...args) => { addLine(args.map(fmt).join(' '), 'error'); errCount++; },
    warn: (...args) => { addLine(args.map(fmt).join(' '), 'warn'); logCount++; }
  };

  try{
    const fn = new Function('console', codeEl.value);
    fn(fakeConsole);
    statusText.textContent = 'تم التنفيذ';
  }catch(err){
    addLine(err.message, 'error');
    errCount++;
    statusText.textContent = 'فيه خطأ';
  }

  showEmptyIfNeeded(logCount, errCount);
  countText.textContent = arNum(logCount) + ' نتائج';
  errorText.textContent = arNum(errCount) + ' خطأ';
}

// ---------- Run Python ----------
async function runPython(){
  resetConsole();
  let logCount = 0, errCount = 0;

  if(!pyodideInstance){
    addLine('بايثون لسه بيتحمّل، استنى شوية وحاول تاني...', 'warn');
    logCount++;
    ensurePyodide();
    showEmptyIfNeeded(logCount, errCount);
    countText.textContent = arNum(logCount) + ' نتائج';
    errorText.textContent = arNum(errCount) + ' خطأ';
    return;
  }

  statusText.textContent = 'جاري التنفيذ...';
  runBtn.disabled = true;

  try{
    pyodideInstance.setStdout({
      batched: (text) => {
        if(text.trim().length){
          addLine(text, 'log');
          logCount++;
        }
      }
    });
    pyodideInstance.setStderr({
      batched: (text) => {
        if(text.trim().length){
          addLine(text, 'error');
          errCount++;
        }
      }
    });

    await pyodideInstance.runPythonAsync(codeEl.value);
    statusText.textContent = 'تم التنفيذ';
  }catch(err){
    addLine(err.message, 'error');
    errCount++;
    statusText.textContent = 'فيه خطأ';
  }

  runBtn.disabled = false;
  showEmptyIfNeeded(logCount, errCount);
  countText.textContent = arNum(logCount) + ' نتائج';
  errorText.textContent = arNum(errCount) + ' خطأ';
}

function runCode(){
  if(currentLang === 'js'){
    runJS();
  } else {
    runPython();
  }
}

runBtn.addEventListener('click', runCode);

document.getElementById('clearResultBtn').addEventListener('click', clearConsoleUI);
document.getElementById('clearBtn2').addEventListener('click', clearConsoleUI);

document.getElementById('resetBtn').addEventListener('click', ()=>{
  codeEl.value = examples[currentLang];
  updateHighlight();
  updateLineNumbers();
  clearConsoleUI();
});

document.getElementById('copyBtn').addEventListener('click', ()=>{
  navigator.clipboard.writeText(codeEl.value).then(()=>{
    const btn = document.getElementById('copyBtn');
    const original = btn.textContent;
    btn.textContent = '✔ تم النسخ';
    setTimeout(()=>{ btn.textContent = original; }, 1200);
  });
});

codeEl.addEventListener('keydown', (e)=>{
  if((e.ctrlKey || e.metaKey) && e.key === 'Enter'){
    e.preventDefault();
    runCode();
  }
  if(e.key === 'Tab'){
    e.preventDefault();
    const start = codeEl.selectionStart;
    const end = codeEl.selectionEnd;
    codeEl.value = codeEl.value.substring(0,start) + '    ' + codeEl.value.substring(end);
    codeEl.selectionStart = codeEl.selectionEnd = start + 4;
    updateLineNumbers();
    updateHighlight();
  }
});




if (document.getElementById('cardsGrid') && !document.getElementById('courseData')) {
const packages = [
  {
    id: 1,
    grade: "first",
    gradeLabel: "الصف الأول الثانوي",
    title: "باقة الشهر الأول + الملزمة - أولى ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 280,
    gradient: "linear-gradient(135deg,#3a3f6b,#8a5a2e)",
    image: "../static/images/first-1.png"
  },
  {
    id: 2,
    grade: "first",
    gradeLabel: "الصف الأول الثانوي",
    title: "الحصة الأولى - أولى ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 70,
    gradient: "linear-gradient(135deg,#1f3a5f,#173a52)",
    image: "../static/images/first-2.png"
  },
  {
    id: 3,
    grade: "second",
    gradeLabel: "الصف الثاني الثانوي",
    title: "الحصة الثانية - تانية ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 80,
    gradient: "linear-gradient(135deg,#355c4a,#1d3b46)",
    image: "../static/images/second-2.png"
  },
  {
    id: 4,
    grade: "first",
    gradeLabel: "الصف الأول الثانوي",
    title: "الحصة الثانية - أولى ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 70,
    gradient: "linear-gradient(135deg,#355c4a,#1d3b46)",
    image: "../static/images/first-3.png"
  },
  {
    id: 5,
    grade: "second",
    gradeLabel: "الصف الثاني الثانوي",
    title: "باقة الشهر الأول + الملزمة - تانية ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 320,
    gradient: "linear-gradient(135deg,#6b3a3a,#3f2436)",
    image: "../static/images/Untitled-1.png"
  },
  {
    id: 6,
    grade: "second",
    gradeLabel: "الصف الثاني الثانوي",
    title: "الحصة الأولى - تانية ثانوي",
    date: "٢٠٢٦/٠٧/٣١",
    newPrice: 80,
    gradient: "linear-gradient(135deg,#1f3a5f,#173a52)",
    image: "../static/images/second-3.png"
  },
];

const grid = document.getElementById('cardsGrid');
const filterBar = document.getElementById('filterBar');

function renderCards(filterGrade){
  grid.innerHTML = '';

  const list = filterGrade === 'all'
    ? packages
    : packages.filter(p => p.grade === filterGrade);

  if(list.length === 0){
    grid.innerHTML = '<div class="no-results">مفيش باقات متاحة للصف ده حاليًا</div>';
    return;
  }

  list.forEach(pkg => {
    const card = document.createElement('div');
    card.className = 'card';

    const bg = pkg.image ? `url('${pkg.image}')` : pkg.gradient;

    card.innerHTML = `
      <div class="card-image" style="background: ${bg}; background-size: cover; background-position: center; background-repeat: no-repeat; border-radius: 10px;">
        <div class="card-logo"><span class="dot">🕊️</span> bird</div>
      </div>
      <div class="card-body">
        <div class="card-tags">
          <h3 class="card-title">${pkg.title}</h3>
          <span class="grade-tag">${pkg.gradeLabel}</span>
        </div>
        <div class="card-date">📅 ${pkg.date}</div>
        <div class="price-box">
          ${pkg.oldPrice ? `<span class="price-old">${pkg.oldPrice} <span class="price-currency">ج.م</span></span>` : ''}
          <span class="price-new">${pkg.newPrice} <span class="price-currency">ج.م</span></span>
        </div>
        <button class="subscribe-btn">🛒 إشترك الأن</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

filterBar.addEventListener('click', (e)=>{
  const btn = e.target.closest('.filter-pill');
  if(!btn) return;

  filterBar.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');

  renderCards(btn.dataset.grade);
});

renderCards('all');
}
 








const icons = document.querySelectorAll(".floating-icon");

document.addEventListener("mousemove", function (e) {

    const mouseX = e.clientX;
    const mouseY = e.clientY;

    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;

    const moveX = mouseX - centerX;
    const moveY = mouseY - centerY;

    icons.forEach((icon, index) => {

        const speed = (index + 1) * 0.01;

        icon.style.transform = `
            translate(
                ${moveX * speed}px,
                ${moveY * speed}px
            )
        `;
    });

});