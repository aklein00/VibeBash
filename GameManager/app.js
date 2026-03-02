const STATUS_CONFIG = {
  'shipped':        { label: 'Shipped',        color: 'green' },
  'polished':       { label: 'Polished',       color: 'green' },
  'active-dev':     { label: 'Active Dev',     color: 'cyan' },
  'prototype':      { label: 'Prototype',      color: 'yellow' },
  'pre-production': { label: 'Pre-Production', color: 'orange' },
  'concept':        { label: 'Concept',        color: 'gray' },
  'on-hold':        { label: 'On Hold',        color: 'gray' },
};

const FILTERS = ['All', 'Active', 'Shipped', 'Prototype', 'Pre-Production', 'On Hold'];

let catalog = null;
let activeFilter = 'All';
let searchQuery = '';
let versionData = null;   // from versions.json (current project deps)
let latestVersions = {};  // { packageName: latestVersion } from npm registry
let versionChecked = false;
let scanData = null;
let scanChecked = false;
let scanStale = false;

const SCAN_CACHE_KEY = 'gamemanager_scan_cache';

const CACHE_KEY = 'gamemanager_version_cache';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

// Key packages to always highlight
const KEY_PACKAGES = [
  '@series-inc/venus-sdk', '@series-inc/rundot-game-sdk',
  'phaser', 'three', 'vite', 'react', 'typescript',
];

async function init() {
  const res = await fetch('catalog.json');
  catalog = await res.json();
  renderStats();
  renderFilters();
  renderGrid();
  setupSearch();
  setupModal();
  setupVersionChecker();
  setupExportPrompt();
  setupAnalyze();

  // Restore cached scan data
  const cachedScan = loadScanCache();
  if (cachedScan) {
    scanData = cachedScan.data;
    scanStale = cachedScan.stale;
    scanChecked = true;

    const btn = document.getElementById('analyze-projects');
    const { outOfSync, new: newCount } = scanData.summary;
    if (outOfSync > 0 || newCount > 0) {
      btn.textContent = `${outOfSync + newCount} Out of Sync`;
      btn.classList.add('has-outdated');
    } else {
      btn.textContent = 'All In Sync';
      btn.classList.add('done');
    }

    renderGrid();
  }
}

// ── Version Checker ──────────────────────────────────────────

function loadCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const cached = JSON.parse(raw);
    if (Date.now() - cached.timestamp > CACHE_TTL) {
      localStorage.removeItem(CACHE_KEY);
      return null;
    }
    return cached.data;
  } catch { return null; }
}

function saveCache(data) {
  localStorage.setItem(CACHE_KEY, JSON.stringify({ timestamp: Date.now(), data }));
}

function loadScanCache() {
  try {
    const raw = localStorage.getItem(SCAN_CACHE_KEY);
    if (!raw) return null;
    const cached = JSON.parse(raw);
    const age = Date.now() - cached.timestamp;
    return { data: cached.data, stale: age > CACHE_TTL };
  } catch { return null; }
}

function saveScanCache(data) {
  localStorage.setItem(SCAN_CACHE_KEY, JSON.stringify({ timestamp: Date.now(), data }));
}

function timeAgo(dateString) {
  const now = Date.now();
  const then = new Date(dateString).getTime();
  if (isNaN(then)) return '';
  const seconds = Math.floor((now - then) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return minutes === 1 ? '1 minute ago' : `${minutes} minutes ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return days === 1 ? '1 day ago' : `${days} days ago`;
  const months = Math.floor(days / 30);
  return months === 1 ? '1 month ago' : `${months} months ago`;
}

function updateVersionScanAge(generatedAt) {
  const el = document.getElementById('version-scan-age');
  if (!el || !generatedAt) return;
  const age = Date.now() - new Date(generatedAt).getTime();
  const isStale = age > CACHE_TTL;
  const ago = timeAgo(generatedAt);
  el.textContent = `Scanned ${ago}`;
  el.className = 'version-scan-age' + (isStale ? ' version-scan-stale' : '');
  el.title = isStale
    ? 'Dependency snapshot is stale. Run: python3 scanner.py --versions'
    : `versions.json generated ${new Date(generatedAt).toLocaleString()}`;
}

function getScanInfoForProject(slug) {
  if (!scanData || !scanData.report) return null;
  const project = catalog.projects.find(p => p.slug === slug);
  if (!project) return null;
  const projectName = project.name.toLowerCase().replace(/\s/g, '');
  for (const item of scanData.report) {
    const scanName = item.name.toLowerCase().replace(/[\s_-]/g, '');
    if (scanName === projectName || item.name === project.name) {
      return item.scanned;
    }
  }
  return null;
}

async function fetchLatestVersion(pkg) {
  const url = `https://registry.npmjs.org/${encodeURIComponent(pkg)}/latest`;
  const res = await fetch(url);
  if (!res.ok) return null;
  const json = await res.json();
  return json.version || null;
}

function cleanVersion(v) {
  // Strip ^, ~, >=, etc. to get bare semver
  return (v || '').replace(/^[^0-9]*/, '');
}

function isOutdated(current, latest) {
  if (!current || !latest) return false;
  const c = cleanVersion(current).split('.').map(Number);
  const l = latest.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    if ((l[i] || 0) > (c[i] || 0)) return true;
    if ((l[i] || 0) < (c[i] || 0)) return false;
  }
  return false;
}

