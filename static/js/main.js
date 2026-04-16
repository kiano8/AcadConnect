// AcadConnect — Main JS

document.addEventListener('DOMContentLoaded', () => {

  // ============================================================
  // Theme Toggle (localStorage, matches landing page behaviour)
  // ============================================================
  const themeBtn  = document.getElementById('theme-toggle-btn');
  const themeIcon = document.getElementById('theme-toggle-icon');

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (themeIcon) {
      themeIcon.className = theme === 'dark' ? 'ph ph-sun' : 'ph ph-moon';
    }
  }

  // On load: respect server-set value, but let localStorage override
  const serverTheme = document.documentElement.getAttribute('data-theme') || 'light';
  const savedTheme  = localStorage.getItem('theme');
  applyTheme(savedTheme || serverTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next    = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      localStorage.setItem('theme', next);
    });
  }

  // ============================================================
  // Mobile Sidebar Toggle
  // ============================================================
  const sidebarToggleBtn = document.getElementById('sidebar-toggle');
  const sidebar          = document.getElementById('app-sidebar');

  if (sidebarToggleBtn && sidebar) {
    sidebarToggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 600 &&
          !sidebar.contains(e.target) &&
          !sidebarToggleBtn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ============================================================
  // Notification Badge Polling
  // ============================================================
  function updateNotifBadge() {
    fetch('/notifications/api/unread/')
      .then(r => r.json())
      .then(data => {
        const count    = data.count;
        const topBadge = document.getElementById('topbar-notif-badge');
        const sideBadge= document.getElementById('sidebar-notif-count');
        if (topBadge) {
          topBadge.textContent = count;
          topBadge.style.display = count > 0 ? 'flex' : 'none';
        }
        if (sideBadge) {
          sideBadge.textContent = count;
          sideBadge.style.display = count > 0 ? 'inline-flex' : 'none';
        }
      })
      .catch(() => {});
  }

  if (document.querySelector('.sidebar')) {
    updateNotifBadge();
    setInterval(updateNotifBadge, 30000);
  }

  // ============================================================
  // Countdown Timers
  // ============================================================
  function updateCountdowns() {
    document.querySelectorAll('[data-deadline]').forEach(el => {
      const deadline = new Date(el.dataset.deadline);
      const now      = new Date();
      const diff     = deadline - now;

      if (diff <= 0) {
        el.textContent = 'Overdue';
        el.classList.add('urgent');
        return;
      }

      const days  = Math.floor(diff / 86400000);
      const hours = Math.floor((diff % 86400000) / 3600000);
      const mins  = Math.floor((diff % 3600000) / 60000);

      let text;
      if (days > 0)        text = `${days}d ${hours}h`;
      else if (hours > 0)  text = `${hours}h ${mins}m`;
      else                 text = `${mins}m left`;

      el.textContent = text;
      if (diff < 86400000) el.classList.add('urgent');
    });
  }

  updateCountdowns();
  setInterval(updateCountdowns, 60000);

  // ============================================================
  // Progress Bar Animation
  // ============================================================
  document.querySelectorAll('.progress-fill').forEach(bar => {
    const target = bar.dataset.progress || bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target; }, 120);
  });

  // ============================================================
  // Auto-dismiss Alerts
  // ============================================================
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      alert.style.transition = 'all 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 4500);
  });

  // ============================================================
  // Stress Level Display
  // ============================================================
  const stressRange   = document.getElementById('stress-range');
  const stressDisplay = document.getElementById('stress-display');
  if (stressRange && stressDisplay) {
    stressDisplay.textContent = stressRange.value;
    stressRange.addEventListener('input', () => {
      stressDisplay.textContent = stressRange.value;
      const val    = parseInt(stressRange.value);
      const colors = ['#52B788','#52B788','#52B788','#52B788',
                       '#E9C46A','#E9C46A','#F4A261','#F4A261',
                       '#E07A5F','#E07A5F'];
      stressDisplay.style.color = colors[val - 1] || '#52B788';
    });
  }


});
