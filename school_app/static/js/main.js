const grid = document.getElementById('cardsGrid');
const filterBar = document.getElementById('filterBar');
const modalOverlay = document.getElementById('codeModalOverlay');
const modalCourseTitle = document.getElementById('modalCourseTitle');
const codeInput = document.getElementById('codeInput');
const codeError = document.getElementById('codeError');
const submitCodeBtn = document.getElementById('submitCodeBtn');
const closeModalBtn = document.getElementById('closeModal');

let activeCourseId = null;

function renderCards(filterGrade) {
  grid.innerHTML = '';

  const list = filterGrade === 'all'
    ? packages
    : packages.filter(p => p.grade === filterGrade);

  if (list.length === 0) {
    grid.innerHTML = '<div class="no-results">مفيش باقات متاحة للصف ده حاليًا</div>';
    return;
  }

  list.forEach(pkg => {
    const card = document.createElement('div');
    card.className = 'card';

    const bg = pkg.image ? `url('${pkg.image}')` : pkg.gradient;

    card.innerHTML = `
      <div class="card-image" style="background: ${bg}; background-size: cover; background-position: center; background-repeat: no-repeat;">
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
        <button class="subscribe-btn" data-id="${pkg.id}" data-title="${pkg.title}">🛒 إشترك الأن</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

filterBar.addEventListener('click', (e) => {
  const btn = e.target.closest('.filter-pill');
  if (!btn) return;

  filterBar.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');

  renderCards(btn.dataset.grade);
});

// فتح البوباب لما يدوس اشتراك
grid.addEventListener('click', (e) => {
  const btn = e.target.closest('.subscribe-btn');
  if (!btn) return;

  activeCourseId = parseInt(btn.dataset.id, 10);
  modalCourseTitle.textContent = btn.dataset.title;
  codeInput.value = '';
  codeError.textContent = '';
  modalOverlay.classList.add('open');
  codeInput.focus();
});

function closeModal() {
  modalOverlay.classList.remove('open');
  activeCourseId = null;
}

closeModalBtn.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', (e) => {
  if (e.target === modalOverlay) closeModal();
});

async function submitCode() {
  const code = codeInput.value.trim();
  if (!code) {
    codeError.textContent = 'من فضلك اكتب الكود';
    return;
  }

  submitCodeBtn.disabled = true;
  submitCodeBtn.textContent = 'جاري التحقق...';
  codeError.textContent = '';

  try {
    const res = await fetch('/api/verify-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ course_id: activeCourseId, code })
    });
    const data = await res.json();

    if (data.success) {
      window.location.href = data.redirect_url;
    } else {
      codeError.textContent = data.message || 'حصل خطأ، حاول تاني';
    }
  } catch (err) {
    codeError.textContent = 'حصل خطأ في الاتصال، حاول تاني';
  } finally {
    submitCodeBtn.disabled = false;
    submitCodeBtn.textContent = 'تأكيد الكود';
  }
}

submitCodeBtn.addEventListener('click', submitCode);
codeInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') submitCode();
});

renderCards('all');