function isCriticallyOutdated(current, latest) {
  if (!current || !latest) return false;
  const cMajor = parseInt(cleanVersion(current).split('.')[0]) || 0;
  const lMajor = parseInt(latest.split('.')[0]) || 0;
  return lMajor > cMajor;
}

function getProjectVersionInfo(slug) {
  if (!versionData || !versionData.projects[slug]) return null;
  const deps = versionData.projects[slug].dependencies;
  const results = [];
  // Show key packages first, then others
  const seen = new Set();
  for (const pkg of KEY_PACKAGES) {
    if (deps[pkg]) {
      seen.add(pkg);
      results.push({ pkg, current: deps[pkg], latest: latestVersions[pkg] || null });
    }
  }
  for (const [pkg, ver] of Object.entries(deps)) {
    if (!seen.has(pkg)) {
      results.push({ pkg, current: ver, latest: latestVersions[pkg] || null });
    }
  }
  return results;
}

function countOutdated(slug) {
  const info = getProjectVersionInfo(slug);
  if (!info) return { total: 0, critical: 0 };
  const total = info.filter(d => isOutdated(d.current, d.latest)).length;
  const critical = info.filter(d => isCriticallyOutdated(d.current, d.latest)).length;
  return { total, critical };
}

async function checkVersions() {
  const btn = document.getElementById('check-versions');
  btn.textContent = 'Checking...';
  btn.classList.remove('done', 'has-outdated');
  btn.classList.add('loading');

  try {
    // Load versions.json
    const res = await fetch('versions.json');
    if (!res.ok) throw new Error('versions.json not found — run: python3 scanner.py --versions');
    versionData = await res.json();

    // Check cache first
    const cached = loadCache();
    if (cached) {
      latestVersions = cached;
    } else {
      // Collect unique packages across all projects
      const allPkgs = new Set();
      for (const proj of Object.values(versionData.projects)) {
        for (const pkg of Object.keys(proj.dependencies)) {
          allPkgs.add(pkg);
        }
      }

      // Fetch latest versions (batch with concurrency limit)
      const pkgList = [...allPkgs];
      const results = {};
      const BATCH = 6;
      for (let i = 0; i < pkgList.length; i += BATCH) {
        const batch = pkgList.slice(i, i + BATCH);
        btn.textContent = `Checking ${i + batch.length}/${pkgList.length}...`;
        const fetched = await Promise.all(batch.map(async pkg => {
          const latest = await fetchLatestVersion(pkg);
          return [pkg, latest];
        }));
        for (const [pkg, ver] of fetched) {
          if (ver) results[pkg] = ver;
        }
      }
      latestVersions = results;
      saveCache(results);
    }

    versionChecked = true;

    // Show when versions.json was generated
    updateVersionScanAge(versionData.generatedAt);

    // Count total outdated
    let totalOutdated = 0;
    for (const slug of Object.keys(versionData.projects)) {
      totalOutdated += countOutdated(slug).total;
    }

    btn.classList.remove('loading');
    if (totalOutdated > 0) {
      btn.textContent = `${totalOutdated} Outdated`;
      btn.classList.add('has-outdated');
    } else {
      btn.textContent = 'All Up to Date';
      btn.classList.add('done');
    }

    renderGrid();
  } catch (err) {
    btn.classList.remove('loading');
    btn.textContent = 'Error';
    btn.title = err.message;
    console.error('Version check failed:', err);
  }
}

