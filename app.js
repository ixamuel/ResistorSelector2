// lookups and resistors are set by initApp(DATA) called from data.js loader
let lookups, resistors;

const MIN_RES = 0.0001;
const MAX_RES = 100000000;
const LOG_MIN = Math.log10(MIN_RES);
const LOG_MAX = Math.log10(MAX_RES);

// state is initialized in initApp() once lookups is available
let state;

let filtered = [];
let displayedCount = 100;
const INCREMENT = 100;

function initApp(data) {
    lookups = data.lookups;
    resistors = data.resistors;

    // Initialize state now that lookups is available
    state = {
        resMin: 0,
        resMax: MAX_RES,
        targetRes: null,
        products: new Set(),
        status: new Set([lookups.status.indexOf('Active')]),
        tolerance: new Set(),
        power: new Set(),
        tcr: new Set(),
        size: new Set(),
        series: "",
        search: "",
        isDecimal: true,
        sort: { key: null, dir: null },
        selectedPns: [],
        activeValues: null
    };

    setupTags('products', 'tags-products');
    setupTags('status', 'tags-status');
    setupTags('tolerance', 'tags-tolerance');
    setupTags('power', 'tags-power');
    setupTags('tcr', 'tags-tcr');
    setupTags('size', 'tags-size');

    // Series setup
    const seriesSel = document.getElementById('seriesSelect');
    refresh(); // Refresh will call updateAvailability

    // Listeners
    document.getElementById('resSliderMin').oninput = onRangeInput;
    document.getElementById('resSliderMax').oninput = onRangeInput;
    document.getElementById('resMin').onchange = onManualInput;
    document.getElementById('resMax').onchange = onManualInput;
    document.getElementById('pnSearch').oninput = (e) => { state.search = e.target.value.trim().toLowerCase(); refresh(); };
    document.getElementById('seriesSelect').onchange = (e) => { state.series = e.target.value; refresh(); };
    document.getElementById('decimalToggle').onclick = toggleDecimal;
    document.getElementById('resetBtn').onclick = resetFilters;

    document.querySelectorAll('thead th[data-sort]').forEach(th => {
        th.onclick = () => onSort(th.dataset.sort);
    });

    document.getElementById('sidebarToggle').onclick = toggleSidebar;

    document.querySelectorAll('.section-header').forEach(h => {
        h.onclick = () => h.parentElement.classList.toggle('section-collapsed');
    });

    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting && displayedCount < filtered.length) {
            displayedCount += INCREMENT;
            render();
        }
    });
    observer.observe(document.getElementById('sentinel'));

    document.getElementById('loader').style.display = 'none';

    // Ensure Active is highlighted on init
    const activeIdx = lookups.status.indexOf('Active');
    if (activeIdx !== -1) {
        document.getElementById('tags-status').children[activeIdx].classList.add('active');
    }
}

function createTagBtn(key, idx) {
    const val = lookups[key][idx];
    const btn = document.createElement('button');
    btn.className = 'tag-btn';
    if (key === 'products') {
        const prodClasses = ['prod-as', 'prod-cs', 'prod-gp', 'prod-hp', 'prod-ht', 'prod-sp'];
        if (prodClasses[idx]) btn.classList.add(prodClasses[idx]);
    }
    btn.innerHTML = `<span>${val || 'N/A'}</span> <span class="count-chip" id="count-${key}-${idx}">0</span>`;
    btn.onclick = () => {
        if (btn.classList.contains('unavailable')) return;
        if (state[key].has(idx)) {
            state[key].delete(idx);
            btn.classList.remove('active');
        } else {
            state[key].add(idx);
            btn.classList.add('active');
        }
        refresh();
    };
    return btn;
}

function setupTags(key, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    let indices = lookups[key].map((_, i) => i);

    if (key === 'tcr') {
        const ranges = indices.filter(i => lookups[key][i].includes(' to '));
        const singles = indices.filter(i => !lookups[key][i].includes(' to '));

        ranges.sort((a, b) => lookups[key][a].localeCompare(lookups[key][b]));
        singles.sort((a, b) => {
            const valA = parseFloat(lookups[key][a].replace(/[^\d.-]/g, '')) || 0;
            const valB = parseFloat(lookups[key][b].replace(/[^\d.-]/g, '')) || 0;
            return Math.abs(valA) - Math.abs(valB);
        });

        if (ranges.length > 0) {
            const rangeDiv = document.createElement('div');
            rangeDiv.className = 'tag-group';
            rangeDiv.style.marginBottom = '8px';
            ranges.forEach(idx => rangeDiv.appendChild(createTagBtn(key, idx)));
            container.appendChild(rangeDiv);
        }

        if (singles.length > 0) {
            const gridDiv = document.createElement('div');
            gridDiv.className = 'tag-grid';
            singles.forEach(idx => gridDiv.appendChild(createTagBtn(key, idx)));
            container.appendChild(gridDiv);
        }
    } else {
        indices.forEach((idx) => {
            container.appendChild(createTagBtn(key, idx));
        });
    }
}

