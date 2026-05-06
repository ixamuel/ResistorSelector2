import json
import os

def generate_modular_files(json_path, output_dir="."):
    """
    Generates the modular files (index.html, data.js) from the resistor data.
    Assumes styles.css and app.js already exist or are managed separately.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Generate data.js
    data_js_path = os.path.join(output_dir, 'data.js')
    with open(data_js_path, 'w', encoding='utf-8') as f:
        f.write(f"const DATA = {json.dumps(data, indent=None)};\n")
    print(f"Generated {data_js_path}")

    # 2. Generate index.html
    # We use a template-like approach for the main HTML structure
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResistorSelector v2.1</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

<div id="loader">
    <div class="spinner"></div>
    <div style="font-weight: 700; color: var(--primary)">Optimizing Selector Engine...</div>
</div>

<aside class="sidebar">
    <div class="sidebar-scroll">
        <div class="filter-section">
            <div class="section-header">Resistance <span class="arrow">▼</span></div>
            <div class="section-content">
                <div class="filter-item">
                    <div class="toggle-wrap">
                        <span style="font-size: 0.75rem; font-weight: 700;">Decimal Unit (0.01Ω)</span>
                        <div class="toggle-switch" id="decimalToggle">
                            <div class="toggle-knob"></div>
                        </div>
                    </div>
                    
                    <label>Resistance Range / Search</label>
                    <div class="range-inputs">
                        <input type="text" id="resMin" placeholder="Min (1k)">
                        <input type="text" id="resMax" placeholder="Max (10M)">
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <div class="range-container">
                            <div class="dual-range">
                                <div class="slider-track" id="resTrack"></div>
                                <input type="range" id="resSliderMin" min="0" max="100" value="0">
                                <input type="range" id="resSliderMax" min="0" max="100" value="100">
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.6rem; color: #94a3b8; font-weight: 700;">
                            <span>1mΩ</span>
                            <span>1Ω</span>
                            <span>1kΩ</span>
                            <span>10MΩ</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="filter-section">
            <div class="section-header">Electrical Specs <span class="arrow">▼</span></div>
            <div class="section-content">
                <div class="filter-item">
                    <label>Tolerance (%)</label>
                    <div id="tags-tolerance" class="tag-grid"></div>
                </div>
                <div class="filter-item">
                    <label>Power Rating (W)</label>
                    <div id="tags-power" class="tag-grid"></div>
                </div>
                <div class="filter-item">
                    <label>T.C.R (ppm/K)</label>
                    <div id="tags-tcr"></div>
                </div>
            </div>
        </div>

        <div class="filter-section">
            <div class="section-header">Category & Status <span class="arrow">▼</span></div>
            <div class="section-content">
                <div class="filter-item">
                    <label>Products</label>
                    <div id="tags-products" class="tag-group"></div>
                </div>
                <div class="filter-item">
                    <label>Status</label>
                    <div id="tags-status" class="tag-group"></div>
                </div>
            </div>
        </div>

        <div class="filter-section">
            <div class="section-header">Series & Size <span class="arrow">▼</span></div>
            <div class="section-content">
                <div class="filter-item">
                    <label>Select Series</label>
                    <select id="seriesSelect" class="input-pill" style="width:100%; border-radius: 8px; font-weight: 700;"></select>
                </div>
                <div class="filter-item">
                    <label>Size (Inch/Metric)</label>
                    <div id="tags-size" class="tag-group"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="sidebar-footer">
        <button class="btn-clear" id="resetBtn">Clear All Filters</button>
    </div>
</aside>
<div class="sidebar-overlay" onclick="toggleSidebar()"></div>

<main class="main-content">
    <header class="top-bar">
        <div style="display: flex; align-items: center;">
            <button class="sidebar-toggle" id="sidebarToggle" title="Toggle Sidebar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
            </button>
            <div class="top-bar-title">
                <h1>ResistorSelector v.2.1 by Sam</h1>
                <div id="counter" style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700;">Loading database...</div>
                <div id="selection-note" style="font-size: 0.7rem; color: var(--primary); font-weight: 700; margin-top: 2px; display: none;"></div>
            </div>
        </div>
        <div class="search-area">
            <input type="text" id="pnSearch" class="input-pill" placeholder="🔍 Search Part Number (ERJ...)">
        </div>
    </header>

    <div class="results-area">
        <table class="results-table">
            <thead>
                <tr>
                    <th class="checkbox-cell"></th>
                    <th data-sort="pn">Part Number</th>
                    <th data-sort="rv">Resistance</th>
                    <th data-sort="pr">Power</th>
                    <th data-sort="rt">Tolerance</th>
                    <th data-sort="tc">TCR</th>
                    <th data-sort="sz">Size</th>
                    <th data-sort="se">Series</th>
                    <th data-sort="s">Status</th>
                    <th data-sort="pk">Packaging</th>
                </tr>
            </thead>
            <tbody id="resTable"></tbody>
        </table>
        <div id="sentinel" style="height: 100px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 0.8rem; font-weight: 600;">
            Scroll for more results
        </div>
    </div>

    <div class="pill-container">
        <div id="selection-pill" class="selection-pill"></div>
        <div id="action-pill" class="action-pill">
            <button class="pill-btn btn-clear-sel" onclick="clearSelection()">Clear Selection</button>
            <button class="pill-btn btn-compare" onclick="comparePNs()">Compare PN</button>
            <button class="pill-btn btn-export" onclick="exportTable()">Export Table</button>
            <button class="pill-btn btn-datasheet" onclick="openDatasheet()">Datasheet</button>
            <button class="pill-btn btn-octopart" onclick="openOctopart()">Octopart</button>
            <button class="pill-btn btn-mouser" onclick="openMouser()">Mouser</button>
            <button class="pill-btn btn-farnell" onclick="openFarnell()">Farnell</button>
        </div>
    </div>
</main>

<script src="data.js"></script>
<script src="app.js"></script>
</body>
</html>"""

    index_path = os.path.join(output_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Generated {index_path}")

if __name__ == "__main__":
    generate_modular_files('resistors_compact.json')