function setupVersionChecker() {
  document.getElementById('check-versions').addEventListener('click', () => {
    if (!versionChecked) checkVersions();
  });
}

function getFiltered() {
  return catalog.projects.filter(p => {
    const matchesFilter =
      activeFilter === 'All' ||
      (activeFilter === 'Active' && p.status === 'active-dev') ||
      (activeFilter === 'Shipped' && (p.status === 'shipped' || p.status === 'polished')) ||
      (activeFilter === 'Prototype' && p.status === 'prototype') ||
      (activeFilter === 'Pre-Production' && (p.status === 'pre-production' || p.status === 'concept')) ||
      (activeFilter === 'On Hold' && p.status === 'on-hold');

    const matchesSearch = !searchQuery ||
      p.name.toLowerCase().includes(searchQuery) ||
      p.genre.toLowerCase().includes(searchQuery) ||
      p.techStack.some(t => t.toLowerCase().includes(searchQuery));

    return matchesFilter && matchesSearch;
  });
}

function renderStats() {
  const el = document.getElementById('stats');
  const projects = catalog.projects;
  const active = projects.filter(p => p.status === 'active-dev').length;
  const shipped = projects.filter(p => p.status === 'shipped' || p.status === 'polished').length;
  const proto = projects.filter(p => p.status === 'prototype').length;
  const preProd = projects.filter(p => p.status === 'pre-production' || p.status === 'concept').length;
  const withMilestones = projects.filter(p => p.hasMilestones).length;

  el.innerHTML = `
    <span><span class="stat-value">${projects.length}</span> projects</span>
    <span><span class="stat-value">${active}</span> active</span>
    <span><span class="stat-value">${shipped}</span> shipped</span>
    <span><span class="stat-value">${proto}</span> prototype</span>
    <span><span class="stat-value">${preProd}</span> pre-prod</span>
    <span><span class="stat-value">${withMilestones}/${projects.length}</span> milestones</span>
  `;
}

function renderFilters() {
  const el = document.getElementById('filters');
  el.innerHTML = FILTERS.map(f =>
    `<button class="filter-btn${f === activeFilter ? ' active' : ''}" data-filter="${f}">${f}</button>`
  ).join('');

  el.addEventListener('click', e => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    activeFilter = btn.dataset.filter;
    el.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b.dataset.filter === activeFilter));
    renderGrid();
  });
}

function setupSearch() {
  document.getElementById('search').addEventListener('input', e => {
    searchQuery = e.target.value.toLowerCase().trim();
    renderGrid();
  });
}

function progressColor(completion) {
  if (completion >= 80) return 'green';
  if (completion >= 50) return 'cyan';
  if (completion >= 25) return 'yellow';
  return 'orange';
}