function parseVal(s) {
    if (!s) return null;
    // Clean string: remove commas, Ω, ohm, and trim
    s = s.toString().replace(/,/g, '').replace(/Ω|ohm/gi, '').trim();
    if (!s) return null;

    let mult = 1;
    const lowS = s.toLowerCase();

    if (lowS.endsWith('k')) { mult = 1000; s = s.slice(0, -1); }
    else if (s.endsWith('M')) { mult = 1000000; s = s.slice(0, -1); }
    else if (lowS.endsWith('m')) { mult = 0.001; s = s.slice(0, -1); }
    else if (lowS.endsWith('mo') || lowS.endsWith('mohm')) {
        mult = 0.001;
        s = s.replace(/m[oO]([hH][mM])?$/i, '');
    }

    const v = parseFloat(s);
    return isNaN(v) ? null : v * mult;
}

function formatRes(v) {
    if (v === 0) return "0 Ω";
    if (state.isDecimal) {
        if (v < 1) return v.toFixed(3).replace(/\.?0+$/, '') + " Ω";
        if (v < 10) return v.toFixed(2).replace(/\.?0+$/, '') + " Ω";
        return v.toLocaleString() + " Ω";
    } else {
        if (v >= 1000000) return (v / 1000000).toFixed(2).replace(/\.00$/, '').replace(/\.0$/, '') + " MΩ";
        if (v >= 1000) return (v / 1000).toFixed(2).replace(/\.00$/, '').replace(/\.0$/, '') + " kΩ";
        if (v < 1) return (v * 1000).toFixed(1).replace(/\.0$/, '') + " mΩ";
        return v.toFixed(2).replace(/\.00$/, '').replace(/\.0$/, '') + " Ω";
    }
}

function onRangeInput() {
    let low = parseInt(document.getElementById('resSliderMin').value);
    let high = parseInt(document.getElementById('resSliderMax').value);
    if (low > high) [low, high] = [high, low];

    state.resMin = Math.pow(10, LOG_MIN + (LOG_MAX - LOG_MIN) * (low / 100));
    state.resMax = Math.pow(10, LOG_MIN + (LOG_MAX - LOG_MIN) * (high / 100));
    state.targetRes = null;

    document.getElementById('resMin').value = formatRes(state.resMin);
    document.getElementById('resMax').value = formatRes(state.resMax);

    updateTrack(low, high);
    refresh();
}

function onManualInput() {
    const minStr = document.getElementById('resMin').value;
    const maxStr = document.getElementById('resMax').value;

    const minVal = parseVal(minStr);
    const maxVal = parseVal(maxStr);

    state.resMin = minVal !== null ? minVal : 0;
    state.resMax = maxVal !== null ? maxVal : MAX_RES;

    const isSingle = (minStr && !maxStr) || (!minStr && maxStr) || (minStr === maxStr && minStr !== "");
    state.targetRes = isSingle ? (minVal || maxVal) : null;

    const l = Math.max(0, Math.min(100, (Math.log10(Math.max(MIN_RES, state.resMin)) - LOG_MIN) / (LOG_MAX - LOG_MIN) * 100));
    const h = Math.max(0, Math.min(100, (Math.log10(Math.max(MIN_RES, state.resMax)) - LOG_MIN) / (LOG_MAX - LOG_MIN) * 100));

    document.getElementById('resSliderMin').value = l;
    document.getElementById('resSliderMax').value = h;

    updateTrack(l, h);
    refresh();
}

function updateTrack(l, h) {
    document.getElementById('resTrack').style.background = `linear-gradient(to right, #e2e8f0 ${l}%, var(--primary) ${l}%, var(--primary) ${h}%, #e2e8f0 ${h}%)`;
}

function toggleDecimal() {
    state.isDecimal = !state.isDecimal;
    document.getElementById('decimalToggle').classList.toggle('active');
    document.getElementById('resMin').value = state.resMin > 0 ? formatRes(state.resMin) : "";
    document.getElementById('resMax').value = state.resMax < MAX_RES ? formatRes(state.resMax) : "";
    render();
}

