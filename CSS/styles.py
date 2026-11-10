CSS_STYLE = """
window {
    background-color: #121212;
}

.sidebar {
    background-color: #1e1e1e;
    border-right: 2px solid #2e2e2e;
    border-left: none;
}

.sidebar.rtl {
    border-right: none;
    border-left: 2px solid #2e2e2e;
}

.nav-btn {
    color: #a1a1aa;
    background-image: none;
    background-color: transparent;
    border: none;
    border-bottom: 1px solid #121212;
    border-radius: 0px;
    outline: none;
    padding: 12px 15px;
    font-weight: bold;
    font-size: 13px;
    transition: all 0.2s ease;
}

.nav-btn:hover {
    background-color: #2d2d2d;
    color: #4d9de0;
}

.nav-btn:checked, .nav-btn:active {
    background-color: #121212;
    color: #4d9de0;
    border-left: 3px solid #4d9de0;
    border-right: none;
}

/* RTL: flip highlight to the right side */
.sidebar.rtl .nav-btn:checked, .sidebar.rtl .nav-btn:active {
    border-left: none;
    border-right: 3px solid #4d9de0;
}

.btn-accent {
    background-image: none;
    background-color: #3f3f3f;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #525252;
    border-radius: 4px;
    padding: 8px 18px;
}

.btn-accent:hover {
    background-color: #525252;
    color: #ffffff;
}

.btn-accent:disabled {
    background-color: #181818;
    color: #525252;
    border-color: #242424;
}

.btn-orange {
    background-image: none;
    background-color: #8c1610;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #b32017;
    border-radius: 4px;
    padding: 8px 18px;
}

.btn-orange:hover {
    background-color: #b32017;
    color: #ffffff;
}

.btn-orange:disabled {
    background-color: #260705;
    color: #732620;
    border-color: #3d0d0a;
}

.btn-secondary {
    background-image: none;
    background-color: #262626;
    color: #d4d4d8;
    font-weight: bold;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px 12px;
}

.btn-compact {
    background-image: none;
    background-color: #262626;
    color: #d4d4d8;
    font-weight: bold;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 10px;
    min-height: 20px;
    min-width: 70px;
}

.btn-compact:hover {
    background-color: #3c3c3c;
    color: #ffffff;
    border-color: #4d9de0;
}

.btn-compact:disabled {
    background-color: #181818;
    color: #525252;
    border-color: #242424;
}

.btn-secondary:hover {
    background-color: #3c3c3c;
    color: #ffffff;
    border-color: #4d9de0;
}

.btn-secondary:disabled {
    background-color: #181818;
    color: #525252;
    border-color: #242424;
}

.card-panel {
    background-color: #1c1c1c;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 12px;
}

.mod-card {
    background-color: #1c1c1c;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 14px 16px;
    transition: border-color 0.15s ease;
}

.mod-card:hover {
    border-color: #4d9de0;
}

.mod-title {
    font-size: 15px;
    font-weight: bold;
    color: #4d9de0;
}

.mod-card .subtitle {
    font-size: 13px;
    color: #a1a1aa;
}

.console-view {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    background-color: #0c0c0c;
    color: #d4d4d8;
}

.header-title {
    font-size: 18px;
    font-weight: bold;
    color: #4d9de0;
}

.subtitle {
    font-size: 11px;
    color: #a1a1aa;
}

.text-desc {
    font-size: 12px;
    color: #d4d4d8;
}

/* Theme-matching ComboBox / Dropdown styling */
combobox {
    background-color: #262626;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 0px 4px;
    color: #d4d4d8;
    min-height: 0;
}

combobox:hover {
    background-color: #3c3c3c;
    border-color: #4d9de0;
}

.protontricks-backend-combo:disabled,
.protontricks-backend-combo:disabled button {
    background-color: #181818;
    color: #525252;
    border-color: #242424;
}

.protontricks-backend-combo:disabled cellview {
    color: #525252;
}

combobox button {
    background-color: transparent;
    border: none;
    color: #4d9de0;
    padding: 0 4px;
    min-height: 0;
}

combobox cellview {
    color: #d4d4d8;
    padding: 0;
}

/* Style dropdown popup menu */
menu {
    background-color: #1c1c1c;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    color: #d4d4d8;
    padding: 4px;
}

menuitem {
    padding: 6px 12px;
    border-radius: 3px;
    color: #d4d4d8;
}

menuitem:hover, menuitem:active {
    background-color: #2d2d2d;
    color: #4d9de0;
}

/* Theme-matching Radio and Check button styling */
checkbutton, check, radiobutton, radio {
    color: #d4d4d8;
    outline: none;
}

checkbutton check, radiobutton radio {
    min-height: 16px;
    min-width: 16px;
    border: 1px solid #3c3c3c;
    border-radius: 3px;
    background-color: #121212;
    color: #4d9de0;
    margin-right: 6px;
    margin-left: 6px;
    box-shadow: none;
}

checkbutton check:checked, radiobutton radio:checked {
    background-color: #203460;
    border-color: #4d9de0;
    background-image: none;
}

checkbutton check:hover, radiobutton radio:hover {
    border-color: #4d9de0;
}

radiobutton radio {
    border-radius: 50%;
}
"""