function renderGrid() {
  const el = document.getElementById('grid');
  const projects = getFiltered();

  if (projects.length === 0) {
    el.innerHTML = '<p style="color: var(--text-dim); grid-column: 1/-1; text-align: center; padding: 40px;">No projects match filters.</p>';
    return;
  }

  el.innerHTML = projects.map(p => {
    const cfg = STATUS_CONFIG[p.status] || STATUS_CONFIG['concept'];
    const completion = p.completion;
    const color = progressColor(completion || 0);

    let milestoneHtml = '';
    if (p.hasMilestones) {
      milestoneHtml = `<div class="milestone-info"><span class="icon">&#9632;</span> ${p.completedMilestones}/${p.totalMilestones} milestones</div>`;
    } else {
      milestoneHtml = `<div class="no-milestones">&#9888;&#65039; No milestone plan</div>`;
    }

    const progressHtml = completion != null
      ? `<div class="progress-bar"><div class="progress-fill ${color}" style="width:${completion}%"></div></div>`
      : '';

    const outdatedInfo = versionChecked ? countOutdated(p.slug) : { total: 0, critical: 0 };
    const outdatedBadge = outdatedInfo.total > 0
      ? `<span class="badge-outdated${outdatedInfo.critical > 0 ? ' badge-critical' : ''}">${outdatedInfo.total} outdated</span>`
      : '';

    const scanInfo = getScanInfoForProject(p.slug);
    const lastEditedHtml = scanInfo && scanInfo.lastModified
      ? `Edited ${timeAgo(scanInfo.lastModified)}`
      : '';
    const staleClass = (scanStale && scanData) ? ' card-stale' : '';
    const staleWarning = (scanStale && scanData)
      ? '<div class="stale-warning">This project may be out of date</div>'
      : '';

    return `
      <div class="card${staleClass}" data-slug="${p.slug}">
        <div class="card-header">
          <div class="card-name">${p.name}${outdatedBadge}</div>
          <span class="badge badge-${p.status}">${cfg.label}</span>
        </div>
        <div class="card-genre">${p.genre}</div>
        <div class="card-desc">${p.description}</div>
        ${progressHtml}
        ${milestoneHtml}
        <div class="card-meta">
          ${p.techStack.map(t => `<span class="tag">${t}</span>`).join('')}
          <span class="tag tag-platform">${p.platform}</span>
        </div>
        ${staleWarning}
        <div class="card-footer">
          <span>${completion != null ? completion + '% complete' : ''}</span>
          <span>${lastEditedHtml || `Reviewed ${p.lastReviewed}`}</span>
        </div>
      </div>
    `;
  }).join('');
}

function setupModal() {
  const modal = document.getElementById('modal');
  const body = document.getElementById('modal-body');

  document.getElementById('grid').addEventListener('click', e => {
    const card = e.target.closest('.card');
    if (!card) return;
    const slug = card.dataset.slug;
    const p = catalog.projects.find(pr => pr.slug === slug);
    if (!p) return;
    renderModal(p);
    modal.classList.remove('hidden');
  });

  modal.querySelector('.modal-backdrop').addEventListener('click', () => modal.classList.add('hidden'));
  modal.querySelector('.modal-close').addEventListener('click', () => modal.classList.add('hidden'));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') modal.classList.add('hidden'); });
}

function renderModal(p) {
  const cfg = STATUS_CONFIG[p.status] || STATUS_CONFIG['concept'];
  const body = document.getElementById('modal-body');

  let milestonesHtml = '';
  if (p.milestones && p.milestones.length > 0) {
    milestonesHtml = `
      <div class="modal-section">
        <div class="milestone-header">
          <h3>Milestones (${p.completedMilestones}/${p.totalMilestones})</h3>
          <button class="export-prompt-btn" data-slug="${p.slug}" data-type="progress">Export progress prompt</button>
        </div>
        <ul>
          ${p.milestones.map(m => {
            const pct = m.completion != null ? ` (${m.completion}%)` : '';
            return `<li><span class="milestone-dot ${m.status}"></span> ${m.name}${pct}</li>`;
          }).join('')}
        </ul>
      </div>
    `;
  } else {
    milestonesHtml = `
      <div class="modal-section">
        <div class="milestone-header">
          <h3>Milestones</h3>
          <button class="export-prompt-btn" data-slug="${p.slug}" data-type="progress">Export milestone prompt</button>
        </div>
        <p style="color: var(--yellow);">No milestone plan defined for this project.</p>
      </div>
    `;
  }

  body.innerHTML = `
    <div style="display:flex; gap:12px; align-items:center; margin-bottom:4px;">
      <div class="modal-title">${p.name}</div>
      <span class="badge badge-${p.status}">${cfg.label}</span>
    </div>
    <div class="modal-genre">${p.genre} &middot; ${p.platform}</div>

    <div class="modal-section">
      <h3>Description</h3>
      <p>${p.description}</p>
    </div>

    ${p.completion != null ? `
    <div class="modal-section">
      <h3>Progress</h3>
      <div class="progress-bar" style="height:8px; margin-bottom:6px;">
        <div class="progress-fill ${progressColor(p.completion)}" style="width:${p.completion}%"></div>
      </div>
      <p>${p.completion}% complete${p.currentMilestone ? ' &mdash; Current: ' + p.currentMilestone : ''}</p>
    </div>
    ` : ''}

    ${milestonesHtml}

    <div class="modal-section">
      <h3>Tech Stack</h3>
      <div class="modal-tags">
        ${p.techStack.map(t => `<span class="tag">${t}</span>`).join('')}
        <span class="tag tag-platform">${p.platform}</span>
      </div>
    </div>

    <div class="modal-section">
      <h3>Project Flags</h3>
      <div class="modal-flags">
        <span class="${p.hasGDD ? 'flag-yes' : 'flag-no'}">${p.hasGDD ? '&#10003;' : '&#10007;'} Game Design Document</span>
        <span class="${p.hasMilestones ? 'flag-yes' : 'flag-no'}">${p.hasMilestones ? '&#10003;' : '&#10007;'} Milestone Plan</span>
        <span class="${p.hasProductionStatus ? 'flag-yes' : 'flag-no'}">${p.hasProductionStatus ? '&#10003;' : '&#10007;'} Production Status</span>
        <span class="${p.runGameDeployed ? 'flag-yes' : 'flag-no'}">${p.runGameDeployed ? '&#10003;' : '&#10007;'} Live on run.game</span>
        <span class="${p.gitActive ? 'flag-yes' : 'flag-no'}">${p.gitActive ? '&#10003;' : '&#10007;'} Git Active</span>
      </div>
    </div>

    ${renderRunGameSection(p)}

    ${p.notes ? `
    <div class="modal-section">
      <h3>Notes</h3>
      <div class="modal-notes">${p.notes}</div>
    </div>
    ` : ''}

    ${renderVersionSection(p.slug)}

    <div class="modal-section" style="margin-bottom:0;">
      <h3>Location</h3>
      <p style="font-family: var(--font-mono); font-size: 0.8rem;">${p.path}</p>
    </div>
  `;
}

