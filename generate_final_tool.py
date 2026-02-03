import json
import os

def generate_html(json_path, output_html):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Base HTML template with sophisticated CSS and JS logic
    html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ResistorSelector v2.1</title>
    <style>
        :root {
            /* Brand & Primary Palette */
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --primary-light: rgba(79, 70, 229, 0.08);
            --primary-ultra-light: rgba(79, 70, 229, 0.04);
            
            /* Backgrounds */
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-header: #fafafa;
            --bg-muted: #f1f5f9;
            
            /* Text */
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            
            /* Borders */
            --border: #e2e8f0;
            --border-hover: #cbd5e1;
            
            /* Status Accents */
            --active-bg: #dcfce7;
            --active-text: #166534;
            --active-border: #bbf7d0;
            
            --nrnd-bg: #fee2e2;
            --nrnd-text: #991b1b;
            --nrnd-border: #fecaca;
            
            /* Delta Feedback tagging */
            --delta-green: #15803d;
            --delta-yellow: #a16207;
            --delta-red: #b91c1c;

            /* Action Buttons */
            --btn-clear: #fee2e2;
            --btn-clear-text: #991b1b;
            --btn-clear-hover: #fecaca;
            
            --btn-compare: #4f46e5;
            --btn-export: #10b981;
            --btn-octopart: #0ea5e9;
            --btn-mouser: #10108a;

            /* Product Category Colors */
            --prod-as: #8b5cf6; /* Anti-Sulfurated - Purple */
            --prod-cs: #3b82f6; /* Current Sensing - Blue */
            --prod-gp: #64748b; /* General Purpose - Slate */
            --prod-hp: #10b981; /* High Precision - Emerald */
            --prod-ht: #f59e0b; /* High Temperature - Amber/Orange */
            --prod-sp: #6366f1; /* Small & High Power - Indigo */
            
            /* Layout */
            --sidebar-width: 320px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar Layout */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            flex-shrink: 0;
            box-shadow: 4px 0 15px rgba(0, 0, 0, 0.05);
            z-index: 100;
            position: relative;
        }

        .sidebar.collapsed {
            display: none;
        }

        .sidebar-scroll {
            flex: 1;
            overflow-y: auto;
        }

        .filter-section {
            border-bottom: 1px solid var(--border);
        }

        .section-header {
            padding: 12px 16px;
            background: #fafafa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .section-header:hover { background: #f1f5f9; }

        .section-content { padding: 16px; }

        .section-collapsed .section-content { display: none; }

        .section-header .arrow { transition: transform 0.2s; font-size: 10px; }
        .section-collapsed .section-header .arrow { transform: rotate(-90deg); }

        .filter-item { margin-bottom: 20px; }
        .filter-item label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 8px;
        }

        /* Fixed Sidebar Footer */
        .sidebar-footer {
            padding: 16px;
            background: var(--bg-card);
            border-top: 1px solid var(--border);
            box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
            margin-top: auto; /* Push to bottom of flex container */
        }

        .btn-clear {
            width: 100%;
            padding: 10px;
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-clear:hover { background: #fecaca; }

        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .top-bar {
            height: 70px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            flex-shrink: 0;
            z-index: 90;
        }

        .top-bar-title h1 {
            font-size: 1.1rem;
            font-weight: 900;
            color: var(--primary);
            letter-spacing: -0.01em;
        }

        .search-area {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        /* Sidebar Toggle Button */
        .sidebar-toggle {
            background: none;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
            transition: all 0.2s;
            margin-right: 16px;
        }
        .sidebar-toggle:hover {
            background: var(--bg-muted);
            color: var(--primary);
            border-color: var(--primary);
        }
        .sidebar-toggle svg { width: 20px; height: 20px; }

        .input-pill {
            padding: 8px 16px;
            border: 1px solid var(--border);
            border-radius: 99px;
            font-size: 0.85rem;
            outline: none;
            transition: all 0.2s;
            width: 250px;
        }
        .input-pill:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }

        /* Tags */
        .tag-group { display: flex; flex-direction: column; gap: 6px; }
        .tag-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }
        
        .tag-btn {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 10px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: white;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-main);
            width: 100%;
            text-align: left;
        }
        .tag-grid .tag-btn { 
            flex-direction: column; 
            padding: 6px 2px; 
            text-align: center; 
            gap: 4px;
            font-size: 0.65rem;
        }
        
        .tag-btn:hover { border-color: var(--border-hover); background: var(--bg-header); }
        .tag-btn.active { background: var(--primary-ultra-light); border-color: var(--primary); color: var(--primary); }
        .tag-btn.unavailable { opacity: 0.3; cursor: not-allowed; background: var(--bg-muted); color: var(--text-light); }

        /* Specific Product Tag Styles when Active */
        .tag-btn.active.prod-as { background: rgba(139, 92, 246, 0.1); border-color: var(--prod-as); color: var(--prod-as); }
        .tag-btn.active.prod-cs { background: rgba(59, 130, 246, 0.1); border-color: var(--prod-cs); color: var(--prod-cs); }
        .tag-btn.active.prod-gp { background: rgba(100, 116, 139, 0.1); border-color: var(--prod-gp); color: var(--prod-gp); }
        .tag-btn.active.prod-hp { background: rgba(16, 185, 129, 0.1); border-color: var(--prod-hp); color: var(--prod-hp); }
        .tag-btn.active.prod-ht { background: rgba(245, 158, 11, 0.1); border-color: var(--prod-ht); color: var(--prod-ht); }
        .tag-btn.active.prod-sp { background: rgba(99, 102, 241, 0.1); border-color: var(--prod-sp); color: var(--prod-sp); }
        
        .count-chip {
            font-size: 0.65rem;
            background: var(--bg-muted);
            color: var(--text-muted);
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            border: 1px solid var(--border);
        }
        .active .count-chip { background: var(--primary); color: white; border-color: var(--primary); }
        
        /* Product active chips */
        .active.prod-as .count-chip { background: var(--prod-as); }
        .active.prod-cs .count-chip { background: var(--prod-cs); }
        .active.prod-gp .count-chip { background: var(--prod-gp); }
        .active.prod-hp .count-chip { background: var(--prod-hp); }
        .active.prod-ht .count-chip { background: var(--prod-ht); }
        .active.prod-sp .count-chip { background: var(--prod-sp); }

        /* Toggle Switch */
        .toggle-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f8fafc;
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            border: 1px solid var(--border);
        }
        .toggle-switch {
            position: relative;
            width: 40px;
            height: 20px;
            background: #cbd5e1;
            border-radius: 20px;
            cursor: pointer;
            transition: 0.3s;
        }
        .toggle-switch.active { background: var(--primary); }
        .toggle-knob {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            background: white;
            border-radius: 50%;
            transition: 0.3s;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .toggle-switch.active .toggle-knob { transform: translateX(20px); }

        /* Range Slider */
        .range-container { position: relative; height: 30px; margin: 15px 0; }
        .slider-track {
            position: absolute;
            width: 100%;
            height: 6px;
            background: #e2e8f0;
            top: 50%;
            transform: translateY(-50%);
            border-radius: 3px;
        }
        .dual-range input[type="range"] {
            position: absolute;
            width: 100%;
            pointer-events: none;
            -webkit-appearance: none;
            background: none;
            top: 50%;
            transform: translateY(-50%);
            z-index: 2;
        }
        .dual-range input[type="range"]::-webkit-slider-thumb {
            pointer-events: auto;
            -webkit-appearance: none;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: white;
            border: 2px solid var(--primary);
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .range-inputs { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 12px; 
            margin-top: 10px;
        }
        .range-inputs input {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.8rem;
            text-align: center;
            font-weight: 600;
            outline: none;
        }
        .range-inputs input:focus { border-color: var(--primary); }

        /* Results Table */
        .results-area { flex: 1; overflow: auto; padding: 20px; }
        .results-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: white;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }
        .results-table th {
            position: sticky;
            top: 0;
            background: #fafafa;
            padding: 12px 16px;
            font-size: 0.7rem;
            font-weight: 800;
            text-transform: uppercase;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border);
            cursor: pointer;
            user-select: none;
            text-align: left;
            z-index: 10;
        }
        .results-table th:hover { background: #f1f5f9; color: var(--primary); }
        .results-table th.sort-active { color: var(--primary); }
        .results-table th::after {
            content: ' ↕';
            font-size: 0.8em;
            opacity: 0.3;
        }
        .results-table th.sort-desc::after { content: ' ↓'; opacity: 1; }
        .results-table th.sort-asc::after { content: ' ↑'; opacity: 1; }

        .results-table td { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; }
        .results-table tr:last-child td { border-bottom: none; }
        .results-table tr:hover td { background: #f8fafc; }
        .results-table tr.nrfnd { background: #fee2e2; }
        .results-table tr.nrfnd:hover td { background: #fecaca; }

        .part-number { font-weight: 700; color: var(--primary); cursor: pointer; }
        .res-container { display: flex; align-items: center; gap: 8px; }
        .res-value { font-weight: 900; }
        .delta-tag {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 800;
            color: white;
            white-space: nowrap;
        }
        .delta-green { background: #166534; }
        .delta-yellow { background: #854d0e; }
        .delta-red { background: #991b1b; }

        .tag-status { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
        .tag-packaging { font-size: 0.65rem; color: var(--text-muted); font-weight: 500; }
        .status-active { background: var(--active-bg); color: var(--active-text); }
        .status-nrnd { background: var(--nrnd-bg); color: var(--nrnd-text); }

        /* Loading */
        #loader {
            position: fixed; top:0; left:0; width:100%; height:100%;
            background: white; display: flex; flex-direction: column;
            align-items: center; justify-content: center; z-index: 1000;
        }
        .spinner {
            width: 40px; height: 40px; border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary); border-radius: 50%;
            animation: spin 1s linear infinite; margin-bottom: 16px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* Selection Pills */
        .pill-container {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            z-index: 1000;
            pointer-events: none;
        }

        .selection-pill, .action-pill {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            padding: 8px 16px;
            border-radius: 99px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            pointer-events: auto;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .selection-pill {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--primary);
            max-width: 80vw;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            opacity: 0;
            transform: translateY(20px);
        }

        .selection-pill.active {
            opacity: 1;
            transform: translateY(0);
        }

        .action-pill {
            padding: 6px;
            opacity: 0;
            transform: translateY(20px);
        }
        .action-pill.active {
            opacity: 1;
            transform: translateY(0);
        }

        .pill-btn {
            padding: 8px 16px;
            border-radius: 99px;
            border: none;
            font-size: 0.75rem;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
            color: white;
        }

        .btn-clear-sel { background: #64748b; }
        .btn-clear-sel:hover { background: #475569; }
        .btn-compare { background: var(--primary); }
        .btn-compare:hover { background: var(--primary-hover); }
        .btn-export { background: #10b981; }
        .btn-export:hover { background: #059669; }
        .btn-octopart { background: #0ea5e9; }
        .btn-octopart:hover { background: #0284c7; }
        .btn-mouser { background: #1e3a8a; }
        .btn-mouser:hover { background: #1e3a8a; filter: brightness(1.2); }

        .checkbox-cell { width: 40px; text-align: center !important; }
        .custom-checkbox {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid var(--border);
            cursor: pointer;
            transition: all 0.2s;
            display: inline-block;
            vertical-align: middle;
            position: relative;
        }
        .custom-checkbox.checked {
            background: var(--primary);
            border-color: var(--primary);
        }
        .custom-checkbox.checked::after {
            content: '✓';
            color: white;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            font-weight: 900;
        }

        /* Mobile Optimization */
        @media (max-width: 768px) {
            body { position: relative; }
            
            .sidebar {
                position: fixed;
                left: 0;
                top: 0;
                bottom: 0;
                width: 280px;
                height: 100%;
                box-shadow: 5px 0 25px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
                z-index: 1100; /* Above pills on mobile */
            }

            .sidebar.collapsed {
                display: flex; /* Keep layout but hide with transform */
                transform: translateX(-100%);
            }

            .main-content {
                width: 100%;
            }

            .top-bar {
                padding: 0 12px;
                height: 60px;
                gap: 8px;
            }

            .top-bar-title h1 { font-size: 0.9rem; }
            .top-bar-title #counter { font-size: 0.65rem; }

            .search-area .input-pill {
                width: 140px;
                padding: 6px 12px;
                font-size: 0.75rem;
            }

            .results-area {
                padding: 8px;
            }

            .results-table th, .results-table td {
                padding: 8px 10px;
                font-size: 0.75rem;
            }

            .sidebar-toggle {
                margin-right: 8px;
                padding: 6px;
            }

            /* Overlay for mobile when sidebar is open */
            .sidebar-overlay {
                display: none;
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(2px);
                z-index: 95;
            }
            .sidebar:not(.collapsed) + .sidebar-overlay {
                display: block;
            }

            .pill-container {
                bottom: 12px;
                width: 95%;
            }
            .action-pill {
                flex-wrap: wrap;
                justify-content: center;
                border-radius: 20px;
                padding: 12px;
            }
            .pill-btn {
                padding: 6px 12px;
                font-size: 0.7rem;
            }
        }
        
        /* Scrollbars */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
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
                            <span>100μΩ</span>
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
                <h1>ResistorSelector</h1>
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
            <button class="pill-btn btn-octopart" onclick="openOctopart()">Octopart</button>
            <button class="pill-btn btn-mouser" onclick="openMouser()">Mouser</button>
        </div>
    </div>
</main>

<script>
    const DATA = __RESISTOR_DATA__;
    const { lookups, resistors } = DATA;

    const MIN_RES = 0.0001; 
    const MAX_RES = 100000000;
    const LOG_MIN = Math.log10(MIN_RES);
    const LOG_MAX = Math.log10(MAX_RES);

    let state = {
        resMin: 0,
        resMax: MAX_RES,
        targetRes: null, // For coloring
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
        activeValues: null // To track exactly what's being shown (exact match or closest neighbors)
    };

    let filtered = [];
    let displayedCount = 100;
    const INCREMENT = 100;

    function init() {
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
        document.getElementById('pnSearch').oninput = (e) => { state.search = e.target.value.toLowerCase(); refresh(); };
        document.getElementById('seriesSelect').onchange = (e) => { state.series = e.target.value; refresh(); };
        document.getElementById('decimalToggle').onclick = toggleDecimal;
        document.getElementById('resetBtn').onclick = resetFilters;

        document.querySelectorAll('thead th[data-sort]').forEach(th => {
            th.onclick = () => onSort(th.dataset.sort);
        });

        document.getElementById('sidebarToggle').onclick = toggleSidebar;

        // Auto-collapse sidebar on very small screens initially
        if (window.innerWidth < 768) {
            document.querySelector('.sidebar').classList.add('collapsed');
        }

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
            if (v >= 1000000) return (v/1000000).toFixed(2).replace(/\.00$/, '').replace(/\.0$/, '') + " MΩ";
            if (v >= 1000) return (v/1000).toFixed(2).replace(/\.00$/, '').replace(/\.0$/, '') + " kΩ";
            if (v < 1) return (v*1000).toFixed(1).replace(/\.0$/, '') + " mΩ";
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

    function getShort(g) { return {products:'p', status:'s', tolerance:'rt', power:'pr', tcr:'tc', size:'sz'}[g]; }

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
                <tr class="${status === 'NRFND' ? 'nrfnd' : ''}" onclick="toggleSelect('${r.pn}')">
                    <td class="checkbox-cell">
                        <div class="custom-checkbox ${isSelected ? 'checked' : ''}"></div>
                    </td>
                    <td><span class="part-number" onclick="event.stopPropagation(); window.open('https://octopart.com/search?q='+encodeURIComponent('${r.pn}'), '_blank')">${r.pn}</span></td>
                    <td>
                        <div class="res-container">
                            <span class="res-value">${formatRes(r.rv)}</span>
                            ${deltaTag}
                        </div>
                    </td>
                    <td>${lookups.power[r.pr]}W</td>
                    <td>${lookups.tolerance[r.rt]}%</td>
                    <td>${lookups.tcr[r.tc]}</td>
                    <td>${lookups.size[r.sz]}</td>
                    <td>${lookups.series[r.se]}</td>
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
            pill.textContent = state.selectedPns.join(', ');
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

    window.onload = init;
</script>
</body>
</html>
"""
    
    # Inject data
    final_html = html_content.replace('__RESISTOR_DATA__', json.dumps(data))
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"Generated {output_html}")

if __name__ == "__main__":
    generate_html('resistors_compact.json', 'resistor_selector_v2.html')
    generate_html('resistors_compact.json', 'index.html')
