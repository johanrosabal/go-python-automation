document.addEventListener('DOMContentLoaded', () => {
  // 0. Zero-Dependency Syntax Highlighter (VS Code Dark+ / One Dark Pro style)
  const PY_KEYWORDS = new Set([
    'from', 'import', 'class', 'def', 'return', 'assert', 'if', 'else', 'elif',
    'for', 'while', 'in', 'not', 'and', 'or', 'True', 'False', 'None', 'pass',
    'try', 'except', 'finally', 'with', 'as', 'raise', 'yield', 'lambda', 'true', 'false'
  ]);

  const PY_SELF = new Set(['self', 'cls', 'super']);

  const PY_TYPES = new Set([
    'BasePage', 'BaseComponent', 'BaseApp', 'BaseTest', 'BaseEndpoint', 'BaseAPITest',
    'LoginPage', 'InventoryPage', 'SidebarComponent', 'DemoApp', 'CheckoutPage',
    'TestLogin', 'TestLoginScenarios', 'TestCheckoutFlowE2E', 'UsersEndpoint', 'TestUsersAPI',
    'InputElement', 'ButtonElement', 'TextElement', 'DropdownElement', 'CheckboxElement',
    'TableElement', 'UploadElement', 'ContainerElement', 'MediaElement', 'UIElement',
    'str', 'int', 'float', 'bool', 'dict', 'list', 'tuple', 'set'
  ]);

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function highlightCode(raw) {
    // Single-pass master regex to tokenize strings, comments, decorators, kwargs, methods, words, and numbers
    const tokenRegex = /(#[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(@[a-zA-Z_]\w*)|(\b[a-zA-Z_]\w*(?=\s*=[^=]))|(\b[a-zA-Z_]\w*(?=\s*\())|(\.[a-zA-Z_]\w*)|(\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_]\w*\b)/g;

    let result = '';
    let lastIndex = 0;
    let match;

    while ((match = tokenRegex.exec(raw)) !== null) {
      if (match.index > lastIndex) {
        result += escapeHtml(raw.slice(lastIndex, match.index));
      }

      const [
        full,
        comment,
        stringLit,
        decorator,
        kwargName,
        funcCall,
        dotProp,
        numberLit,
        word
      ] = match;

      if (comment) {
        result += `<span class="tok-comment">${escapeHtml(comment)}</span>`;
      } else if (stringLit) {
        result += `<span class="tok-string">${escapeHtml(stringLit)}</span>`;
      } else if (decorator) {
        result += `<span class="tok-decorator">${escapeHtml(decorator)}</span>`;
      } else if (kwargName) {
        result += `<span class="tok-arg">${escapeHtml(kwargName)}</span>`;
      } else if (funcCall) {
        if (PY_TYPES.has(funcCall)) {
          result += `<span class="tok-class">${escapeHtml(funcCall)}</span>`;
        } else if (PY_SELF.has(funcCall)) {
          result += `<span class="tok-self">${escapeHtml(funcCall)}</span>`;
        } else {
          result += `<span class="tok-func">${escapeHtml(funcCall)}</span>`;
        }
      } else if (dotProp) {
        result += `.<span class="tok-prop">${escapeHtml(dotProp.slice(1))}</span>`;
      } else if (numberLit) {
        result += `<span class="tok-number">${escapeHtml(numberLit)}</span>`;
      } else if (word) {
        if (PY_KEYWORDS.has(word)) {
          result += `<span class="tok-keyword">${escapeHtml(word)}</span>`;
        } else if (PY_SELF.has(word)) {
          result += `<span class="tok-self">${escapeHtml(word)}</span>`;
        } else if (PY_TYPES.has(word)) {
          result += `<span class="tok-class">${escapeHtml(word)}</span>`;
        } else {
          result += escapeHtml(word);
        }
      } else {
        result += escapeHtml(full);
      }

      lastIndex = tokenRegex.lastIndex;
    }

    if (lastIndex < raw.length) {
      result += escapeHtml(raw.slice(lastIndex));
    }

    return result;
  }

  // Apply syntax highlighting and bind Copy buttons
  document.querySelectorAll('.code-block').forEach((block) => {
    const copyBtn = block.querySelector('.copy-btn');
    const pre = block.querySelector('pre');
    const codeEl = block.querySelector('pre code') || pre;

    if (codeEl && pre) {
      const rawText = codeEl.textContent;
      pre.dataset.rawCode = rawText;
      codeEl.innerHTML = highlightCode(rawText);

      if (copyBtn) {
        copyBtn.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(pre.dataset.rawCode || pre.innerText);
            const original = copyBtn.textContent;
            copyBtn.textContent = '✓ Copiado';
            setTimeout(() => {
              copyBtn.textContent = original;
            }, 1600);
          } catch (err) {
            copyBtn.textContent = 'Error';
          }
        });
      }
    }
  });

  // 1. Theme Toggle (GoDocs Light default, [data-theme="dark"] for Dark Mode)
  const themeBtn = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('docs_theme') || 'light';

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      if (themeBtn) themeBtn.textContent = '☀️ Modo Claro';
      localStorage.setItem('docs_theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      if (themeBtn) themeBtn.textContent = '🌙 Modo Oscuro';
      localStorage.setItem('docs_theme', 'light');
    }
  }

  // Initialize theme from saved preference
  applyTheme(savedTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      applyTheme(isDark ? 'light' : 'dark');
    });
  }

  // 2. Sidebar Toggle (Desktop Collapse/Expand & Mobile Drawer with Backdrop)
  const menuBtn = document.getElementById('menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  const isDesktop = () => window.innerWidth > 960;
  const savedCollapsed = localStorage.getItem('docs_sidebar_collapsed') === 'true';

  if (isDesktop() && savedCollapsed) {
    document.body.classList.add('sidebar-collapsed');
  }

  function toggleSidebar() {
    if (isDesktop()) {
      const collapsed = document.body.classList.toggle('sidebar-collapsed');
      localStorage.setItem('docs_sidebar_collapsed', collapsed);
    } else {
      const isOpen = sidebar.classList.toggle('open');
      if (backdrop) {
        backdrop.classList.toggle('active', isOpen);
      }
    }
  }

  function closeMobileSidebar() {
    if (!isDesktop() && sidebar && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      if (backdrop) backdrop.classList.remove('active');
    }
  }

  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleSidebar();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', () => {
      closeMobileSidebar();
    });
  }

  // Close mobile drawer when clicking any navigation link
  document.querySelectorAll('.sidebar .nav-link').forEach((link) => {
    link.addEventListener('click', () => {
      closeMobileSidebar();
    });
  });

  window.addEventListener('resize', () => {
    if (isDesktop()) {
      if (sidebar) sidebar.classList.remove('open');
      if (backdrop) backdrop.classList.remove('active');
      if (localStorage.getItem('docs_sidebar_collapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
      } else {
        document.body.classList.remove('sidebar-collapsed');
      }
    } else {
      document.body.classList.remove('sidebar-collapsed');
    }
  });

  // 3. Global Search & Autocomplete Dropdown (GoDocs Hugo / Algolia Style)
  const searchInput = document.getElementById('global-search');
  const searchDropdown = document.getElementById('search-dropdown');
  const sections = document.querySelectorAll('.doc-section');
  const navLinks = document.querySelectorAll('.sidebar .nav-link');

  // Build searchable index from sidebar links and section headings
  const searchIndex = [];

  document.querySelectorAll('.sidebar .nav-group').forEach((group) => {
    const groupTitle = group.querySelector('.nav-group-title')?.innerText || 'General';
    group.querySelectorAll('.nav-link').forEach((link) => {
      const href = link.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      const targetId = href.substring(1);
      const targetEl = document.getElementById(targetId);
      const title = link.innerText.trim();
      const textPreview = targetEl ? targetEl.innerText.substring(0, 300).replace(/\s+/g, ' ') : '';
      searchIndex.push({
        id: targetId,
        title: title,
        category: groupTitle,
        preview: textPreview,
        element: targetEl
      });
    });
  });

  // Also index inner sub-headings (h2, h3) that have ids or are inside sections
  document.querySelectorAll('.doc-section h2, .doc-section h3').forEach((heading) => {
    const parentSection = heading.closest('.doc-section');
    const targetId = heading.id || parentSection?.id;
    if (!targetId) return;
    const title = heading.innerText.trim();
    if (!searchIndex.some((item) => item.id === targetId && item.title === title)) {
      searchIndex.push({
        id: targetId,
        title: title,
        category: parentSection?.getAttribute('id') ? `Sección #${parentSection.id}` : 'Documentación',
        preview: heading.nextElementSibling ? heading.nextElementSibling.innerText.substring(0, 160) : '',
        element: heading
      });
    }
  });

  let selectedIndex = -1;

  function renderSearchResults(query) {
    if (!searchDropdown) return;
    const q = query.trim().toLowerCase();
    if (!q || q.length < 2) {
      searchDropdown.style.display = 'none';
      searchDropdown.innerHTML = '';
      selectedIndex = -1;
      return;
    }

    const matches = searchIndex.filter((item) => {
      return (
        item.title.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.id.toLowerCase().includes(q) ||
        item.preview.toLowerCase().includes(q)
      );
    }).slice(0, 8); // Max 8 results

    if (matches.length === 0) {
      searchDropdown.innerHTML = `
        <div class="search-no-results">
          🔍 No se encontraron coincidencias para <strong>"${escapeHtml(query)}"</strong>
        </div>
      `;
      searchDropdown.style.display = 'block';
      selectedIndex = -1;
      return;
    }

    searchDropdown.innerHTML = matches.map((match, idx) => `
      <div class="search-result-item" data-index="${idx}" data-target="#${match.id}">
        <div class="search-result-title">
          <span>${highlightMatch(match.title, q)}</span>
        </div>
        <div class="search-result-subtitle">
          📁 ${escapeHtml(match.category)} ${match.preview ? '• ' + highlightMatch(match.preview.substring(0, 75) + '...', q) : ''}
        </div>
      </div>
    `).join('');

    searchDropdown.style.display = 'block';
    selectedIndex = -1;

    // Attach click events
    searchDropdown.querySelectorAll('.search-result-item').forEach((item) => {
      item.addEventListener('click', () => {
        const targetHash = item.getAttribute('data-target');
        navigateToTarget(targetHash);
      });
    });
  }

  function highlightMatch(text, query) {
    if (!query) return escapeHtml(text);
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark style="background: rgba(255, 0, 79, 0.2); color: var(--accent-primary); font-weight: 800; border-radius: 2px; padding: 0 2px;">$1</mark>');
  }

  function escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function navigateToTarget(targetHash) {
    if (!targetHash) return;
    const targetEl = document.querySelector(targetHash);
    if (targetEl) {
      if (searchDropdown) searchDropdown.style.display = 'none';
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      targetEl.classList.remove('search-highlight-target');
      void targetEl.offsetWidth; // Force reflow
      targetEl.classList.add('search-highlight-target');
      setTimeout(() => targetEl.classList.remove('search-highlight-target'), 2800);
      try {
        history.pushState(null, '', targetHash);
      } catch (e) {}

      // Activate corresponding sidebar link
      navLinks.forEach((link) => {
        link.classList.toggle('active', link.getAttribute('href') === targetHash);
      });
    }
  }

  // Keyboard shortcut Ctrl+K
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      renderSearchResults(e.target.value);
    });

    searchInput.addEventListener('focus', (e) => {
      if (e.target.value.trim().length >= 2) {
        renderSearchResults(e.target.value);
      }
    });

    searchInput.addEventListener('keydown', (e) => {
      const items = searchDropdown?.querySelectorAll('.search-result-item');
      if (!items || items.length === 0 || searchDropdown.style.display === 'none') return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % items.length;
        updateSelectedResult(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + items.length) % items.length;
        updateSelectedResult(items);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (selectedIndex >= 0 && items[selectedIndex]) {
          const targetHash = items[selectedIndex].getAttribute('data-target');
          navigateToTarget(targetHash);
        } else if (items.length > 0) {
          const targetHash = items[0].getAttribute('data-target');
          navigateToTarget(targetHash);
        }
      } else if (e.key === 'Escape') {
        searchDropdown.style.display = 'none';
      }
    });
  }

  function updateSelectedResult(items) {
    items.forEach((item, idx) => {
      if (idx === selectedIndex) {
        item.classList.add('selected');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('selected');
      }
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (searchDropdown && !e.target.closest('.search-wrapper')) {
      searchDropdown.style.display = 'none';
    }
  });

  // 4. Prefix Explorer Filter
  const filterBtns = document.querySelectorAll('.filter-btn[data-category]');
  const prefixRows = document.querySelectorAll('#prefix-table tbody tr');

  filterBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      filterBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.getAttribute('data-category');
      prefixRows.forEach((row) => {
        if (cat === 'all' || row.getAttribute('data-cat') === cat) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  });

  // 5. Tabs Switching
  document.querySelectorAll('.tabs').forEach((tabContainer) => {
    const buttons = tabContainer.querySelectorAll('.tab-btn');
    const parent = tabContainer.parentElement;
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');
        buttons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        parent.querySelectorAll('.tab-panel').forEach((panel) => {
          panel.classList.toggle('active', panel.id === target);
        });
      });
    });
  });

  // 5b. Diagram Flow Tab Switcher
  const diagramTabs = document.querySelectorAll('.diagram-tab-pill');
  const diagramPanels = document.querySelectorAll('.diagram-content-panel');

  diagramTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const targetId = tab.getAttribute('data-diagram');
      diagramTabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      diagramPanels.forEach((panel) => {
        const isActive = panel.id === targetId;
        panel.classList.toggle('active', isActive);
      });
    });
  });

  // 6. Scroll-Spy for Sidebar Navigation
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach((link) => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    },
    { rootMargin: '-90px 0px -70% 0px', threshold: 0 }
  );

  sections.forEach((sec) => {
    if (sec.id) observer.observe(sec);
  });
});