function onSort(key) {
    if (state.sort.key === key) {
        if (state.sort.dir === 'desc') state.sort.dir = 'asc';
        else if (state.sort.dir === 'asc') { state.sort.dir = null; state.sort.key = null; }
        else state.sort.dir = 'desc';
    } else {
        state.sort.key = key;
        state.sort.dir = 'desc';
    }

    document.querySelectorAll('thead th').forEach(th => {
        th.classList.remove('sort-active', 'sort-asc', 'sort-desc');
        if (th.dataset.sort === state.sort.key && state.sort.dir) {
            th.classList.add('sort-active', `sort-${state.sort.dir}`);
        }
    });

    if (state.sort.key) applySort();
    else refresh(); // Restore original filter order
}

function applySort() {
    const k = state.sort.key;
    const d = state.sort.dir === 'asc' ? 1 : -1;
    filtered.sort((a, b) => {
        let va = a[k], vb = b[k];
        if (k === 'rv') return (va - vb) * d;
        if (typeof va === 'number') return (va - vb) * d;
        return va.toString().localeCompare(vb.toString()) * d;
    });
    render();
}

function refresh() {
    const minRaw = document.getElementById('resMin').value;
    const maxRaw = document.getElementById('resMax').value;
    const isSingle = (minRaw && !maxRaw) || (!minRaw && maxRaw) || (minRaw === maxRaw && minRaw !== "");
    const singleVal = isSingle ? (parseVal(minRaw) || parseVal(maxRaw)) : null;
    state.targetRes = singleVal;

    const noteEl = document.getElementById('selection-note');
    noteEl.style.display = 'none';

    // Base Context (respecting all filters except resistance)
    let baseFiltered = resistors.filter(r => {
        if (state.products.size && !state.products.has(r.p)) return false;
        if (state.status.size && !state.status.has(r.s)) return false;
        if (state.tolerance.size && !state.tolerance.has(r.rt)) return false;
        if (state.power.size && !state.power.has(r.pr)) return false;
        if (state.tcr.size && !state.tcr.has(r.tc)) return false;
        if (state.size.size && !state.size.has(r.sz)) return false;
        if (state.series && r.se != state.series) return false;
        if (state.search && !r.pn.toLowerCase().includes(state.search)) return false;
        return true;
    });

    if (isSingle && singleVal !== null) {
        filtered = baseFiltered.filter(r => r.rv === singleVal);
        state.activeValues = filtered.length > 0 ? [singleVal] : null;

        if (filtered.length === 0) {
            const uniqueRVs = Array.from(new Set(baseFiltered.map(r => r.rv))).sort((a, b) => a - b);
            if (uniqueRVs.length > 0) {
                let idx = uniqueRVs.findIndex(v => v > singleVal);
                let neighbors = [];
                if (idx === -1) neighbors = [uniqueRVs[uniqueRVs.length - 1]];
                else if (idx === 0) neighbors = [uniqueRVs[0]];
                else neighbors = [uniqueRVs[idx - 1], uniqueRVs[idx]];

                filtered = baseFiltered.filter(r => neighbors.includes(r.rv));
                state.activeValues = neighbors;
                noteEl.textContent = `No exact match for ${formatRes(singleVal)}. Showing closest values: ${neighbors.map(formatRes).join(' and ')}`;
                noteEl.style.display = 'block';
            }
        }
    } else {
        filtered = baseFiltered.filter(r => r.rv >= state.resMin && r.rv <= state.resMax);
        state.activeValues = null; // Default range behavior
    }

    displayedCount = INCREMENT;
    document.getElementById('counter').textContent = `${filtered.length.toLocaleString()} Components Matched`;

    updateAvailability();
    if (state.sort.key) applySort();
    else render();
}