function renderRunGameSection(p) {
  const rg = p.runGame;
  if (!rg) return '';

  const statusColors = {
    'deployed': 'green',
    'ready': 'cyan',
    'needs-config': 'yellow',
    'not-started': 'orange',
    'not-applicable': 'gray',
  };
  const statusLabels = {
    'deployed': 'Live on run.game',
    'ready': 'Ready to Publish',
    'needs-config': 'Almost Ready',
    'not-started': 'Not Started',
    'not-applicable': 'Not Applicable',
  };

  const color = statusColors[rg.status] || 'gray';
  const label = statusLabels[rg.status] || rg.status;

  let sdkHtml = '';
  if (rg.sdk) {
    const sdkName = rg.sdk === '@series-inc/rundot-game-sdk'
      ? 'Rundot Game SDK (newest)'
      : rg.sdk === '@series-inc/venus-sdk'
        ? 'Venus SDK (run.game connector)'
        : rg.sdk;
    const versionNote = rg.sdkVersion === '*'
      ? '<span class="rg-version-warn">any version (wildcard)</span>'
      : `v${rg.sdkVersion}`;
    sdkHtml = `
      <div class="rg-detail">
        <span class="rg-detail-label">Connector Software:</span>
        <span>${sdkName} &mdash; ${versionNote}</span>
      </div>
    `;
  }

  let gameIdHtml = '';
  if (rg.gameId) {
    gameIdHtml = `
      <div class="rg-detail">
        <span class="rg-detail-label">Game ID:</span>
        <span class="rg-game-id">${rg.gameId}</span>
      </div>
    `;
  }

  let featuresHtml = '';
  if (rg.featuresUsed && rg.featuresUsed.length > 0) {
    featuresHtml = `
      <div class="rg-features">
        <div class="rg-feature-label">Features being used:</div>
        <ul class="rg-feature-list rg-feature-yes">
          ${rg.featuresUsed.map(f => `<li>&#10003; ${f}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  let missingHtml = '';
  if (rg.featuresMissing && rg.featuresMissing.length > 0) {
    missingHtml = `
      <div class="rg-features">
        <div class="rg-feature-label">Not set up yet:</div>
        <ul class="rg-feature-list rg-feature-no">
          ${rg.featuresMissing.map(f => `<li>&#10007; ${f}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  return `
    <div class="modal-section rg-section">
      <h3>run.game Status</h3>
      <div class="rg-status-row">
        <span class="rg-badge rg-badge-${color}">${label}</span>
        ${rg.readiness ? `<span class="rg-readiness">${rg.readiness}</span>` : ''}
      </div>
      ${rg.summary ? `<p class="rg-summary">${rg.summary}</p>` : ''}
      ${sdkHtml}
      ${gameIdHtml}
      ${featuresHtml}
      ${missingHtml}
    </div>
  `;
}

// ── Progress Prompt Export ───────────────────────────────────

function generateProgressPrompt(slug) {
  const p = catalog.projects.find(pr => pr.slug === slug);
  if (!p) return '';
  return p.hasMilestones ? generateMilestoneProgressPrompt(p) : generateCreateMilestonePrompt(p);
}

function generateMilestoneProgressPrompt(p) {
  let prompt = `I need help planning the next steps for my project "${p.name}".\n\n`;
  prompt += `## Project Overview\n`;
  prompt += `- **Genre:** ${p.genre}\n`;
  prompt += `- **Tech Stack:** ${p.techStack.join(', ')}\n`;
  prompt += `- **Platform:** ${p.platform}\n`;
  prompt += `- **Overall Completion:** ${p.completion != null ? p.completion + '%' : 'Unknown'}\n\n`;

  prompt += `## Milestone Status\n`;
  for (const m of p.milestones) {
    const icon = m.status === 'completed' ? '✅' : m.status === 'in-progress' ? '🔄' : '⬜';
    const pct = m.completion != null ? ` (${m.completion}%)` : '';
    prompt += `${icon} ${m.name}${pct}\n`;
  }
  prompt += `\n`;

  if (p.currentMilestone) {
    prompt += `**Current Focus:** ${p.currentMilestone}\n\n`;
  }

  if (p.notes) {
    prompt += `## Notes from Project Review\n${p.notes}\n\n`;
  }

  if (p.runGame && p.runGame.summary && p.runGame.status !== 'not-applicable') {
    prompt += `## run.game Platform Status\n${p.runGame.summary}\n\n`;
  }

  prompt += `## What I Need\n`;
  prompt += `Look at the current milestone progress above and help me create an efficient plan to move this project forward. Focus on what's most impactful — what should I work on next, and in what order?\n\n`;
  prompt += `**Before making a plan, please ASK ME QUESTIONS about:**\n`;
  prompt += `- What's actually working in the game right now vs what's broken\n`;
  prompt += `- How much time I can dedicate to this project\n`;
  prompt += `- Any blockers or challenges I'm facing\n`;
  prompt += `- What I consider "done" for the current milestone\n`;
  prompt += `- My priorities (polish vs new features vs fixing bugs)\n`;

  return prompt;
}

function generateCreateMilestonePrompt(p) {
  let prompt = `I need help creating a milestone plan (MILESTONES.md) for my project "${p.name}".\n\n`;
  prompt += `## Project Overview\n`;
  prompt += `- **Genre:** ${p.genre}\n`;
  prompt += `- **Tech Stack:** ${p.techStack.join(', ')}\n`;
  prompt += `- **Platform:** ${p.platform}\n`;
  prompt += `- **Overall Completion:** ${p.completion != null ? p.completion + '%' : 'Unknown'}\n`;
  prompt += `- **Status:** ${(STATUS_CONFIG[p.status] || {}).label || p.status}\n\n`;

  prompt += `## Description\n${p.description}\n\n`;

  if (p.notes) {
    prompt += `## Notes from Project Review\n${p.notes}\n\n`;
  }

  const flags = [];
  if (p.hasGDD) flags.push('Has a Game Design Document');
  if (p.hasProductionStatus) flags.push('Has a Production Status doc');
  if (p.gitActive) flags.push('Git is active');
  if (p.runGameDeployed) flags.push('Deployed on run.game');
  if (flags.length > 0) {
    prompt += `## What's Already Set Up\n${flags.map(f => '- ' + f).join('\n')}\n\n`;
  }

  if (p.runGame && p.runGame.summary && p.runGame.status !== 'not-applicable') {
    prompt += `## run.game Platform Status\n${p.runGame.summary}\n\n`;
  }

  prompt += `## What I Need\n`;
  prompt += `Create a MILESTONES.md file for this project. `;
  if (p.completion != null && p.completion > 0) {
    prompt += `The project is already ${p.completion}% complete, so the milestone plan should document what has already been accomplished (mark those milestones as complete) AND lay out the remaining work.\n\n`;
  } else {
    prompt += `This project is just getting started, so the milestones should cover the full journey from foundation to launch.\n\n`;
  }

  prompt += `**Before creating the milestone plan, please ASK ME QUESTIONS about:**\n`;
  prompt += `- What features are already working in the project\n`;
  prompt += `- What I consider the most important features still needed\n`;
  prompt += `- Whether I'm targeting a specific launch date or platform\n`;
  prompt += `- How I want to break up the work (small milestones vs big phases)\n`;
  prompt += `- Any features I've decided to cut or defer\n`;

  return prompt;
}

function renderVersionSection(slug) {
  if (!versionChecked) return '';
  const info = getProjectVersionInfo(slug);
  if (!info || info.length === 0) return '';

  const outdatedCount = info.filter(d => isOutdated(d.current, d.latest)).length;
  const criticalCount = info.filter(d => isCriticallyOutdated(d.current, d.latest)).length;
  const checkedCount = info.filter(d => d.latest).length;

  let summaryHtml = '';
  if (outdatedCount > 0) {
    const criticalNote = criticalCount > 0
      ? `<span class="critical-count">${criticalCount} critical</span>, `
      : '';
    summaryHtml = `${criticalNote}<span class="outdated-count">${outdatedCount}</span> outdated, <span class="uptodate-count">${checkedCount - outdatedCount}</span> up to date`;
  } else {
    summaryHtml = `<span class="uptodate-count">${checkedCount}</span> dependencies up to date`;
  }

  const rows = info.map(d => {
    const current = cleanVersion(d.current);
    const latest = d.latest || '—';
    const critical = isCriticallyOutdated(d.current, d.latest);
    const outdated = isOutdated(d.current, d.latest);
    const cls = critical ? 'ver-critical' : (outdated ? 'ver-outdated' : (d.latest ? 'ver-up-to-date' : ''));
    return `<tr class="${cls}">
      <td>${d.pkg}${critical ? ' <span class="ver-critical-tag">MAJOR</span>' : ''}</td>
      <td class="ver-current">${current}</td>
      <td class="ver-arrow">${d.latest ? '→' : ''}</td>
      <td class="ver-latest">${latest}</td>
    </tr>`;
  }).join('');

  const exportBtn = outdatedCount > 0
    ? `<button class="export-prompt-btn" data-slug="${slug}">Export update prompt</button>`
    : '';

  return `
    <div class="modal-section">
      <h3>Dependencies</h3>
      <div class="version-header">
        <div class="version-summary">${summaryHtml}</div>
        ${exportBtn}
      </div>
      <table class="version-table">
        <thead><tr><th>Package</th><th>Current</th><th></th><th>Latest</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function generateUpdatePrompt(slug) {
  const info = getProjectVersionInfo(slug);
  if (!info) return '';
  const project = catalog.projects.find(p => p.slug === slug);
  const projectName = project ? project.name : slug;

  const outdated = info.filter(d => isOutdated(d.current, d.latest));
  if (outdated.length === 0) return '';

  const critical = outdated.filter(d => isCriticallyOutdated(d.current, d.latest));
  const minor = outdated.filter(d => !isCriticallyOutdated(d.current, d.latest));

  let prompt = `Update the outdated dependencies in this project (${projectName}).\n\n`;

  if (critical.length > 0) {
    prompt += `CRITICAL — Major version behind (these may have breaking changes, test carefully):\n`;
    for (const d of critical) {
      prompt += `- ${d.pkg}: currently ${cleanVersion(d.current)} → latest is ${d.latest}\n`;
    }
    prompt += '\n';
  }

  if (minor.length > 0) {
    prompt += `Minor/patch updates:\n`;
    for (const d of minor) {
      prompt += `- ${d.pkg}: currently ${cleanVersion(d.current)} → latest is ${d.latest}\n`;
    }
    prompt += '\n';
  }

  prompt += `Steps:\n`;
  prompt += `1. Update each package to the latest version in package.json\n`;
  prompt += `2. Run npm install to apply changes\n`;
  prompt += `3. Build the project and fix any breaking changes\n`;
  prompt += `4. Test that the game still runs correctly\n`;

  return prompt;
}

function setupExportPrompt() {
  document.getElementById('modal-body').addEventListener('click', e => {
    const btn = e.target.closest('.export-prompt-btn');
    if (!btn) return;
    const slug = btn.dataset.slug;
    const type = btn.dataset.type;
    const prompt = type === 'progress' ? generateProgressPrompt(slug) : generateUpdatePrompt(slug);
    const originalText = btn.textContent;
    navigator.clipboard.writeText(prompt).then(() => {
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('copied');
      }, 2000);
    }).catch(() => {
      const ta = document.createElement('textarea');
      ta.value = prompt;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = originalText;
        btn.classList.remove('copied');
      }, 2000);
    });
  });
}

// ── Live Analyze ────────────────────────────────────────────

function setupAnalyze() {
  document.getElementById('analyze-projects').addEventListener('click', () => {
    if (!scanChecked || scanStale) runAnalysis();
  });
}

async function runAnalysis() {
  const btn = document.getElementById('analyze-projects');
  btn.textContent = 'Scanning...';
  btn.classList.add('loading');
  scanChecked = true;

  try {
    const res = await fetch('/api/scan');
    if (!res.ok) throw new Error('Scan failed — make sure server.py is running (not python3 -m http.server)');
    scanData = await res.json();

    btn.classList.remove('loading');
    const { inSync, outOfSync, new: newCount } = scanData.summary;
    if (outOfSync > 0 || newCount > 0) {
      btn.textContent = `${outOfSync + newCount} Out of Sync`;
      btn.classList.add('has-outdated');
    } else {
      btn.textContent = 'All In Sync';
      btn.classList.add('done');
    }

    saveScanCache(scanData);
    scanStale = false;
    renderGrid();

    showScanResults(scanData);

    // Refresh version data since the scan regenerated versions.json
    versionChecked = false;
    checkVersions();
  } catch (err) {
    btn.classList.remove('loading');
    btn.textContent = 'Scan Error';
    btn.title = err.message;
    btn.classList.add('has-outdated');
    scanChecked = false;
    console.error('Scan failed:', err);
  }
}

function showScanResults(data) {
  const existing = document.querySelector('.scan-overlay');
  if (existing) existing.remove();

  const { inSync, outOfSync, new: newCount } = data.summary;
  const changed = data.report.filter(r => r.diffs.length > 0);

  let itemsHtml = '';
  if (changed.length === 0) {
    itemsHtml = '<p class="scan-all-good">Everything matches the catalog. No changes detected.</p>';
  } else {
    itemsHtml = changed.map(r => {
      const tag = r.isNew
        ? '<span class="scan-tag scan-tag-new">NEW</span>'
        : '<span class="scan-tag scan-tag-changed">CHANGED</span>';
      const diffs = r.diffs.map(d => `<div class="scan-diff-line">${d}</div>`).join('');
      return `<div class="scan-diff-item">${tag}<strong>${r.name}</strong>${diffs}</div>`;
    }).join('');
  }

  // Missing milestone plans section
  const missingMilestones = data.report.filter(r => !r.scanned.hasMilestones);
  let milestonesWarningHtml = '';
  if (missingMilestones.length > 0) {
    const names = missingMilestones.map(r => `<li>${r.name}</li>`).join('');
    milestonesWarningHtml = `
      <div class="scan-missing-milestones">
        <h3>&#9888; Missing Milestone Plans (${missingMilestones.length})</h3>
        <p>These projects have no MILESTONES.md file. Milestone plans are critical for tracking progress.</p>
        <ul>${names}</ul>
      </div>
    `;
  }

  const overlay = document.createElement('div');
  overlay.className = 'scan-overlay';
  overlay.innerHTML = `
    <div class="scan-overlay-backdrop"></div>
    <div class="scan-overlay-content">
      <h2 class="scan-title">Project Scan Results</h2>
      <div class="scan-summary">
        <span class="scan-count scan-count-sync">${inSync} in sync</span>
        <span class="scan-count scan-count-changed">${outOfSync} out of sync</span>
        <span class="scan-count scan-count-new">${newCount} new</span>
      </div>
      <div class="scan-items">${itemsHtml}</div>
      ${milestonesWarningHtml}
      <button class="scan-dismiss-btn">Dismiss</button>
    </div>
  `;

  document.body.appendChild(overlay);
  overlay.querySelector('.scan-overlay-backdrop').addEventListener('click', () => overlay.remove());
  overlay.querySelector('.scan-dismiss-btn').addEventListener('click', () => overlay.remove());
}

init();