function updateAvailability() {
    const groups = ['products', 'status', 'tolerance', 'power', 'tcr', 'size'];
    const groupStats = {};
    groups.forEach(g => groupStats[g] = {});
    const seriesCounts = {};

    resistors.forEach(r => {
        let resM = false;
        if (state.activeValues !== null) {
            resM = state.activeValues.includes(r.rv);
        } else {
            resM = (r.rv >= state.resMin && r.rv <= state.resMax);
        }
        const prM = !state.products.size || state.products.has(r.p);
        const stM = !state.status.size || state.status.has(r.s);
        const tlM = !state.tolerance.size || state.tolerance.has(r.rt);
        const pwM = !state.power.size || state.power.has(r.pr);
        const tcM = !state.tcr.size || state.tcr.has(r.tc);
        const szM = !state.size.size || state.size.has(r.sz);
        const seM = !state.series || r.se == state.series;
        const shM = !state.search || r.pn.toLowerCase().includes(state.search);

        const allMatched = resM && prM && stM && tlM && pwM && tcM && szM && seM && shM;

        if (allMatched) {
            groups.forEach(g => groupStats[g][r[getShort(g)]] = (groupStats[g][r[getShort(g)]] || 0) + 1);
            seriesCounts[r.se] = (seriesCounts[r.se] || 0) + 1;
        } else {
            const checkOthers = (grpKey) => {
                if (grpKey !== 'res' && !resM) return false;
                if (grpKey !== 'products' && !prM) return false;
                if (grpKey !== 'status' && !stM) return false;
                if (grpKey !== 'tolerance' && !tlM) return false;
                if (grpKey !== 'power' && !pwM) return false;
                if (grpKey !== 'tcr' && !tcM) return false;
                if (grpKey !== 'size' && !szM) return false;
                if (grpKey !== 'series' && !seM) return false;
                if (grpKey !== 'search' && !shM) return false;
                return true;
            };

            groups.forEach(g => { if (checkOthers(g)) groupStats[g][r[getShort(g)]] = (groupStats[g][r[getShort(g)]] || 0) + 1; });
            if (checkOthers('series')) seriesCounts[r.se] = (seriesCounts[r.se] || 0) + 1;
        }
    });

    groups.forEach(g => {
        lookups[g].forEach((_, idx) => {
            const count = groupStats[g][idx] || 0;
            const el = document.getElementById(`count-${g}-${idx}`);
            if (el) {
                el.textContent = count.toLocaleString();
                el.parentElement.classList.toggle('unavailable', count === 0);
            }
        });
    });

    const seriesSel = document.getElementById('seriesSelect');
    const currentVal = state.series;
    seriesSel.innerHTML = '<option value="">All Series (' + resistors.length.toLocaleString() + ')</option>';
    lookups.series.forEach((s, i) => {
        const count = seriesCounts[i] || 0;
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = `${s} (${count.toLocaleString()})`;
        if (count === 0) opt.disabled = true;
        if (i == currentVal) opt.selected = true;
        seriesSel.appendChild(opt);
    });
}

function getShort(g) { return { products: 'p', status: 's', tolerance: 'rt', power: 'pr', tcr: 'tc', size: 'sz' }[g]; }

function getDeltaTag(v, target) {
    if (!target || v === target) return '';
    const diff = (v - target) / target;
    const absDiff = Math.abs(diff);
    const percent = (diff * 100).toFixed(1);
    const sign = diff > 0 ? '+' : '';

    let cls = 'delta-red';
    if (absDiff < 0.02) cls = 'delta-green';
    else if (absDiff < 0.05) cls = 'delta-yellow';

    return `<span class="delta-tag ${cls}">${sign}${percent}%</span>`;
}

function render() {
    const table = document.getElementById('resTable');
    const slice = filtered.slice(0, displayedCount);

    table.innerHTML = slice.map(r => {
        const status = lookups.status[r.s];
        const deltaTag = getDeltaTag(r.rv, state.targetRes);
        const isSelected = state.selectedPns.includes(r.pn);
        return `
                <tr class="${status === 'NRFND' ? 'nrfnd' : ''}">
                    <td class="checkbox-cell" onclick="toggleSelect('${r.pn}')">
                        <div class="custom-checkbox ${isSelected ? 'checked' : ''}"></div>
                    </td>
                    <td>
                        <div class="pn-container">
                            <span class="part-number" onclick="window.open('https://octopart.com/search?q='+encodeURIComponent('${r.pn}'), '_blank')">${r.pn}</span>
                            <div class="btn-copy-pn" onclick="copyToClipboard('${r.pn}', this)" title="Copy Part Number">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                            </div>
                        </div>
                    </td>
                    <td class="res-cell">
                        <div class="res-container">
                            <span class="res-value">${formatRes(r.rv)}</span>
                            ${deltaTag}
                        </div>
                    </td>
                    <td>${lookups.power[r.pr]}W</td>
                    <td>${lookups.tolerance[r.rt]}%</td>
                    <td>${lookups.tcr[r.tc]}</td>
                    <td>${lookups.size[r.sz]}</td>
                    <td class="series-cell">${lookups.series[r.se]}</td>
                    <td><span class="tag-status ${status === 'Active' ? 'status-active' : 'status-nrnd'}">${status}</span></td>
                    <td><span class="tag-packaging">${lookups.packaging[r.pk]}</span></td>
                </tr>
            `;
    }).join('');

    document.getElementById('sentinel').textContent = displayedCount >= filtered.length ? "End of Results" : "Scroll for More Results";
}

function toggleSelect(pn) {
    const idx = state.selectedPns.indexOf(pn);
    if (idx === -1) {
        state.selectedPns.push(pn);
    } else {
        state.selectedPns.splice(idx, 1);
    }
    updateSelectionUI();
    render();
}

function updateSelectionUI() {
    const pill = document.getElementById('selection-pill');
    const actions = document.getElementById('action-pill');

    if (state.selectedPns.length > 0) {
        pill.innerHTML = state.selectedPns.map(pn => `
                <div class="part-pill">
                    <span>${pn}</span>
                    <div class="btn-remove" onclick="toggleSelect('${pn}')">✕</div>
                </div>
            `).join('');
        pill.classList.add('active');
        actions.classList.add('active');
    } else {
        pill.classList.remove('active');
        actions.classList.remove('active');
    }
}

function clearSelection() {
    state.selectedPns = [];
    updateSelectionUI();
    render();
}

function comparePNs() {
    if (state.selectedPns.length === 0) return;
    state.search = "";
    document.getElementById('pnSearch').value = "";
    // Just filter to show ONLY selected PNs
    state.resMin = 0;
    state.resMax = MAX_RES;
    state.targetRes = null;

    filtered = resistors.filter(r => state.selectedPns.includes(r.pn));
    displayedCount = filtered.length;
    render();
    document.getElementById('counter').textContent = `Comparing ${filtered.length} Selected Components`;
}

function exportTable() {
    if (state.selectedPns.length === 0) return;

    const selectedResistors = resistors.filter(r => state.selectedPns.includes(r.pn));
    selectedResistors.sort((a, b) => state.selectedPns.indexOf(a.pn) - state.selectedPns.indexOf(b.pn));

    let tableRows = selectedResistors.map(r => `
            <tr>
                <td>${r.pn}</td>
                <td>${formatRes(r.rv)}</td>
                <td>${lookups.power[r.pr]}W</td>
                <td>${lookups.tolerance[r.rt]}%</td>
                <td>${lookups.tcr[r.tc]}</td>
                <td>${lookups.size[r.sz]}</td>
                <td>${lookups.series[r.se]}</td>
                <td>${lookups.status[r.s]}</td>
                <td>${lookups.packaging[r.pk]}</td>
            </tr>
        `).join('');

    let md = "| Part Number | Resistance | Power | Tol | TCR | Size | Series | Status | Packaging |\\n";
    md += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\\n";
    selectedResistors.forEach(r => {
        md += `| ${r.pn} | ${formatRes(r.rv)} | ${lookups.power[r.pr]}W | ${lookups.tolerance[r.rt]}% | ${lookups.tcr[r.tc]} | ${lookups.size[r.sz]} | ${lookups.series[r.se]} | ${lookups.status[r.s]} | ${lookups.packaging[r.pk]} |\n`;
    });

    const newWin = window.open("", "_blank");
    newWin.document.write(`
            <html>
            <head>
                <title>Exported Resistor Table</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; background: #f8fafc; color: #1e293b; }
                    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
                    h2 { margin-top: 0; color: #4f46e5; }
                    .hint { font-size: 14px; color: #64748b; margin-bottom: 24px; }
                    
                    /* Table styling for Word/Outlook friendly copy */
                    table { width: 100%; border-collapse: collapse; margin-bottom: 32px; border: 1px solid #e2e8f0; }
                    th { background: #f1f5f9; text-align: left; padding: 12px; font-size: 12px; text-transform: uppercase; color: #475569; border: 1px solid #e2e8f0; }
                    td { padding: 12px; font-size: 13px; border: 1px solid #e2e8f0; color: #334155; }
                    tr:nth-child(even) { background: #f8fafc; }

                    .actions { display: flex; gap: 12px; margin-bottom: 24px; }
                    .btn { padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer; font-weight: 700; font-size: 13px; transition: all 0.2s; }
                    .btn-copy { background: #4f46e5; color: white; }
                    .btn-copy:hover { background: #4338ca; }
                    .btn-md { background: #e2e8f0; color: #475569; }
                    
                    pre { background: #f1f5f9; padding: 16px; border-radius: 8px; font-size: 12px; white-space: pre-wrap; display: none; border: 1px solid #e2e8f0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Exported Components</h2>
                    <p class="hint">The table below is formatted for easy copy-pasting into <b>Word, Outlook, or Excel</b>. Use the button below to select and copy everything.</p>
                    
                    <div class="actions">
                        <button class="btn btn-copy" onclick="copyTable()">Copy Table for Word/Outlook</button>
                        <button class="btn btn-md" onclick="toggleMarkdown()">Show Markdown</button>
                    </div>

                    <div id="table-wrapper">
                        <table id="res-table">
                            <thead>
                                <tr>
                                    <th>Part Number</th>
                                    <th>Resistance</th>
                                    <th>Power</th>
                                    <th>Tol</th>
                                    <th>TCR</th>
                                    <th>Size</th>
                                    <th>Series</th>
                                    <th>Status</th>
                                    <th>Packaging</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>

                    <pre id="md-content">${md}</pre>
                </div>

                <script>
                    function copyTable() {
                        const range = document.createRange();
                        range.selectNode(document.getElementById('res-table'));
                        window.getSelection().removeAllRanges();
                        window.getSelection().addRange(range);
                        document.execCommand('copy');
                        window.getSelection().removeAllRanges();
                        
                        const btn = document.querySelector('.btn-copy');
                        const original = btn.textContent;
                        btn.textContent = 'Copied!';
                        btn.style.background = '#10b981';
                        setTimeout(() => {
                            btn.textContent = original;
                            btn.style.background = '#4f46e5';
                        }, 2000);
                    }

                    function toggleMarkdown() {
                        const pre = document.getElementById('md-content');
                        const btn = document.querySelector('.btn-md');
                        if (pre.style.display === 'block') {
                            pre.style.display = 'none';
                            btn.textContent = 'Show Markdown';
                        } else {
                            pre.style.display = 'block';
                            btn.textContent = 'Hide Markdown';
                        }
                    }
                <\/script>
            </body>
            </html>
        `);
    newWin.document.close();
}

function copyToClipboard(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        if (btn) {
            btn.classList.add('copied');
            const original = btn.innerHTML;
            btn.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                `;
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = original;
            }, 1500);
        }
    });
}

function openOctopart() {
    state.selectedPns.forEach(pn => {
        window.open(`https://octopart.com/search?q=${encodeURIComponent(pn)}`, '_blank');
    });
}

function openMouser() {
    state.selectedPns.forEach(pn => {
        const url = `https://www.mouser.de/c/?q=${encodeURIComponent(pn)}&m=Panasonic&NewSearch=1`;
        window.open(url, '_blank');
    });
}

function openFarnell() {
    state.selectedPns.forEach(pn => {
        const url = `https://de.farnell.com/search?brand=panasonic&st=${encodeURIComponent(pn)}`;
        window.open(url, '_blank');
    });
}

function openDatasheet() {
    const uniqueLinks = new Set();
    state.selectedPns.forEach(pn => {
        const r = resistors.find(res => res.pn === pn);
        if (r && r.de !== undefined) {
            const link = lookups.datasheet[r.de];
            if (link && link !== "nan" && link !== "") {
                uniqueLinks.add(link);
            }
        }
    });
    uniqueLinks.forEach(link => window.open(link, '_blank'));
}

function resetFilters() {
    state = {
        resMin: 0, resMax: MAX_RES, targetRes: null,
        products: new Set(), status: new Set([lookups.status.indexOf('Active')]),
        tolerance: new Set(), power: new Set(), tcr: new Set(), size: new Set(),
        series: "", search: "",
        isDecimal: state.isDecimal, sort: { key: null, dir: null },
        selectedPns: state.selectedPns,
        activeValues: null
    };
    document.querySelectorAll('.tag-btn').forEach(b => b.classList.remove('active'));
    const activeIdx = lookups.status.indexOf('Active');
    if (activeIdx !== -1) document.getElementById('tags-status').children[activeIdx].classList.add('active');
    document.getElementById('resSliderMin').value = 0;
    document.getElementById('resSliderMax').value = 100;
    document.getElementById('resMin').value = "";
    document.getElementById('resMax').value = "";
    document.getElementById('pnSearch').value = "";
    document.getElementById('seriesSelect').value = "";
    updateTrack(0, 100);
    refresh();
}
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('collapsed');
}

// initApp is called from data.js after the gzip data is fetched and decompressed
