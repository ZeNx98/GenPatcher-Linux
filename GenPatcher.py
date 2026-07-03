#!/usr/bin/env python3
import os
import sys
import shutil
import threading
import subprocess

ZH_APP_ID = "2732960"
ZH_GAME_FOLDER = "Command & Conquer Generals - Zero Hour"
OFFLINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Offline")

GAME_ROOT = ""
GENERALS_DIR = ""
PREFIX_DIR = ""
DOCS_DIR = ""
ZH_DOCS_DATA = ""
CCG_DOCS_DATA = ""

def find_steam_roots():
    """Find all possible Steam root directories on this system."""
    candidates = [
        os.path.expanduser("~/.local/share/Steam"),
        os.path.expanduser("~/.steam/steam"),
        os.path.expanduser("~/.steam/root"),
        "/usr/share/steam",
        "/opt/steam",
    ]
    if os.environ.get("STEAM_ROOT"):
        candidates.insert(0, os.environ["STEAM_ROOT"])
    return [p for p in candidates if os.path.isdir(p)]

def parse_vdf_library_paths(steam_root):
    """Parse libraryfolders.vdf and return all Steam library paths."""
    vdf_path = os.path.join(steam_root, "steamapps", "libraryfolders.vdf")
    if not os.path.exists(vdf_path):
        return []
    paths = []
    try:
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith('"path"'):
                    parts = line.split('"')
                    if len(parts) >= 4:
                        lib_path = parts[3].strip()
                        if os.path.isdir(lib_path):
                            paths.append(lib_path)
    except Exception:
        pass
    return paths

def detect_steam_game():
    """Dynamically locate ZH game folder across all Steam libraries."""
    global GAME_ROOT, GENERALS_DIR, PREFIX_DIR, DOCS_DIR, ZH_DOCS_DATA, CCG_DOCS_DATA

    all_library_roots = set()

    for steam_root in find_steam_roots():
        all_library_roots.add(steam_root)
        for lib in parse_vdf_library_paths(steam_root):
            all_library_roots.add(lib)

    for lib_root in all_library_roots:
        common_path = os.path.join(lib_root, "steamapps", "common", ZH_GAME_FOLDER)
        exe_found = (
            os.path.exists(os.path.join(common_path, "Generals.exe")) or
            os.path.exists(os.path.join(common_path, "generals.exe")) or
            os.path.exists(os.path.join(common_path, "GeneralsOnlineZH.exe"))
        )
        if exe_found:
            GAME_ROOT = common_path
            GENERALS_DIR = os.path.join(GAME_ROOT, "ZH_Generals")
            steamapps_root = os.path.join(lib_root, "steamapps")
            PREFIX_DIR = os.path.join(steamapps_root, "compatdata", ZH_APP_ID, "pfx")
            DOCS_DIR = os.path.join(PREFIX_DIR, "drive_c", "users", "steamuser", "Documents")
            ZH_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Zero Hour Data")
            CCG_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Data")
            return True
    return False

def set_game_root(new_path):
    """Manually override the game root (used by LOCATE button)."""
    global GAME_ROOT, GENERALS_DIR, PREFIX_DIR, DOCS_DIR, ZH_DOCS_DATA, CCG_DOCS_DATA
    GAME_ROOT = os.path.abspath(new_path)
    GENERALS_DIR = os.path.join(GAME_ROOT, "ZH_Generals")

    if "steamapps" + os.sep + "common" in GAME_ROOT or "steamapps/common" in GAME_ROOT:
        steamapps_root = GAME_ROOT
        while os.path.basename(steamapps_root) != "steamapps" and os.path.dirname(steamapps_root) != steamapps_root:
            steamapps_root = os.path.dirname(steamapps_root)
        PREFIX_DIR = os.path.join(steamapps_root, "compatdata", ZH_APP_ID, "pfx")
    else:
        PREFIX_DIR = (
            os.environ.get("WINEPREFIX") or
            os.path.expanduser("~/.wine")
        )

    DOCS_DIR = os.path.join(PREFIX_DIR, "drive_c", "users", "steamuser", "Documents")
    if not os.path.isdir(DOCS_DIR):
        win_users = os.path.join(PREFIX_DIR, "drive_c", "users")
        if os.path.isdir(win_users):
            for user in os.listdir(win_users):
                candidate = os.path.join(win_users, user, "Documents")
                if os.path.isdir(candidate):
                    DOCS_DIR = candidate
                    break
    ZH_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Zero Hour Data")
    CCG_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Data")

detect_steam_game()

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
except ImportError:
    print("\nError: PyGObject / GTK 3 is not installed or configured in Python.")
    print("Please install PyGObject and GTK 3 using your system's package manager.")
    print("Example for Arch Linux:    sudo pacman -S python-gobject gtk3")
    print("Example for Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
    print("Example for Fedora:        sudo dnf install python3-gobject gtk3\n")
    sys.exit(1)

# Custom CSS styling 
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
    min-width: 40px;
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

CURRENT_LANG = "en"

TRANSLATIONS = {
    "en": {
        "apply_fixes": "Apply Fixes",
        "gentool": "GenTool",
        "addons": "Addons & Tools",
        "options": "Game Settings",
        "about": "About / Info",
        "ver_label": "v2.14 Linux GTK",
        "lang_label": "Language:",
        
        "fixes_title": "APPLY FIXES & ONLINE SETUP",
        "fixes_subtitle": "Setup Generals Online client, stability configurations, and runtimes",
        "game_found": "<b>✓ Zero Hour Installation folder:</b> <span foreground='#4d9de0'>FOUND</span>",
        "game_missing": "<b>✗ Zero Hour Installation folder:</b> <span foreground='#ef4444'>MISSING</span>",
        "prefix_found": "<b>✓ Proton Wine prefix database:</b> <span foreground='#4d9de0'>FOUND</span>",
        "prefix_missing": "<b>✗ Proton Wine prefix database:</b> <span foreground='#ef4444'>MISSING</span>",
        "offline_found": "<b>✓ Offline Patch installer assets:</b> <span foreground='#4d9de0'>FOUND</span>",
        "offline_missing": "<b>✗ Offline Patch installer assets:</b> <span foreground='#ef4444'>MISSING</span>",
        "btn_apply": "APPLY FIXES & ONLINE SETUP",
        "btn_apply_done": "FIXES ALREADY APPLIED",
        "btn_locate": "LOCATE generals.exe",
        "welcome_console": "Welcome to GenPatcher Linux Console. Ready to apply online setup and stability fixes.",
        
        "gentool_title": "GENTOOL ENHANCEMENT",
        "gentool_subtitle": "Install GenTool utility for modern screen configurations",
        "gentool_desc": "GenTool is the single most important utility for C&C Generals & Zero Hour. It adds:\n\n• Full widescreen resolution support natively\n• In-game camera zoom adjustments (singleplayer & observer)\n• Multiplayer anti-cheat integration & online platform support\n• Framerate stabilization caps for modern processors\n• Borderless window mode options",
        "btn_gentool": "INSTALL GENTOOL",
        "btn_gentool_done": "GENTOOL ALREADY INSTALLED",
        
        "addons_title": "ADDONS & TOOLS",
        "addons_subtitle": "Install optional community mods and customizations",
        "cb_title": "Control Bar Pro HUD",
        "cb_desc": "Sleek, modern in-game HUD interface built and optimized for modern widescreen monitors.",
        "cb_res_label": "Resolution:",
        "btn_hud": "INSTALL HUD",
        "btn_hud_done": "REINSTALL HUD",
        
        "hk_title": "Hotkey Control Scheme Profiles",
        "hk_desc": "Select and apply custom keybindings to align in-game icons with your keyboard keys.",
        "hk_leikeze": "Leikeze Grid Layout",
        "hk_lang": "Language: ",
        "hk_legionnaire": "Legionnaire Layout",
        "hk_default": "Restore Default Scheme",
        "hk_visual": "Show hotkey letters on control bar (HUD)",
        "btn_hk": "APPLY HOTKEYS",
        "btn_hk_done": "REAPPLY HOTKEYS",
        
        "maps_title": "Community Map Pack",
        "maps_desc": "Huge selection of customized skirmish maps, co-op campaign stages, and Art Of Defense (AOD) challenges.",
        "btn_maps": "EXTRACT MAPS",
        "btn_maps_done": "RE-EXTRACT MAPS",
        
        "gl_title": "GenLauncher Mod Manager",
        "gl_desc": "Central launcher for installing and running mods like Rise of the Reds, Shockwave, or Operation Firestorm.",
        "btn_gl": "INSTALL GENLAUNCHER",
        "btn_gl_done": "REINSTALL GENLAUNCHER",
        
        "font_title": "Unicode Russian Font Fix",
        "font_desc": "Unicode font patch (GenArial) to resolve formatting issues or startup crashes on Cyrillic game installations.",
        "btn_font": "INSTALL FONT FIX",
        "btn_font_done": "REINSTALL FONT FIX",
        

        "btn_open": "OPEN",
        "btn_check_update": "CHECK FOR CLIENT UPDATE",
        "update_found_title": "Update Available",
        "update_found_text": "A new version of the Generals Online client is available.\n\nInstalled Version: {current}\nLatest Available: {latest}\n\nWould you like to download and install it now?",
        "no_update_title": "Up to Date",
        "no_update_text": "Your Generals Online client is already up to date.",
        "btn_github": "GitHub Page",
        "btn_generals_online": "Generals Online",
        "btn_gentool_page": "GenTool Page",
        "btn_genpatcher_page": "GenPatcher Page",
        
        "about_title": "ABOUT GENPATCHER",
        "about_subtitle": "Information and credits regarding this project",
        "about_desc": "GenPatcher Linux is an open-source utility designed to configure, patch, and optimize Command & Conquer: Generals and Zero Hour for Wine and Proton environments. It automates prefix setup, registry DLL overrides, resolution matching, and mod deployment natively on Linux distributions.\n\nProject Home: https://github.com/ZeNx98/GenPatcher-Linux\nDeveloper: ZeNx98\n\nSpecial Thanks:\n• Legionnaire (Original creator of GenPatcher for Windows, who compiled the stability fixes and community assets)\n• Generals Online and C&C Online Community Teams\n\nDisclaimer: This project is distributed in the hope that it will be useful, but without any warranty. Running these modifications is at your own risk."
    },
    "ar": {
        "apply_fixes": "تطبيق الإصلاحات",
        "gentool": "جين تول",
        "addons": "الإضافات والأدوات",
        "options": "إعدادات اللعبة",
        "about": "حول البرنامج",
        "ver_label": "نسخة لينكس v2.14",
        "lang_label": "اللغة:",
        
        "fixes_title": "تطبيق الإصلاحات وإعداد اللعب عبر الإنترنت",
        "fixes_subtitle": "إعداد Generals Online وتكوينات الاستقرار والمكتبات البرمجية",
        "game_found": "<b>✓ مجلد تثبيت Zero Hour:</b> <span foreground='#4d9de0'>تم العثور عليه</span>",
        "game_missing": "<b>✗ مجلد تثبيت Zero Hour:</b> <span foreground='#ef4444'>مفقود</span>",
        "prefix_found": "<b>✓ قاعدة بيانات المستودع Proton Wine:</b> <span foreground='#4d9de0'>تم العثور عليها</span>",
        "prefix_missing": "<b>✗ قاعدة بيانات المستودع Proton Wine:</b> <span foreground='#ef4444'>مفقودة</span>",
        "offline_found": "<b>✓ ملفات التثبيت غير المتصلة بالإنترنت:</b> <span foreground='#4d9de0'>تم العثور عليها</span>",
        "offline_missing": "<b>✗ ملفات التثبيت غير المتصلة بالإنترنت:</b> <span foreground='#ef4444'>مفقودة</span>",
        "btn_apply": "تطبيق الإصلاحات وإعداد اللعب عبر الإنترنت",
        "btn_apply_done": "تم تطبيق الإصلاحات بالفعل",
        "btn_locate": "تحديد موقع generals.exe",
        "welcome_console": "مرحبًا بك في لوحة تحكم GenPatcher للينكس. جاهز لتطبيق إعدادات اللعب عبر الإنترنت وإصلاحات الاستقرار.",
        
        "gentool_title": "تحسينات GENTOOL",
        "gentool_subtitle": "تثبيت أداة GenTool لتكوينات الشاشة الحديثة",
        "gentool_desc": "تعد أداة GenTool أهم أداة مساعدة للعبة C&C Generals & Zero Hour. فهي تضيف:\n\n• دعم كامل ودقيق لدقة الشاشة العريضة تلقائيًا\n• تعديل مستوى تقريب الكاميرا داخل اللعبة (اللعب الفردي والمشاهدة)\n• دمج نظام مكافحة الغش واللعب الجماعي عبر منصات الإنترنت\n• تثبيت واستقرار معدل الإطارات للمعالجات الحديثة\n• خيارات تشغيل اللعبة في وضع النافذة بدون حواف",
        "btn_gentool": "تثبيت GENTOOL",
        "btn_gentool_done": "GENTOOL مثبت بالفعل",
        
        "addons_title": "الإضافات والأدوات",
        "addons_subtitle": "تثبيت التعديلات والخرائط والتخصيصات المجتمعية الاختيارية",
        "cb_title": "واجهة التحكم الاحترافية HUD",
        "cb_desc": "واجهة تحكم HUD أنيقة وعصرية مصممة ومحسنة للشاشات العريضة الحديثة.",
        "cb_res_label": "الدقة المطلوبة:",
        "btn_hud": "تثبيت واجهة التحكم",
        "btn_hud_done": "إعادة تثبيت واجهة التحكم",
        
        "hk_title": "مخططات الاختصارات",
        "hk_desc": "تطبيق اعدادات اختصار لتسهيل التحكم داخل اللعبة ولوحة المفاتيح.",
        "hk_leikeze": "تخطيط Leikeze",
        "hk_lang": "اللغة: ",
        "hk_legionnaire": "تخطيط Legionnaire",
        "hk_default": "استعادة التخطيط الأصلي للعبة",
        "hk_visual": "إظهار أحرف الاختصارات على واجهة التحكم (HUD)",
        "btn_hk": "تطبيق الاختصارات",
        "btn_hk_done": "إعادة تطبيق الاختصارات",
        
        "maps_title": "حزمة خرائط المجتمع",
        "maps_desc": "مجموعة ضخمة من خرائط اللعب الجماعي واللعب الفردي المخصصة وتحديات الدفاع (AOD).",
        "btn_maps": "استخراج الخرائط",
        "btn_maps_done": "إعادة استخراج الخرائط",
        
        "gl_title": "مدير التعديلات GenLauncher",
        "gl_desc": "منصة مركزية سهلة لتثبيت وتشغيل التعديلات الكبرى مثل Rise of the Reds و Shockwave.",
        "btn_gl": "تثبيت GENLAUNCHER",
        "btn_gl_done": "إعادة تثبيت GENLAUNCHER",
        
        "font_title": "إصلاح خطوط اليونيكود الروسية",
        "font_desc": "تطبيق خطوط اليونيكود (GenArial) لحل مشاكل التنسيق أو حالات الانهيار المفاجئ للغة الروسية.",
        "btn_font": "تثبيت إهمال خطوط",
        "btn_font_done": "إعادة تثبيت إهمال خطوط",
        

        "btn_open": "فتح",
        "btn_check_update": "التحقق من تحديث جنرالز اونلاين",
        "update_found_title": "تحديث متوفر",
        "update_found_text": "يتوفر إصدار جديد من Generals Online.\n\nالإصدار المثبت: {current}\nالإصدار الأخير: {latest}\n\nهل ترغب في تنزيله وتثبيته الآن؟",
        "no_update_title": "محدث بالكامل",
        "no_update_text": "Generals Online لديك محدث بالفعل إلى آخر إصدار.",
        "btn_github": "صفحة GitHub",
        "btn_generals_online": "جنرالز أونلاين",
        "btn_gentool_page": "موقع GenTool",
        "btn_genpatcher_page": "موقع GenPatcher",
        
        "about_title": "حول GENPATCHER",
        "about_subtitle": "معلومات واعتمادات مطوري هذا المشروع",
        "about_desc": "GenPatcher للينكس هو أداة مفتوحة المصدر مصممة لتهيئة وتحسين وتعديل لعبة Command & Conquer: Generals و Zero Hour لبيئات التشغيل Wine و Proton. يقوم البرنامج بأتمتة إعدادات البادئة وتجاوزات سجل DLL ومطابقة دقة الشاشة وتثبيت الإضافات تلقائيًا على توزيعات لينكس.\n\nصفحة المشروع: https://github.com/ZeNx98/GenPatcher-Linux\nالمطور: ZeNx98\n\nشكر خاص:\n• Legionnaire (المطور الأصلي لأداة GenPatcher على نظام ويندوز، ومجمع إصلاحات الاستقرار والملفات المجتمعية)\n• فرق مجتمع Generals Online و C&C Online\n\nإخلاء مسؤولية: يتم توزيع هذا المشروع على أمل أن يكون مفيدًا، ولكن دون أي ضمان. تشغيل هذه التعديلات يكون على مسؤوليتك الخاصة."
    }
}

class GenPatcherGTK(Gtk.Window):
    def tr(self, key):
        return TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["en"]).get(key, key)

    def __init__(self):
        super().__init__(title="GenPatcher Linux")
        self.set_default_size(700, 500)
        self.set_size_request(600, 400)
        self.set_resizable(True)
        self.connect("destroy", Gtk.main_quit)
        
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(CSS_STYLE.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        self.auto_detect_game_root()
        
        self._busy = False
        self.install_buttons = []
        
        self.diagnostics = check_paths()
        
        self._addon_buttons = []
        self.create_layout()
        self.show_page("fixes")
        self.load_diagnostics()
        
        self.install_buttons = [
            self.btn_apply,
            self.btn_gentool,
            self.btn_check_update,
        ] + self._addon_buttons

        threading.Thread(target=self.startup_update_check, daemon=True).start()

    def set_busy(self):
        """Disable all install buttons while a worker is running."""
        self._busy = True
        for btn in self.install_buttons:
            GLib.idle_add(btn.set_sensitive, False)

    def clear_busy(self):
        """Re-enable all install buttons after a worker finishes (respecting applied status)."""
        self._busy = False
        for btn in self.install_buttons:
            if btn == self.btn_apply and self.diagnostics.get("fixes_applied", False):
                continue
            if btn == self.btn_gentool and self.diagnostics.get("gentool_installed", False):
                continue
            GLib.idle_add(btn.set_sensitive, True)
        GLib.idle_add(self.load_diagnostics)

    def auto_detect_game_root(self):
        """Re-run dynamic detection; show warning if game not found."""
        found = detect_steam_game()
        if not found:
            print("Warning: Could not auto-detect Zero Hour installation. Use the LOCATE button to set the path manually.")

    def create_layout(self):
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.main_box)
        
        self.sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sidebar_box.get_style_context().add_class("sidebar")
        self.sidebar_box.set_size_request(160, -1)
        self.main_box.pack_start(self.sidebar_box, False, False, 0)
        
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.logo_box_ref = logo_box
        logo_box.set_margin_top(25)
        logo_box.set_margin_bottom(2)
        logo_box.set_margin_start(15)
        
        logo_filename = os.path.join("Images", "Logo", "GenPatcher logo.png")
        logo_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo_filename)

        if os.path.exists(logo_img_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(logo_img_path)
                original_w = pixbuf.get_width()
                original_h = pixbuf.get_height()
                target_w = 130
                target_h = int(target_w * (original_h / original_w)) if original_w > 0 else 30
                scaled_pixbuf = pixbuf.scale_simple(target_w, target_h, GdkPixbuf.InterpType.BILINEAR)
                logo_img = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
                logo_box.pack_start(logo_img, False, False, 0)
            except Exception as e:
                logo_img = Gtk.Image.new_from_file(logo_img_path)
                logo_box.pack_start(logo_img, False, False, 0)
            
        self.sidebar_box.pack_start(logo_box, False, False, 0)
        
        self.ver_lbl = Gtk.Label(label="v2.14 Linux GTK")
        self.ver_lbl.get_style_context().add_class("subtitle")
        self.ver_lbl.set_xalign(0)
        self.ver_lbl.set_margin_start(15)
        self.ver_lbl.set_margin_bottom(25)
        self.sidebar_box.pack_start(self.ver_lbl, False, False, 0)
        
        self.gui_lang_combo = Gtk.ComboBoxText()
        self.gui_lang_combo.append("en", "English")
        self.gui_lang_combo.append("ar", "العربية")
        self.gui_lang_combo.set_active_id("en")
        self.gui_lang_combo.set_margin_start(15)
        self.gui_lang_combo.set_margin_end(15)
        self.gui_lang_combo.set_margin_bottom(15)
        self.gui_lang_combo.connect("changed", self.on_gui_lang_changed)
        self.sidebar_box.pack_end(self.gui_lang_combo, False, False, 0)

        self.lang_lbl = Gtk.Label(label="Language:")
        self.lang_lbl.get_style_context().add_class("subtitle")
        self.lang_lbl.set_margin_top(15)
        self.lang_lbl.set_margin_bottom(5)
        self.lang_lbl.set_margin_start(15)
        self.lang_lbl.set_xalign(0)
        self.sidebar_box.pack_end(self.lang_lbl, False, False, 0)
        
        self.nav_group = []
        self.nav_btns = {}
        
        navs = [
            (self.tr("apply_fixes"), "fixes"),
            (self.tr("gentool"), "gentool"),
            (self.tr("addons"), "addons"),
            (self.tr("about"), "about")
        ]
        
        for label, page_id in navs:
            btn = Gtk.RadioButton.new_with_label_from_widget(
                self.nav_group[0] if self.nav_group else None,
                label
            )
            btn.set_mode(False)
            btn.get_style_context().add_class("nav-btn")
            btn.connect("toggled", self.on_nav_toggled, page_id)
            self.sidebar_box.pack_start(btn, False, False, 0)
            self.nav_btns[page_id] = btn
            if not self.nav_group:
                self.nav_group.append(btn)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        self.main_box.pack_start(self.stack, True, True, 0)
        
        self.build_fixes_page()
        self.build_gentool_page()
        self.build_addons_page()
        self.build_about_page()

    def on_nav_toggled(self, button, page_id):
        if button.get_active():
            self.show_page(page_id)

    def show_page(self, page_id):
        self.stack.set_visible_child_name(page_id)

    def load_diagnostics(self):
        self.diagnostics = check_paths()
        
        if self.diagnostics["game_detected"]:
            self.game_lbl.set_markup(self.tr("game_found"))
            self.btn_open_game.set_sensitive(True)
            if self.diagnostics["fixes_applied"]:
                self.btn_apply.set_sensitive(False)
                self.btn_apply.set_label(self.tr("btn_apply_done"))
            else:
                self.btn_apply.set_sensitive(True)
                self.btn_apply.set_label(self.tr("btn_apply"))
        else:
            self.game_lbl.set_markup(self.tr("game_missing"))
            self.btn_open_game.set_sensitive(False)
            self.btn_apply.set_sensitive(False)
            self.btn_apply.set_label(self.tr("btn_apply"))
            
        if self.diagnostics["prefix_detected"]:
            self.prefix_lbl.set_markup(self.tr("prefix_found"))
            self.btn_open_prefix.set_sensitive(True)
        else:
            self.prefix_lbl.set_markup(self.tr("prefix_missing"))
            self.btn_open_prefix.set_sensitive(False)
            

            

        if self.diagnostics["gentool_installed"]:
            self.btn_gentool.set_sensitive(False)
            self.btn_gentool.set_label(self.tr("btn_gentool_done"))
        else:
            self.btn_gentool.set_sensitive(self.diagnostics["game_detected"])
            self.btn_gentool.set_label(self.tr("btn_gentool"))

        if self.diagnostics.get("hud_installed", False):
            self.btn_hud.set_label(self.tr("btn_hud_done"))
        else:
            self.btn_hud.set_label(self.tr("btn_hud"))

        if self.diagnostics.get("hotkeys_applied", False):
            self.btn_hotkeys.set_label(self.tr("btn_hk_done"))
        else:
            self.btn_hotkeys.set_label(self.tr("btn_hk"))

        if self.diagnostics.get("maps_installed", False):
            self.btn_maps.set_label(self.tr("btn_maps_done"))
        else:
            self.btn_maps.set_label(self.tr("btn_maps"))

        if self.diagnostics.get("genlauncher_installed", False):
            self.btn_genlauncher.set_label(self.tr("btn_gl_done"))
        else:
            self.btn_genlauncher.set_label(self.tr("btn_gl"))

        if self.diagnostics.get("fonts_installed", False):
            self.btn_fonts.set_label(self.tr("btn_font_done"))
        else:
            self.btn_fonts.set_label(self.tr("btn_font"))

    def write_log(self, text):
        buf = self.console_view.get_buffer()
        end_iter = buf.get_end_iter()
        buf.insert(end_iter, text + "\n")
        mark = buf.create_mark(None, buf.get_end_iter(), False)
        self.console_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def thread_log(self, text):
        GLib.idle_add(self.write_log, text)

    def update_progress(self, pct, msg=None):
        GLib.idle_add(self.progressbar.set_fraction, pct / 100.0)
        if msg:
            self.thread_log(msg)

    def copy_file_helper(self, src, dst):
        if not os.path.exists(src):
            self.thread_log(f"Warning: Source file missing: {os.path.basename(src)}")
            return False
            
        if os.path.exists(dst) or os.path.islink(dst):
            backup_file(dst)
            if os.path.islink(dst) or os.path.isdir(dst):
                os.remove(dst)
            else:
                os.chmod(dst, 0o777)
                os.remove(dst)
                
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        if dst.endswith(".exe") or dst.endswith(".dat") or dst.endswith(".dll"):
            os.chmod(dst, 0o755)
        self.thread_log(f"✓ Copied: {os.path.basename(src)} -> {os.path.basename(dst)}")
        return True

    def rename_file_helper(self, filepath):
        if os.path.exists(filepath):
            bak_path = filepath + ".bak"
            if not os.path.exists(bak_path):
                shutil.move(filepath, bak_path)
                self.thread_log(f"✓ Disabled: {os.path.basename(filepath)} -> {os.path.basename(filepath)}.bak")
            else:
                os.remove(filepath)
                self.thread_log(f"✓ Removed redundant crash file: {os.path.basename(filepath)}")

    def extract_worker_7z(self, archive_path, output_dir):
        if not os.path.exists(archive_path):
            self.thread_log(f"Warning: Archive missing: {os.path.basename(archive_path)}")
            return False
        self.thread_log(f"Extracting {os.path.basename(archive_path)}...")
        cmd = ["7z", "x", "-y", f"-o{output_dir}", archive_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            self.thread_log(f"✓ Extracted successfully: {os.path.basename(archive_path)}")
            return True
        else:
            self.thread_log(f"Error: Extraction failed: {os.path.basename(archive_path)}")
            return False

    def extract_map_pack_worker(self, archive_path):
        temp_dir = "/tmp/genpatcher_gtk_map_extract"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        if self.extract_worker_7z(archive_path, temp_dir):
            zh_src = os.path.join(temp_dir, "ZH/Maps")
            if os.path.exists(zh_src):
                zh_dst = os.path.join(ZH_DOCS_DATA, "Maps")
                os.makedirs(zh_dst, exist_ok=True)
                for item in os.listdir(zh_src):
                    src_item = os.path.join(zh_src, item)
                    dst_item = os.path.join(zh_dst, item)
                    if os.path.isdir(src_item):
                        if os.path.exists(dst_item):
                            shutil.rmtree(dst_item)
                        shutil.copytree(src_item, dst_item)
                    else:
                        shutil.copy2(src_item, dst_item)
                self.thread_log(f"✓ Extracted Zero Hour custom maps.")

            ccg_src = os.path.join(temp_dir, "CCG/Maps")
            if os.path.exists(ccg_src):
                ccg_dst = os.path.join(CCG_DOCS_DATA, "Maps")
                os.makedirs(ccg_dst, exist_ok=True)
                for item in os.listdir(ccg_src):
                    src_item = os.path.join(ccg_src, item)
                    dst_item = os.path.join(ccg_dst, item)
                    if os.path.isdir(src_item):
                        if os.path.exists(dst_item):
                            shutil.rmtree(dst_item)
                        shutil.copytree(src_item, dst_item)
                    else:
                        shutil.copy2(src_item, dst_item)
                self.thread_log(f"✓ Extracted base Generals custom maps.")
                
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def copy_recursive_helper(self, src_dir, dst_dir):
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            target_dir = dst_dir if rel_path == "." else os.path.join(dst_dir, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(target_dir, f)
                if os.path.exists(dst_file) or os.path.islink(dst_file):
                    backup_file(dst_file)
                    if os.path.islink(dst_file):
                        os.remove(dst_file)
                    else:
                        os.chmod(dst_file, 0o777)
                        os.remove(dst_file)
                shutil.copy2(src_file, dst_file)
                os.chmod(dst_file, 0o755)

    # ==========================================
    # PAGE 1: APPLY FIXES & ONLINE SETUP
    # ==========================================
    def build_fixes_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_margin_top(20)
        page_box.set_margin_bottom(20)
        page_box.set_margin_start(20)
        page_box.set_margin_end(20)
        self.stack.add_named(page_box, "fixes")
        
        self.fixes_title = Gtk.Label(label=self.tr("fixes_title"))
        self.fixes_title.get_style_context().add_class("header-title")
        self.fixes_title.set_xalign(0)
        page_box.pack_start(self.fixes_title, False, False, 0)
        
        self.fixes_sub = Gtk.Label(label=self.tr("fixes_subtitle"))
        self.fixes_sub.get_style_context().add_class("subtitle")
        self.fixes_sub.set_xalign(0)
        self.fixes_sub.set_line_wrap(True)
        page_box.pack_start(self.fixes_sub, False, False, 2)
        
        diag_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        diag_box.get_style_context().add_class("card-panel")
        diag_box.set_margin_top(10)
        page_box.pack_start(diag_box, False, False, 0)
        
        game_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.game_lbl = Gtk.Label()
        self.game_lbl.set_xalign(0)
        game_row.pack_start(self.game_lbl, True, True, 0)
        
        self.btn_open_game = Gtk.Button(label=self.tr("btn_open"))
        self.btn_open_game.get_style_context().add_class("btn-compact")
        self.btn_open_game.connect("clicked", lambda w: self.open_folder_in_fm(GAME_ROOT))
        game_row.pack_end(self.btn_open_game, False, False, 0)
        diag_box.pack_start(game_row, False, False, 2)
        
        prefix_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.prefix_lbl = Gtk.Label()
        self.prefix_lbl.set_xalign(0)
        prefix_row.pack_start(self.prefix_lbl, True, True, 0)
        
        self.btn_open_prefix = Gtk.Button(label=self.tr("btn_open"))
        self.btn_open_prefix.get_style_context().add_class("btn-compact")
        self.btn_open_prefix.connect("clicked", lambda w: self.open_folder_in_fm(PREFIX_DIR))
        prefix_row.pack_end(self.btn_open_prefix, False, False, 0)
        diag_box.pack_start(prefix_row, False, False, 2)
        

        
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        ctrl_box.set_margin_top(12)
        ctrl_box.set_spacing(8)
        page_box.pack_start(ctrl_box, False, False, 0)
        
        self.btn_apply = Gtk.Button(label=self.tr("btn_apply"))
        self.btn_apply.get_style_context().add_class("btn-accent")
        self.btn_apply.connect("clicked", self.start_patching)
        self.btn_apply.set_halign(Gtk.Align.FILL)
        ctrl_box.pack_start(self.btn_apply, False, False, 0)
        
        locate_update_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        ctrl_box.pack_start(locate_update_row, False, False, 0)

        self.btn_locate = Gtk.Button(label=self.tr("btn_locate"))
        self.btn_locate.get_style_context().add_class("btn-secondary")
        self.btn_locate.connect("clicked", self.on_locate_clicked)
        locate_update_row.pack_start(self.btn_locate, True, True, 0)

        self.btn_check_update = Gtk.Button(label=self.tr("btn_check_update"))
        self.btn_check_update.get_style_context().add_class("btn-secondary")
        self.btn_check_update.connect("clicked", self.on_check_update_clicked)
        locate_update_row.pack_start(self.btn_check_update, True, True, 0)
        
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_margin_top(15)
        page_box.pack_start(self.progressbar, False, False, 0)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_margin_top(8)
        page_box.pack_start(scroll, True, True, 0)
        
        self.console_view = Gtk.TextView()
        self.console_view.set_editable(False)
        self.console_view.set_cursor_visible(False)
        self.console_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.console_view.get_style_context().add_class("console-view")
        scroll.add(self.console_view)
        self.write_log("Welcome to GenPatcher Linux Console. Ready to apply online setup and stability fixes.")
        
    def on_locate_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Please select generals.exe (or Generals.exe) from Zero Hour folder",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_exe = Gtk.FileFilter()
        filter_exe.set_name("Game Executable (generals.exe / Generals.exe)")
        filter_exe.add_pattern("*generals.exe")
        filter_exe.add_pattern("*Generals.exe")
        dialog.add_filter(filter_exe)
        
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_file = dialog.get_filename()
            filename = os.path.basename(selected_file).lower()
            if filename == "generals.exe":
                game_dir = os.path.dirname(selected_file)
                if os.path.basename(game_dir) == "ZH_Generals":
                    game_dir = os.path.dirname(game_dir)

                is_steam = ("steamapps/common" in game_dir or
                            "steamapps" + os.sep + "common" in game_dir)

                if is_steam:
                    set_game_root(game_dir)
                    dialog.destroy()
                    self.load_diagnostics()
                    self.write_log(f"✓ Steam game path set to: {GAME_ROOT}")
                    self.show_message_box("Success", f"Game directory resolved:\n{GAME_ROOT}")
                else:
                    dialog.destroy()
                    self._ask_wine_prefix(game_dir)
                    return
            else:
                self.show_message_box("Error", "Invalid file selected. You must select 'generals.exe' or 'Generals.exe'.")
                
        dialog.destroy()

    def _ask_wine_prefix(self, game_dir):
        """Show tutorial popup then folder picker to select Wine prefix for non-Steam installs."""
        tutorial = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="📁  Select Your Wine Prefix Folder"
        )
        tutorial.format_secondary_markup(
            "Because this is a <b>non-Steam installation</b>, GenPatcher needs to know "
            "where your <b>Wine prefix</b> is located.\n\n"
            "<b>What is a Wine prefix?</b>\n"
            "It's a folder that acts as a fake Windows environment for running .exe files "
            "on Linux. It contains a virtual <tt>C:\\</tt> drive with user documents and registry.\n\n"
            "<b>How to find it:</b>\n"
            "• Default location: <tt>~/.wine</tt>\n"
            "• If you use Lutris: check the game's Runner options → "
            "<i>Wine prefix</i> field\n"
            "• If you use Bottles: open the bottle → click the folder icon\n"
            "• If you set <tt>WINEPREFIX</tt> manually, use that folder\n\n"
            "The folder you select must contain a <tt>drive_c/</tt> subfolder inside it.\n\n"
            "Click <b>Select Prefix Folder</b> to continue."
        )
        tutorial.add_button("Cancel", Gtk.ResponseType.CANCEL)
        tutorial.add_button("Select Prefix Folder", Gtk.ResponseType.OK)
        tutorial.set_default_response(Gtk.ResponseType.OK)

        resp = tutorial.run()
        tutorial.destroy()

        if resp != Gtk.ResponseType.OK:
            return

        prefix_dlg = Gtk.FileChooserDialog(
            title="Select your Wine prefix folder (must contain drive_c/)",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        prefix_dlg.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        prefix_dlg.set_current_folder(os.path.expanduser("~"))

        resp2 = prefix_dlg.run()
        if resp2 == Gtk.ResponseType.OK:
            chosen_prefix = prefix_dlg.get_filename()
            prefix_dlg.destroy()

            if not os.path.isdir(os.path.join(chosen_prefix, "drive_c")):
                self.show_message_box(
                    "Invalid Prefix",
                    f"The selected folder does not look like a Wine prefix.\n\n"
                    f"Expected to find a 'drive_c' subfolder inside:\n{chosen_prefix}\n\n"
                    "Please try again and select the correct folder."
                )
                return

            set_game_root(game_dir)

            global PREFIX_DIR, DOCS_DIR, ZH_DOCS_DATA, CCG_DOCS_DATA
            PREFIX_DIR = chosen_prefix
            DOCS_DIR = os.path.join(PREFIX_DIR, "drive_c", "users", "steamuser", "Documents")

            if not os.path.isdir(DOCS_DIR):
                win_users = os.path.join(PREFIX_DIR, "drive_c", "users")
                if os.path.isdir(win_users):
                    for user in os.listdir(win_users):
                        candidate = os.path.join(win_users, user, "Documents")
                        if os.path.isdir(candidate):
                            DOCS_DIR = candidate
                            break

            ZH_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Zero Hour Data")
            CCG_DOCS_DATA = os.path.join(DOCS_DIR, "Command and Conquer Generals Data")

            self.load_diagnostics()
            self.write_log(f"✓ Non-Steam game path set to: {GAME_ROOT}")
            self.write_log(f"✓ Wine prefix set to: {PREFIX_DIR}")
            self.show_message_box(
                "Success",
                f"Game directory:\n{GAME_ROOT}\n\n"
                f"Wine prefix:\n{PREFIX_DIR}"
            )
        else:
            prefix_dlg.destroy()

    def start_patching(self, button):
        if self._busy:
            return
        gentool_dll = os.path.join(GAME_ROOT, "d3d8.dll")
        if not os.path.exists(gentool_dll):
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.NONE,
                text="GenTool is Not Installed"
            )
            dialog.format_secondary_text(
                "GenTool is highly recommended for modern widescreen support, in-game camera zoom, "
                "and online anti-cheat verification.\n\n"
                "Would you like to install GenTool automatically first and then proceed with the setup?"
            )
            dialog.add_button("Install GenTool & Proceed", Gtk.ResponseType.OK)
            dialog.add_button("Cancel Setup", Gtk.ResponseType.CANCEL)
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.OK:
                self.set_busy()
                threading.Thread(target=self._patching_thread, args=(True,), daemon=True).start()
            else:
                self.write_log("Warning: Setup aborted because GenTool was not found.")
                return
        else:
            self.set_busy()
            threading.Thread(target=self._patching_thread, args=(False,), daemon=True).start()

    def _patching_thread(self, install_gentool_first):
        try:
            self.patching_worker(install_gentool_first)
        finally:
            self.clear_busy()

    def patching_worker(self, install_gentool_first):
        try:
            self.update_progress(5, "Contacting playgenerals.online to locate latest client version...")
            
            if install_gentool_first:
                self.update_progress(8, "Auto-installing GenTool first...")
                self.copy_file_helper(os.path.join(OFFLINE_DIR, "d3d8.dll"), os.path.join(GAME_ROOT, "d3d8.dll"))
                if self.diagnostics["ccg_detected"]:
                    self.copy_file_helper(os.path.join(OFFLINE_DIR, "d3d8.dll"), os.path.join(GENERALS_DIR, "d3d8.dll"))
                
                reg_cmd = [
                    "protontricks", "-c",
                    "wine reg add 'HKCU\\Software\\Wine\\DllOverrides' /v d3d8 /t REG_SZ /d native,builtin /f",
                    "2732960"
                ]
                subprocess.run(reg_cmd, capture_output=True, check=True)
                self.thread_log("✓ GenTool auto-installed successfully.")
            
            import urllib.request
            import re
            
            url = "https://cdn.playgenerals.online/GeneralsOnline_setup_062026.exe"
            
            try:
                req = urllib.request.Request(
                    "https://www.playgenerals.online/",
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode('utf-8')
                    match = re.search(r'href=["\'](https://cdn\.playgenerals\.online/GeneralsOnline_setup_[^"\']+\.exe)["\']', html_content)
                    if match:
                        url = match.group(1)
                        self.thread_log(f"✓ Detected latest online installer: {os.path.basename(url)}")
                    else:
                        self.thread_log("Warning: Could not parse latest version from playgenerals.online. Using cached fallback.")
            except Exception as e:
                self.thread_log(f"Warning: Network error while checking version: {str(e)}. Using fallback installer.")

            self.update_progress(20, "Downloading latest Generals Online installer...")
            installer_path = os.path.join(GAME_ROOT, "GeneralsOnline_setup.exe")
            
            req_dl = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req_dl, timeout=30) as dl_resp, open(installer_path, "wb") as f_out:
                f_out.write(dl_resp.read())
            self.thread_log("✓ Downloaded installer successfully.")
            
            self.update_progress(45, "Running Generals Online installer inside Wine prefix...")
            
            exe_name = "generals.exe"
            if os.path.exists(os.path.join(GAME_ROOT, "Generals.exe")):
                exe_name = "Generals.exe"
            wine_exe_param = f"Z:{os.path.join(GAME_ROOT, exe_name)}"
            
            import shlex
            wine_dir_param = f"Z:{GAME_ROOT}"
            inner_cmd = f"cd {shlex.quote(GAME_ROOT)} && wine GeneralsOnline_setup.exe {shlex.quote(wine_exe_param)} /DIR={shlex.quote(wine_dir_param)}"
            
            cmd = [
                "protontricks", "-c",
                inner_cmd,
                "2732960"
            ]
            self.thread_log(f"Executing: protontricks -c '{inner_cmd}' 2732960")
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(installer_path):
                os.remove(installer_path)
            
            online_exe_path = os.path.join(GAME_ROOT, "GeneralsOnlineZH.exe")
            alt_exe_path = os.path.join(GAME_ROOT, "GeneralsOnline.exe")
            
            if not os.path.exists(online_exe_path) and not os.path.exists(alt_exe_path):
                self.thread_log("Error: Generals Online setup did not generate GeneralsOnlineZH.exe or GeneralsOnline.exe.")
                self.thread_log(f"Installer stderr: {res.stderr}")
                self.update_progress(0, "Error: Generals Online installation failed!")
                GLib.idle_add(self.show_message_box, "Installation Failed", 
                               "Generals Online setup did not install successfully. The required executable files were not found.\n\n"
                               "Please review the console logs for details.")
                return

            self.update_progress(65, "Configuring game stability files and creating symlinks...")
            
            self.copy_file_helper(os.path.join(OFFLINE_DIR, "990_DecalsZH.big"), os.path.join(GAME_ROOT, "990_DecalsZH.big"))
            self.copy_file_helper(os.path.join(OFFLINE_DIR, "BIG/Data/English/generals.csf"), os.path.join(GAME_ROOT, "Data/English/generals.csf"))
            
            self.rename_file_helper(os.path.join(GAME_ROOT, "dbghelp.dll"))
            self.rename_file_helper(os.path.join(GAME_ROOT, "BrowserEngine.dll"))

            if self.diagnostics["ccg_detected"]:
                self.copy_file_helper(os.path.join(OFFLINE_DIR, "BIG/Data/English/generals.csf"), os.path.join(GENERALS_DIR, "Data/English/generals.csf"))
                self.rename_file_helper(os.path.join(GENERALS_DIR, "dbghelp.dll"))
                self.rename_file_helper(os.path.join(GENERALS_DIR, "BrowserEngine.dll"))

            old_exe = os.path.join(GAME_ROOT, "Generals.exe")
            legacy_exe = os.path.join(GAME_ROOT, "generals_legacy.exe")
            online_exe_path = os.path.join(GAME_ROOT, "GeneralsOnlineZH.exe")

            if os.path.exists(old_exe) and not os.path.islink(old_exe):
                if os.path.exists(legacy_exe):
                    os.remove(legacy_exe)
                os.rename(old_exe, legacy_exe)
                self.thread_log("✓ Renamed Generals.exe → generals_legacy.exe (vanilla preserved)")
            elif os.path.islink(old_exe):
                os.remove(old_exe)

            if os.path.exists(online_exe_path):
                os.symlink("GeneralsOnlineZH.exe", old_exe)
                self.thread_log("✓ Symlinked Generals.exe → GeneralsOnlineZH.exe")
            else:
                alt_exe_path = os.path.join(GAME_ROOT, "GeneralsOnline.exe")
                if os.path.exists(alt_exe_path):
                    os.symlink("GeneralsOnline.exe", old_exe)
                    self.thread_log("✓ Symlinked Generals.exe → GeneralsOnline.exe")
                else:
                    self.thread_log("Warning: Could not find GeneralsOnlineZH.exe or GeneralsOnline.exe in game root.")

            self.update_progress(75, "Installing VC++ 2005 redistributable...")
            subprocess.run(["protontricks", "-c", f"wine {os.path.join(OFFLINE_DIR, 'vc05')} /q", "2732960"], capture_output=True)
            
            self.update_progress(80, "Installing VC++ 2008 redistributable...")
            subprocess.run(["protontricks", "-c", f"wine {os.path.join(OFFLINE_DIR, 'vc08')} /q", "2732960"], capture_output=True)
            
            self.update_progress(85, "Installing VC++ 2010 redistributable...")
            subprocess.run(["protontricks", "-c", f"wine {os.path.join(OFFLINE_DIR, 'vc10')} /q /norestart", "2732960"], capture_output=True)
            
            self.update_progress(95, "Installing DirectX Runtime package...")
            subprocess.run(["protontricks", "-c", f"wine {os.path.join(OFFLINE_DIR, 'drtx_FILES/DXSETUP.exe')} /silent", "2732960"], capture_output=True)

            ver_file = os.path.join(GAME_ROOT, "generals_online_version.txt")
            ver_stamp = "062026"
            match = re.search(r'GeneralsOnline_setup_(.*?)\.exe', url)
            if match:
                ver_stamp = match.group(1)
            with open(ver_file, "w") as f:
                f.write(ver_stamp)

            self.update_progress(100, "✓ Stability patches and Generals Online successfully installed!")
            GLib.idle_add(self.load_diagnostics)
            GLib.idle_add(self.show_message_box, "Success", "Stability patches and Generals Online client successfully installed!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def startup_update_check(self):
        import time
        time.sleep(1.5)
        if self.diagnostics.get("fixes_applied", False):
            latest_version, latest_url = self.scrape_latest_online_version()
            if latest_version:
                current_version = self.get_installed_online_version()
                if self.is_newer_version(current_version, latest_version):
                    GLib.idle_add(self.prompt_for_client_update, latest_version, latest_url)

    def scrape_latest_online_version(self):
        import urllib.request
        import re
        url = "https://cdn.playgenerals.online/GeneralsOnline_setup_062026.exe"
        version = "062026"
        try:
            req = urllib.request.Request(
                "https://www.playgenerals.online/",
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8')
                match = re.search(r'href=["\'](https://cdn\.playgenerals\.online/GeneralsOnline_setup_([^"\']+)\.exe)["\']', html_content)
                if match:
                    url = match.group(1)
                    version = match.group(2)
        except Exception:
            pass
        return version, url

    def get_installed_online_version(self):
        ver_file = os.path.join(GAME_ROOT, "generals_online_version.txt")
        if os.path.exists(ver_file):
            try:
                with open(ver_file, "r") as f:
                    return f.read().strip()
            except:
                pass
        return "0"

    def is_newer_version(self, current, latest):
        current = current.strip()
        latest = latest.strip()
        if current == latest:
            return False
        try:
            return int(latest) > int(current)
        except:
            return latest != current

    def prompt_for_client_update(self, latest_version, latest_url):
        current_ver = self.get_installed_online_version()
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.tr("update_found_title")
        )
        dialog.format_secondary_text(self.tr("update_found_text").format(current=current_ver, latest=latest_version))
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self.set_busy()
            threading.Thread(target=self.run_update_worker, args=(latest_url, latest_version), daemon=True).start()

    def run_update_worker(self, url, version):
        try:
            self.update_progress(10, "Downloading newer client version...")
            installer_path = os.path.join(GAME_ROOT, "GeneralsOnline_setup.exe")
            import urllib.request
            req_dl = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req_dl, timeout=30) as dl_resp, open(installer_path, "wb") as f_out:
                f_out.write(dl_resp.read())
                
            self.update_progress(50, "Installing newer client inside Wine prefix...")
            exe_name = "generals.exe"
            if os.path.exists(os.path.join(GAME_ROOT, "Generals.exe")):
                exe_name = "Generals.exe"
            wine_exe_param = f"Z:{os.path.join(GAME_ROOT, exe_name)}"
            import shlex
            wine_dir_param = f"Z:{GAME_ROOT}"
            inner_cmd = f"cd {shlex.quote(GAME_ROOT)} && wine GeneralsOnline_setup.exe {shlex.quote(wine_exe_param)} /DIR={shlex.quote(wine_dir_param)}"
            cmd = ["protontricks", "-c", inner_cmd, "2732960"]
            subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(installer_path):
                os.remove(installer_path)
                
            ver_file = os.path.join(GAME_ROOT, "generals_online_version.txt")
            with open(ver_file, "w") as f:
                f.write(version)
                
            self.update_progress(100, "✓ Generals Online client updated successfully!")
            GLib.idle_add(self.show_message_box, "Success", "Generals Online client updated successfully!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")
        finally:
            self.clear_busy()

    def on_check_update_clicked(self, button):
        if self._busy:
            return
        self.set_busy()
        threading.Thread(target=self.manual_update_check_thread, daemon=True).start()

    def manual_update_check_thread(self):
        try:
            self.update_progress(10, "Checking for latest Generals Online client version...")
            latest_version, latest_url = self.scrape_latest_online_version()
            if latest_version:
                current_version = self.get_installed_online_version()
                if self.is_newer_version(current_version, latest_version):
                    GLib.idle_add(self.prompt_for_client_update, latest_version, latest_url)
                else:
                    GLib.idle_add(self.show_message_box, self.tr("no_update_title"), self.tr("no_update_text"))
            else:
                GLib.idle_add(self.show_message_box, "Error", "Could not check for updates. Please try again.")
        finally:
            self.clear_busy()

    def open_folder_in_fm(self, path):
        if path and os.path.exists(path):
            try:
                subprocess.Popen(["xdg-open", path])
            except Exception as e:
                self.write_log(f"Failed to open folder: {str(e)}")

    def show_message_box(self, title, text):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()

    # ==========================================
    # PAGE 2: GENTOOL 
    # ==========================================
    def build_gentool_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_margin_top(20)
        page_box.set_margin_bottom(20)
        page_box.set_margin_start(20)
        page_box.set_margin_end(20)
        self.stack.add_named(page_box, "gentool")
        
        self.gentool_title = Gtk.Label(label=self.tr("gentool_title"))
        self.gentool_title.get_style_context().add_class("header-title")
        self.gentool_title.set_xalign(0)
        page_box.pack_start(self.gentool_title, False, False, 0)
        
        self.gentool_sub = Gtk.Label(label=self.tr("gentool_subtitle"))
        self.gentool_sub.get_style_context().add_class("subtitle")
        self.gentool_sub.set_xalign(0)
        self.gentool_sub.set_line_wrap(True)
        page_box.pack_start(self.gentool_sub, False, False, 2)
        
        self.gentool_desc_lbl = Gtk.Label(label=self.tr("gentool_desc"))
        self.gentool_desc_lbl.get_style_context().add_class("text-desc")
        self.gentool_desc_lbl.set_xalign(0)
        self.gentool_desc_lbl.set_line_wrap(True)
        self.gentool_desc_lbl.set_margin_top(20)
        page_box.pack_start(self.gentool_desc_lbl, False, False, 0)
        
        self.btn_gentool = Gtk.Button(label="INSTALL GENTOOL")
        self.btn_gentool.get_style_context().add_class("btn-accent")
        self.btn_gentool.set_margin_top(35)
        self.btn_gentool.set_halign(Gtk.Align.START)
        self.btn_gentool.connect("clicked", self.install_gentool)
        page_box.pack_start(self.btn_gentool, False, False, 0)

    def install_gentool(self, button):
        if self._busy:
            return
        self.set_busy()
        self.nav_btns["fixes"].set_active(True)
        threading.Thread(target=self._gentool_thread, daemon=True).start()

    def _gentool_thread(self):
        try:
            self.gentool_worker()
        finally:
            self.clear_busy()

    def gentool_worker(self):
        try:
            self.update_progress(20, "Starting GenTool installation...")
            self.copy_file_helper(os.path.join(OFFLINE_DIR, "d3d8.dll"), os.path.join(GAME_ROOT, "d3d8.dll"))
            if self.diagnostics["ccg_detected"]:
                self.copy_file_helper(os.path.join(OFFLINE_DIR, "d3d8.dll"), os.path.join(GENERALS_DIR, "d3d8.dll"))
                
            self.thread_log("Registering d3d8 DLL override inside Proton prefix...")
            reg_cmd = [
                "protontricks", "-c",
                "wine reg add 'HKCU\\Software\\Wine\\DllOverrides' /v d3d8 /t REG_SZ /d native,builtin /f",
                "2732960"
            ]
            subprocess.run(reg_cmd, capture_output=True, check=True)
            self.update_progress(100, "✓ GenTool installed and overrides registered!")
            GLib.idle_add(self.show_message_box, "Success", "GenTool successfully installed!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    # ==========================================
    # PAGE 3: ADDONS & TOOLS 
    # ==========================================
    def build_addons_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_margin_top(20)
        page_box.set_margin_bottom(20)
        page_box.set_margin_start(20)
        page_box.set_margin_end(20)
        self.stack.add_named(page_box, "addons")

        self.addons_title = Gtk.Label(label=self.tr("addons_title"))
        self.addons_title.get_style_context().add_class("header-title")
        self.addons_title.set_xalign(0)
        page_box.pack_start(self.addons_title, False, False, 0)

        self.addons_sub = Gtk.Label(label=self.tr("addons_subtitle"))
        self.addons_sub.get_style_context().add_class("subtitle")
        self.addons_sub.set_xalign(0)
        self.addons_sub.set_line_wrap(True)
        self.addons_sub.set_margin_bottom(12)
        page_box.pack_start(self.addons_sub, False, False, 2)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_box.pack_start(scroll, True, True, 0)

        mods_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        mods_box.set_spacing(6)
        scroll.add(mods_box)

        self.create_controlbar_row(mods_box)
        self.create_hotkeys_row(mods_box)
        self.btn_maps = self.create_mod_row(
            mods_box, "Community Map Pack",
            "1000+ skirmish, co-op and AOD challenge maps.",
            "EXTRACT MAPS", self.install_mappacks
        )
        self.btn_genlauncher = self.create_mod_row(
            mods_box, "GenLauncher Mod Manager",
            "Run Rise of the Reds, Shockwave, Operation Firestorm and more.",
            "INSTALL", self.install_genlauncher
        )
        self.btn_fonts = self.create_mod_row(
            mods_box, "Unicode Russian Font Fix",
            "Fixes Cyrillic encoding crashes on Russian game installations.",
            "INSTALL", self.install_fonts
        )

    def create_mod_row(self, parent, title, desc, btn_label, callback):
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        card.get_style_context().add_class("mod-card")
        parent.pack_start(card, False, False, 0)

        info_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        info_col.set_valign(Gtk.Align.CENTER)
        card.pack_start(info_col, True, True, 0)

        lbl_title = Gtk.Label()
        lbl_title.set_markup(f"<b>{title}</b>")
        lbl_title.get_style_context().add_class("mod-title")
        lbl_title.set_xalign(0)
        info_col.pack_start(lbl_title, False, False, 0)

        lbl_desc = Gtk.Label(label=desc)
        lbl_desc.get_style_context().add_class("subtitle")
        lbl_desc.set_xalign(0)
        lbl_desc.set_line_wrap(True)
        info_col.pack_start(lbl_desc, False, False, 0)

        btn = Gtk.Button(label=btn_label)
        btn.get_style_context().add_class("btn-secondary")
        btn.set_valign(Gtk.Align.CENTER)
        btn.connect("clicked", callback)
        card.pack_end(btn, False, False, 0)
        self._addon_buttons.append(btn)

        if callback == self.install_mappacks:
            self.lbl_maps_title = lbl_title
            self.lbl_maps_desc = lbl_desc
        elif callback == self.install_genlauncher:
            self.lbl_gl_title = lbl_title
            self.lbl_gl_desc = lbl_desc
        elif callback == self.install_fonts:
            self.lbl_font_title = lbl_title
            self.lbl_font_desc = lbl_desc

        return btn

    def create_controlbar_row(self, parent):
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        card.get_style_context().add_class("mod-card")
        parent.pack_start(card, False, False, 0)

        info_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_col.set_valign(Gtk.Align.CENTER)
        card.pack_start(info_col, True, True, 0)

        self.lbl_cb_title = Gtk.Label()
        self.lbl_cb_title.set_markup(f"<b>{self.tr('cb_title')}</b>")
        self.lbl_cb_title.get_style_context().add_class("mod-title")
        self.lbl_cb_title.set_xalign(0)
        info_col.pack_start(self.lbl_cb_title, False, False, 0)

        self.lbl_cb_desc = Gtk.Label(label=self.tr("cb_desc"))
        self.lbl_cb_desc.get_style_context().add_class("subtitle")
        self.lbl_cb_desc.set_xalign(0)
        self.lbl_cb_desc.set_line_wrap(True)
        info_col.pack_start(self.lbl_cb_desc, False, False, 0)

        res_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        res_row.set_margin_top(4)
        info_col.pack_start(res_row, False, False, 0)

        self.lbl_cb_res = Gtk.Label(label=self.tr("cb_res_label"))
        self.lbl_cb_res.get_style_context().add_class("subtitle")
        res_row.pack_start(self.lbl_cb_res, False, False, 0)

        self.hud_res_combo = Gtk.ComboBoxText()
        for key, label in [
            ("1280 720",  "1280×720"),
            ("1600 900",  "1600×900"),
            ("1920 1080", "1920×1080"),
            ("2560 1440", "2560×1440"),
            ("3840 2160", "3840×2160 (4K)"),
        ]:
            self.hud_res_combo.append(key, label)
        self.hud_res_combo.set_active_id("1920 1080")
        self.hud_res_combo.set_valign(Gtk.Align.CENTER)
        res_row.pack_start(self.hud_res_combo, False, False, 0)

        self.btn_hud = Gtk.Button(label="INSTALL HUD")
        self.btn_hud.get_style_context().add_class("btn-secondary")
        self.btn_hud.set_valign(Gtk.Align.CENTER)
        self.btn_hud.connect("clicked", self.install_controlbar)
        card.pack_end(self.btn_hud, False, False, 0)
        self._addon_buttons.append(self.btn_hud)

    def create_hotkeys_row(self, parent):
        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        card.get_style_context().add_class("mod-card")
        parent.pack_start(card, False, False, 0)

        info_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.pack_start(info_col, True, True, 0)

        self.lbl_hk_title = Gtk.Label()
        self.lbl_hk_title.set_markup(f"<b>{self.tr('hk_title')}</b>")
        self.lbl_hk_title.get_style_context().add_class("mod-title")
        self.lbl_hk_title.set_xalign(0)
        info_col.pack_start(self.lbl_hk_title, False, False, 0)

        self.lbl_hk_desc = Gtk.Label(label=self.tr("hk_desc"))
        self.lbl_hk_desc.get_style_context().add_class("subtitle")
        self.lbl_hk_desc.set_xalign(0)
        self.lbl_hk_desc.set_line_wrap(True)
        info_col.pack_start(self.lbl_hk_desc, False, False, 0)

        leikeze_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        leikeze_row.set_margin_top(6)
        info_col.pack_start(leikeze_row, False, False, 0)

        self.r_leikeze = Gtk.RadioButton.new_with_label(None, self.tr("hk_leikeze"))
        self.r_group = [self.r_leikeze]
        leikeze_row.pack_start(self.r_leikeze, False, False, 0)

        self.lbl_hk_lang = Gtk.Label(label=self.tr("hk_lang"))
        self.lbl_hk_lang.get_style_context().add_class("subtitle")
        leikeze_row.pack_start(self.lbl_hk_lang, False, False, 0)

        self.cb_lang = Gtk.ComboBoxText()
        self.cb_lang.append_text("English")
        self.cb_lang.append_text("German")
        self.cb_lang.append_text("Russian")
        self.cb_lang.set_active(0)
        self.cb_lang.set_valign(Gtk.Align.CENTER)
        leikeze_row.pack_start(self.cb_lang, False, False, 0)

        self.r_legionnaire = Gtk.RadioButton.new_with_label_from_widget(self.r_leikeze, self.tr("hk_legionnaire"))
        info_col.pack_start(self.r_legionnaire, False, False, 0)

        self.r_default = Gtk.RadioButton.new_with_label_from_widget(self.r_leikeze, self.tr("hk_default"))
        info_col.pack_start(self.r_default, False, False, 0)

        self.cb_show_visual = Gtk.CheckButton.new_with_label(self.tr("hk_visual"))
        self.cb_show_visual.get_style_context().add_class("text-desc")
        self.cb_show_visual.get_child().set_line_wrap(True)
        self.cb_show_visual.set_active(True)
        self.cb_show_visual.set_margin_top(4)
        info_col.pack_start(self.cb_show_visual, False, False, 0)

        self.btn_hotkeys = Gtk.Button(label="APPLY HOTKEYS")
        self.btn_hotkeys.get_style_context().add_class("btn-secondary")
        self.btn_hotkeys.set_valign(Gtk.Align.START)
        self.btn_hotkeys.set_margin_top(4)
        self.btn_hotkeys.connect("clicked", self.apply_hotkeys)
        card.pack_end(self.btn_hotkeys, False, False, 0)
        self._addon_buttons.append(self.btn_hotkeys)

    def run_worker_thread(self, target_func):
        if self._busy:
            return
        self.set_busy()
        self.nav_btns["fixes"].set_active(True)
        def _run():
            try:
                target_func()
            finally:
                self.clear_busy()
        threading.Thread(target=_run, daemon=True).start()

    def install_genlauncher(self, button):
        self.run_worker_thread(self.genlauncher_worker)

    def genlauncher_worker(self):
        try:
            self.update_progress(20, "Installing GenLauncher Mod Manager...")
            self.copy_file_helper(os.path.join(OFFLINE_DIR, "GenLauncher.exe"), os.path.join(GAME_ROOT, "GenLauncher.exe"))
            self.update_progress(100, "✓ GenLauncher installed successfully!")
            GLib.idle_add(self.show_message_box, "Success", "GenLauncher installed successfully!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def install_controlbar(self, button):
        self.run_worker_thread(self.controlbar_worker)

    def clean_loose_hud_files(self):
        loose_files = [
            "Window/ControlBar.wnd",
            "Window/ControlBarPopupDescription.wnd",
            "Window/Diplomacy.wnd",
            "Window/GeneralsExpPoints.wnd",
            "Window/GenPowersShortcutBarChina.wnd",
            "Window/GenPowersShortcutBarGLA.wnd",
            "Window/GenPowersShortcutBarUS.wnd",
            "Window/InGameChat.wnd",
            "Window/Menus/Defeat.wnd",
            "Window/Menus/DisconnectScreen.wnd",
            "Window/Menus/GameSpyGameOptionsMenu.wnd",
            "Window/Menus/GameSpyLoginProfile.wnd_hidemail",
            "Window/Menus/LanGameOptionsMenu.wnd",
            "Window/Menus/LocalDefeat.wnd",
            "Window/Menus/MessageBox.wnd",
            "Window/Menus/NetworkDirectConnect.wnd_hideip",
            "Window/Menus/ObserverQuit.wnd",
            "Window/Menus/OptionsMenu.wnd_hideip",
            "Window/Menus/PopupBuddyListNotification.wnd",
            "Window/Menus/QuitMenu.wnd",
            "Window/Menus/QuitMessageBox.wnd",
            "Window/Menus/QuitNoSave.wnd",
            "Window/Menus/SkirmishGameOptionsMenu.wnd",
            "Window/Menus/Victorious.wnd",
            "Window/ReplayControl.wnd",
            "Data/INI/ControlBarScheme.ini",
            "Data/INI/InGameUI.ini",
            "Data/INI/MappedImages/HandCreated/AmericaCommandBarPro.ini",
            "Data/INI/MappedImages/HandCreated/AmericaPowersPro.ini",
            "Data/INI/MappedImages/HandCreated/BlankTexture.ini",
            "Data/INI/MappedImages/HandCreated/ChinaCommandBarPro.ini",
            "Data/INI/MappedImages/HandCreated/ChinaPowersPro.ini",
            "Data/INI/MappedImages/HandCreated/ControlBarProCommon.ini",
            "Data/INI/MappedImages/HandCreated/DiplomacyWindowPro.ini",
            "Data/INI/MappedImages/HandCreated/DisconnectWindowPro.ini",
            "Data/INI/MappedImages/HandCreated/GlaCommandBarPro.ini",
            "Data/INI/MappedImages/HandCreated/GlaPowersPro.ini",
            "Data/INI/MappedImages/HandCreated/ObsCommandBarPro.ini",
            "Data/INI/MappedImages/HandCreated/QuitWindowPro.ini",
            "GenTool/fullviewport.dat"
        ]
        for f in loose_files:
            path = os.path.join(GAME_ROOT, f)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    self.thread_log(f"✓ Removed loose layout file: {f}")
                except Exception as e:
                    self.thread_log(f"Warning: Could not remove {f}: {str(e)}")

    def controlbar_worker(self):
        try:
            self.update_progress(5, "Cleaning up old Control Bar Pro files...")
            
            for f in os.listdir(GAME_ROOT):
                if f.startswith("340_ControlBarPro") and f.endswith(".big"):
                    try:
                        os.remove(os.path.join(GAME_ROOT, f))
                        self.thread_log(f"✓ Removed: {f}")
                    except:
                        pass
            self.clean_loose_hud_files()

            self.update_progress(15, "Reading selected resolution...")
            res_str = self.hud_res_combo.get_active_id() or "1920 1080"

            url_map = {
                "1280 720":  "https://www.dropbox.com/scl/fi/vmvmsmopmo8950ydw8h5m/ControlBarProZH_v1.0.3_-Competitive_Edition_By_ExiLe-_1280x720.zip?rlkey=glv48u38qz1mca632sva8d6fz&st=seat43dc&dl=1",
                "1600 900":  "https://www.dropbox.com/scl/fi/8qqy2mm8ybmdfoq9zgbqw/ControlBarProZH_v1.0.3_-Competitive_Edition_By_ExiLe-_1600x900.zip?rlkey=cy06z2mtpuudfac0lij3zlwc2&st=h7ix3z0m&dl=1",
                "1920 1080": "https://www.dropbox.com/scl/fi/64jse2tf7tq6q9anhuaes/ControlBarProZH_v1.0.3_-Competitive_Edition_By_ExiLe-_1920x1080.zip?rlkey=0rvcso4j71vhjuczi07irydjl&st=9s9casxi&dl=1",
                "2560 1440": "https://tinyurl.com/exilecontrolbar2560x1440",
                "3840 2160": "https://tinyurl.com/exilecontrolbar3840x2160",
            }

            download_url = None
            matched_res = None
            for res_key, url in url_map.items():
                if res_key in res_str:
                    download_url = url
                    matched_res = res_key
                    break

            if not download_url:
                download_url = url_map["1920 1080"]
                matched_res = "1920 1080"
                self.thread_log("Resolution not matched exactly, falling back to 1920x1080.")

            self.thread_log(f"✓ Matched resolution: {matched_res}. Downloading ControlBarPro...")
            self.update_progress(30, f"Downloading Control Bar Pro ({matched_res.replace(' ', 'x')})...")

            zip_path = os.path.join(GAME_ROOT, "_cbpr_download.zip")
            result = subprocess.run(
                ["curl", "-sL", "--output", zip_path, download_url],
                capture_output=True
            )
            if result.returncode != 0 or not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1024:
                self.update_progress(0, "Error: Failed to download ControlBarPro zip.")
                return

            self.thread_log("✓ Download complete.")
            self.update_progress(70, "Extracting ControlBarPro files to game folder...")

            extract_result = subprocess.run(
                ["unzip", "-o", zip_path, "-d", GAME_ROOT],
                capture_output=True, text=True
            )
            os.remove(zip_path)

            if extract_result.returncode != 0:
                self.thread_log(f"Warning: unzip stderr: {extract_result.stderr.strip()}")
                self.update_progress(0, "Error: Failed to extract ControlBarPro zip.")
                return

            self.thread_log("✓ ControlBarPro files extracted to game folder.")
            self.update_progress(100, "✓ Control Bar Pro HUD installed successfully!")
            GLib.idle_add(self.show_message_box, "Success", f"Control Bar Pro HUD ({matched_res.replace(' ', 'x')}) successfully installed!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def install_mappacks(self, button):
        self.run_worker_thread(self.mappacks_worker)

    def mappacks_worker(self):
        try:
            self.update_progress(10, "Extracting community maps...")
            map_archives = ["maod", "mmis", "mscr", "mskr"]
            for idx, arch in enumerate(map_archives):
                pct = 15 + idx * 20
                arch_path = os.path.join(OFFLINE_DIR, arch)
                if os.path.exists(arch_path):
                    self.update_progress(pct, f"Extracting map package: {arch}...")
                    self.extract_map_pack_worker(arch_path)
            self.update_progress(100, "✓ All Map Packs extracted successfully!")
            GLib.idle_add(self.show_message_box, "Success", "All Map Packs successfully extracted!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def install_fonts(self, button):
        self.run_worker_thread(self.fonts_worker)

    def fonts_worker(self):
        try:
            self.update_progress(20, "Extracting Russian Font Fixes...")
            temp_font_dir = "/tmp/gena_extract"
            if os.path.exists(temp_font_dir):
                shutil.rmtree(temp_font_dir)
            os.makedirs(temp_font_dir, exist_ok=True)
            
            if self.extract_worker_7z(os.path.join(OFFLINE_DIR, "gena"), temp_font_dir):
                self.copy_file_helper(os.path.join(temp_font_dir, "822_GenArial.big"), os.path.join(GAME_ROOT, "822_GenArial.big"))
                if self.diagnostics["ccg_detected"]:
                    self.copy_file_helper(os.path.join(temp_font_dir, "822_GenArial.big"), os.path.join(GENERALS_DIR, "822_GenArial.big"))
                    
            if os.path.exists(temp_font_dir):
                shutil.rmtree(temp_font_dir)
            self.update_progress(100, "✓ Russian Font patch installed successfully!")
            GLib.idle_add(self.show_message_box, "Success", "Russian Font patches applied!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def apply_hotkeys(self, button):
        if self.r_default.get_active():
            profile = "default"
        elif self.r_legionnaire.get_active():
            profile = "legionnaire"
        else:
            profile = "leikeze"
            
        lang = self.cb_lang.get_active_text()
        show_visual = self.cb_show_visual.get_active()
        
        self.run_worker_thread(lambda: self.hotkeys_worker(profile, lang, show_visual))

    def hotkeys_worker(self, profile, lang, show_visual):
        try:
            self.update_progress(20, "Applying selected Hotkey Control Profile...")
            lang_map = {
                "English": "BIG EN",
                "German": "BIG DE",
                "Russian": "BIG RU"
            }
            lang_folder = lang_map.get(lang, "BIG EN")
            diag = self.diagnostics
            
            if profile == "default":
                self.update_progress(45, "Restoring Default EA Hotkeys...")
                default_csf = os.path.join(OFFLINE_DIR, "BIG/Data/English/generals.csf")
                self.copy_file_helper(default_csf, os.path.join(GAME_ROOT, "Data/English/generals.csf"))
                if diag["ccg_detected"]:
                    self.copy_file_helper(default_csf, os.path.join(GENERALS_DIR, "Data/English/generals.csf"))
                    
            elif profile == "leikeze":
                self.update_progress(45, f"Applying Leikeze's Grid Hotkeys ({lang})...")
                zh_src = os.path.join(OFFLINE_DIR, f"hlei_FILES/ZH/{lang_folder}/Data/English/generals.csf")
                if os.path.exists(zh_src):
                    self.copy_file_helper(zh_src, os.path.join(GAME_ROOT, "Data/English/generals.csf"))
                if diag["ccg_detected"]:
                    ccg_src = os.path.join(OFFLINE_DIR, "hlei_FILES/CCG/BIG EN/Data/English/generals.csf")
                    if os.path.exists(ccg_src):
                        self.copy_file_helper(ccg_src, os.path.join(GENERALS_DIR, "Data/English/generals.csf"))
                        
            elif profile == "legionnaire":
                self.update_progress(45, "Applying Legionnaire's custom Hotkeys...")
                temp_dir = "/tmp/hleg_extract"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                
                if self.extract_worker_7z(os.path.join(OFFLINE_DIR, "hleg"), temp_dir):
                    csf_src = os.path.join(temp_dir, "BIG/Data/English/generals.csf")
                    self.copy_file_helper(csf_src, os.path.join(GAME_ROOT, "Data/English/generals.csf"))
                    if diag["ccg_detected"]:
                        self.copy_file_helper(csf_src, os.path.join(GENERALS_DIR, "Data/English/generals.csf"))
                        
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

            if show_visual:
                self.update_progress(80, "Applying visual control bar hotkey letters...")
                self.install_visual_hotkeys(diag)
            else:
                self.update_progress(80, "Removing visual control bar hotkey letters...")
                self.remove_visual_hotkeys(diag)
                    
            self.update_progress(100, "✓ Hotkeys and visual layout settings applied!")
            GLib.idle_add(self.show_message_box, "Success", "Hotkey profile successfully applied!")
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")

    def install_visual_hotkeys(self, diag):
        self.thread_log("Installing visual hotkey overlays...")
        
        temp_dir = "/tmp/genpatcher_gtk_hlen_extract"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        src_hlen = os.path.join(OFFLINE_DIR, "hlen_FILES")
        if not os.path.exists(src_hlen):
            self.thread_log("Warning: hlen_FILES not found in offline resources.")
            return
            
        shutil.copytree(src_hlen, os.path.join(temp_dir, "hlen_FILES"))
        
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in [".webp", ".avif"]:
                    src_path = os.path.join(root, f)
                    dest_tga_name = os.path.splitext(f)[0] + ".tga"
                    dest_tga_path = os.path.join(root, dest_tga_name)
                    
                    cmd = ["convert", src_path, dest_tga_path]
                    res = subprocess.run(cmd, capture_output=True)
                    if res.returncode == 0:
                        os.remove(src_path)
                    else:
                        self.thread_log(f"Warning: Failed to convert overlay texture {f} to TGA.")
                        
        zh_src = os.path.join(temp_dir, "hlen_FILES/ZH/BIG")
        if os.path.exists(zh_src):
            self.copy_recursive_helper(zh_src, GAME_ROOT)
            self.thread_log("✓ Applied ZH visual hotkeys overlay.")
        else:
            self.thread_log("Warning: hlen_FILES/ZH/BIG not found in staging.")
            
        if diag["ccg_detected"]:
            ccg_src = os.path.join(temp_dir, "hlen_FILES/CCG/BIG")
            if os.path.exists(ccg_src):
                self.copy_recursive_helper(ccg_src, GENERALS_DIR)
                self.thread_log("✓ Applied CCG visual hotkeys overlay.")
            else:
                self.thread_log("Warning: hlen_FILES/CCG/BIG not found in staging.")
                
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    def remove_visual_hotkeys(self, diag):
        self.thread_log("Removing visual hotkey overlays...")
        zh_files = [
            "Data/INI/CommandButton.ini",
            "Data/INI/MappedImages/TextureSize_512/SAUserInterface512.INI",
            "Data/INI/MappedImages/TextureSize_512/SNUserInterface512.INI",
            "Data/INI/MappedImages/TextureSize_512/SSUserInterface512.INI",
            "Data/INI/MappedImages/TextureSize_512/SUUserInterface512.INI",
            "Data/English/Art/Textures/SAUserInterface512_001.tga",
            "Data/English/Art/Textures/SAUserInterface512_002.tga",
            "Data/English/Art/Textures/SAUserInterface512_003.tga",
            "Data/English/Art/Textures/SAUserInterface512_004.tga",
            "Data/English/Art/Textures/SAUserInterface512_005.tga",
            "Data/English/Art/Textures/SNUserInterface512_003.tga",
            "Data/English/Art/Textures/SNUserInterface512_004.tga",
            "Data/English/Art/Textures/SSUserInterface512_001.tga",
            "Data/English/Art/Textures/SSUserInterface512_002.tga",
            "Data/English/Art/Textures/SUUserInterface512_001.tga",
            "Data/English/Art/Textures/SUUserInterface512_003.tga",
            "Data/English/Art/Textures/SUUserInterface512_004.tga"
        ]
        for f in zh_files:
            path = os.path.join(GAME_ROOT, f)
            if os.path.exists(path):
                os.remove(path)
                self.thread_log(f"✓ Removed ZH: {f}")
                
        if diag["ccg_detected"]:
            ccg_files = [
                "Data/INI/CommandButton.ini",
                "Data/INI/MappedImages/TextureSize_512/SAUserInterface512.INI",
                "Art/Textures/sauserinterface512_002.tga",
                "Art/Textures/sauserinterface512_003.tga",
                "Art/Textures/snuserinterface512_002.tga",
                "Art/Textures/snuserinterface512_003.tga",
                "Art/Textures/ssuserinterface512_001.tga",
                "Art/Textures/suuserinterface512_002.tga",
                "Art/Textures/suuserinterface512_003.tga"
            ]
            for f in ccg_files:
                path = os.path.join(GENERALS_DIR, f)
                if os.path.exists(path):
                    os.remove(path)
                    self.thread_log(f"✓ Removed CCG: {f}")

    # PAGE 4: ABOUT / INFO
    def build_about_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page_box.set_margin_top(20)
        page_box.set_margin_bottom(20)
        page_box.set_margin_start(20)
        page_box.set_margin_end(20)
        self.stack.add_named(page_box, "about")
        
        self.about_title = Gtk.Label(label=self.tr("about_title"))
        self.about_title.get_style_context().add_class("header-title")
        self.about_title.set_xalign(0)
        page_box.pack_start(self.about_title, False, False, 0)
        
        self.about_sub = Gtk.Label(label=self.tr("about_subtitle"))
        self.about_sub.get_style_context().add_class("subtitle")
        self.about_sub.set_xalign(0)
        self.about_sub.set_line_wrap(True)
        page_box.pack_start(self.about_sub, False, False, 2)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_box.get_style_context().add_class("card-panel")
        info_box.set_margin_top(15)
        page_box.pack_start(info_box, False, False, 0)
        
        self.about_desc_lbl = Gtk.Label(label=self.tr("about_desc"))
        self.about_desc_lbl.get_style_context().add_class("text-desc")
        self.about_desc_lbl.set_xalign(0)
        self.about_desc_lbl.set_line_wrap(True)
        info_box.pack_start(self.about_desc_lbl, False, False, 0)
        
        self.btn_github = Gtk.Button()
        self.btn_github.get_style_context().add_class("btn-secondary")
        self.btn_github.connect("clicked", lambda b: subprocess.Popen(["xdg-open", "https://github.com/ZeNx98/GenPatcher-Linux"]))
        box_github = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_github.set_halign(Gtk.Align.CENTER)
        img_github = Gtk.Image.new_from_icon_name("go-home-symbolic", Gtk.IconSize.BUTTON)
        self.lbl_github = Gtk.Label(label=self.tr("btn_github"))
        box_github.pack_start(img_github, False, False, 0)
        box_github.pack_start(self.lbl_github, False, False, 0)
        self.btn_github.add(box_github)
        
        self.btn_go = Gtk.Button()
        self.btn_go.get_style_context().add_class("btn-secondary")
        self.btn_go.connect("clicked", lambda b: subprocess.Popen(["xdg-open", "https://playgenerals.online/"]))
        box_go = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_go.set_halign(Gtk.Align.CENTER)
        img_go = Gtk.Image.new_from_icon_name("applications-internet-symbolic", Gtk.IconSize.BUTTON)
        self.lbl_go = Gtk.Label(label=self.tr("btn_generals_online"))
        box_go.pack_start(img_go, False, False, 0)
        box_go.pack_start(self.lbl_go, False, False, 0)
        self.btn_go.add(box_go)
        
        self.btn_gt = Gtk.Button()
        self.btn_gt.get_style_context().add_class("btn-secondary")
        self.btn_gt.connect("clicked", lambda b: subprocess.Popen(["xdg-open", "https://www.gentool.net/"]))
        box_gt = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_gt.set_halign(Gtk.Align.CENTER)
        img_gt = Gtk.Image.new_from_icon_name("system-run-symbolic", Gtk.IconSize.BUTTON)
        self.lbl_gt = Gtk.Label(label=self.tr("btn_gentool_page"))
        box_gt.pack_start(img_gt, False, False, 0)
        box_gt.pack_start(self.lbl_gt, False, False, 0)
        self.btn_gt.add(box_gt)
        
        self.btn_gp = Gtk.Button()
        self.btn_gp.get_style_context().add_class("btn-secondary")
        self.btn_gp.connect("clicked", lambda b: subprocess.Popen(["xdg-open", "https://legi.cc/genpatcher"]))
        box_gp = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_gp.set_halign(Gtk.Align.CENTER)
        img_gp = Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON)
        self.lbl_gp = Gtk.Label(label=self.tr("btn_genpatcher_page"))
        box_gp.pack_start(img_gp, False, False, 0)
        box_gp.pack_start(self.lbl_gp, False, False, 0)
        self.btn_gp.add(box_gp)

        self.links_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.links_box.set_margin_top(15)
        self.links_box.pack_start(self.btn_github, True, True, 0)
        self.links_box.pack_start(self.btn_go, True, True, 0)
        self.links_box.pack_start(self.btn_gt, True, True, 0)
        self.links_box.pack_start(self.btn_gp, True, True, 0)
        page_box.pack_start(self.links_box, False, False, 0)

    def on_gui_lang_changed(self, combo):
        global CURRENT_LANG
        active_id = combo.get_active_id()
        if active_id:
            CURRENT_LANG = active_id
            self.update_gui_texts()

    def update_gui_texts(self):
        is_rtl = CURRENT_LANG == "ar"
        direction = Gtk.TextDirection.RTL if is_rtl else Gtk.TextDirection.LTR
        self.set_direction(direction)
        self.set_direction_recursive(self, direction)

        sc = self.sidebar_box.get_style_context()
        if is_rtl:
            sc.add_class("rtl")
        else:
            sc.remove_class("rtl")

        if is_rtl:
            self.logo_box_ref.set_margin_start(15)
            self.logo_box_ref.set_margin_end(0)
            self.logo_box_ref.set_halign(Gtk.Align.START)
            self.ver_lbl.set_margin_start(15)
            self.ver_lbl.set_margin_end(0)
            self.ver_lbl.set_halign(Gtk.Align.START)
            self.ver_lbl.set_xalign(1)
            self.lang_lbl.set_margin_start(15)
            self.lang_lbl.set_margin_end(0)
            self.lang_lbl.set_halign(Gtk.Align.START)
            self.lang_lbl.set_xalign(1)
        else:
            self.logo_box_ref.set_margin_start(15)
            self.logo_box_ref.set_margin_end(0)
            self.logo_box_ref.set_halign(Gtk.Align.START)
            self.ver_lbl.set_margin_start(15)
            self.ver_lbl.set_margin_end(0)
            self.ver_lbl.set_halign(Gtk.Align.START)
            self.ver_lbl.set_xalign(0)
            
            self.lang_lbl.set_margin_start(15)
            self.lang_lbl.set_margin_end(0)
            self.lang_lbl.set_halign(Gtk.Align.START)
            self.lang_lbl.set_xalign(0)

        self.ver_lbl.set_text(self.tr("ver_label"))
        self.lang_lbl.set_text(self.tr("lang_label"))

        self.nav_btns["fixes"].set_label(self.tr("apply_fixes"))
        self.nav_btns["gentool"].set_label(self.tr("gentool"))
        self.nav_btns["addons"].set_label(self.tr("addons"))
        self.nav_btns["about"].set_label(self.tr("about"))

        self.fixes_title.set_text(self.tr("fixes_title"))
        self.fixes_sub.set_text(self.tr("fixes_subtitle"))
        self.btn_locate.set_label(self.tr("btn_locate"))
        self.btn_open_game.set_label(self.tr("btn_open"))
        self.btn_open_prefix.set_label(self.tr("btn_open"))
        self.btn_check_update.set_label(self.tr("btn_check_update"))
        self.load_diagnostics()

        self.gentool_title.set_text(self.tr("gentool_title"))
        self.gentool_sub.set_text(self.tr("gentool_subtitle"))
        self.gentool_desc_lbl.set_text(self.tr("gentool_desc"))

        self.addons_title.set_text(self.tr("addons_title"))
        self.addons_sub.set_text(self.tr("addons_subtitle"))
        self.lbl_cb_title.set_markup(f"<b>{self.tr('cb_title')}</b>")
        self.lbl_cb_desc.set_text(self.tr("cb_desc"))
        self.lbl_cb_res.set_text(self.tr("cb_res_label"))

        self.lbl_hk_title.set_markup(f"<b>{self.tr('hk_title')}</b>")
        self.lbl_hk_desc.set_text(self.tr("hk_desc"))
        self.r_leikeze.set_label(self.tr("hk_leikeze"))
        self.lbl_hk_lang.set_text(self.tr("hk_lang"))
        self.r_legionnaire.set_label(self.tr("hk_legionnaire"))
        self.r_default.set_label(self.tr("hk_default"))
        self.cb_show_visual.set_label(self.tr("hk_visual"))

        _xalign = 1 if is_rtl else 0
        for widget in (self.r_leikeze, self.r_legionnaire, self.r_default, self.cb_show_visual):
            child = widget.get_child()
            if child:
                child.set_xalign(_xalign)

        self.lbl_maps_title.set_markup(f"<b>{self.tr('maps_title')}</b>")
        self.lbl_maps_desc.set_text(self.tr("maps_desc"))

        self.lbl_gl_title.set_markup(f"<b>{self.tr('gl_title')}</b>")
        self.lbl_gl_desc.set_text(self.tr("gl_desc"))

        self.lbl_font_title.set_markup(f"<b>{self.tr('font_title')}</b>")
        self.lbl_font_desc.set_text(self.tr("font_desc"))


        self.about_title.set_text(self.tr("about_title"))
        self.about_sub.set_text(self.tr("about_subtitle"))
        self.about_desc_lbl.set_text(self.tr("about_desc"))
        self.lbl_github.set_text(self.tr("btn_github"))
        self.lbl_go.set_text(self.tr("btn_generals_online"))
        self.lbl_gt.set_text(self.tr("btn_gentool_page"))
        self.lbl_gp.set_text(self.tr("btn_genpatcher_page"))

    def set_direction_recursive(self, widget, direction):
        widget.set_direction(direction)
        if hasattr(widget, "get_children"):
            for child in widget.get_children():
                self.set_direction_recursive(child, direction)

# ==========================================
# DIAGNOSTICS & IO STATICS
# ==========================================
def backup_file(filepath):
    if os.path.exists(filepath):
        backup_path = filepath + ".original_backup"
        if not os.path.exists(backup_path):
            if os.path.islink(filepath):
                target = os.readlink(filepath)
                with open(backup_path, "w") as f:
                    f.write(f"SYMLINK_TO: {target}\n")
            else:
                shutil.copy2(filepath, backup_path)

def check_paths():
    online_exe_exists = False
    gentool_exists = False
    genlauncher_exists = False
    hud_exists = False
    maps_exists = False
    font_fix_exists = False
    hotkeys_applied = False
    
    if GAME_ROOT:
        online_exe_exists = (
            os.path.exists(os.path.join(GAME_ROOT, "GeneralsOnlineZH.exe")) or
            os.path.exists(os.path.join(GAME_ROOT, "GeneralsOnline.exe"))
        )
        gentool_exists = os.path.exists(os.path.join(GAME_ROOT, "d3d8.dll"))
        genlauncher_exists = os.path.exists(os.path.join(GAME_ROOT, "GenLauncher.exe"))
        try:
            hud_exists = any(f.startswith("340_ControlBarPro") and f.endswith(".big") for f in os.listdir(GAME_ROOT))
        except:
            hud_exists = False
        font_fix_exists = os.path.exists(os.path.join(GAME_ROOT, "822_GenArial.big"))
        hotkeys_applied = os.path.exists(os.path.join(GAME_ROOT, "Data/English/generals.csf"))

    if ZH_DOCS_DATA:
        try:
            maps_exists = os.path.exists(os.path.join(ZH_DOCS_DATA, "Maps")) and len(os.listdir(os.path.join(ZH_DOCS_DATA, "Maps"))) > 0
        except:
            maps_exists = False

    return {
        "game_detected": os.path.exists(GAME_ROOT) if GAME_ROOT else False,
        "prefix_detected": os.path.exists(PREFIX_DIR) if PREFIX_DIR else False,
        "offline_files_detected": os.path.exists(OFFLINE_DIR),
        "game_path": GAME_ROOT,
        "prefix_path": PREFIX_DIR,
        "offline_path": OFFLINE_DIR,
        "ccg_detected": os.path.exists(GENERALS_DIR) if GENERALS_DIR else False,
        "fixes_applied": online_exe_exists,
        "gentool_installed": gentool_exists,
        "genlauncher_installed": genlauncher_exists,
        "hud_installed": hud_exists,
        "maps_installed": maps_exists,
        "fonts_installed": font_fix_exists,
        "hotkeys_applied": hotkeys_applied,
    }

def get_current_settings():
    settings = {
        "zh_resolution": "1920 1080",
        "ccg_resolution": "1920 1080",
        "zh_edge_scroll": False,
        "ccg_edge_scroll": False,
    }
    zh_ini = os.path.join(ZH_DOCS_DATA, "Options.ini")
    if os.path.exists(zh_ini):
        with open(zh_ini, "r") as f:
            for line in f:
                if "Resolution =" in line:
                    settings["zh_resolution"] = line.split("=", 1)[1].strip()
                if "ScreenEdgeScrollEnabledInFullscreenApp = yes" in line:
                    settings["zh_edge_scroll"] = True
    return settings

def update_options_ini(file_path, resolution, edge_scroll):
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = f"""AntiAliasing = 4
ArchiveReplays = no
DrawScrollAnchor = no
Gamma = 50
IdealStaticGameLOD = High
LanguageFilter = false
MoneyTransactionVolume = 0
MoveScrollAnchor = no
MusicVolume = 55
Resolution = {resolution}
Retaliation = yes
SFX3DVolume = 79
SFXVolume = 71
ScreenEdgeScrollEnabledInFullscreenApp = {"yes" if edge_scroll else "no"}
ScreenEdgeScrollEnabledInWindowedApp = {"yes" if edge_scroll else "no"}
ScrollFactor = 50
StaticGameLOD = VeryHigh
VoiceVolume = 70
"""
        with open(file_path, "w") as f:
            f.write(content)
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    keys_to_set = {
        "Resolution": resolution,
        "ScreenEdgeScrollEnabledInFullscreenApp": "yes" if edge_scroll else "no",
        "ScreenEdgeScrollEnabledInWindowedApp": "yes" if edge_scroll else "no",
        "CursorCaptureEnabledInFullscreenGame": "yes" if edge_scroll else "no",
        "CursorCaptureEnabledInWindowedGame": "yes" if edge_scroll else "no",
    }
    seen_keys = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(";"):
            new_lines.append(line)
            continue
        
        parts = stripped.split("=", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            if key in keys_to_set:
                new_lines.append(f"{key} = {keys_to_set[key]}\n")
                seen_keys.add(key)
                modified = True
                continue
        new_lines.append(line)

    for key, val in keys_to_set.items():
        if key not in seen_keys:
            new_lines.append(f"{key} = {val}\n")
            modified = True

    if modified:
        with open(file_path, "w") as f:
            f.writelines(new_lines)

if __name__ == "__main__":
    app = GenPatcherGTK()
    app.show_all()
    Gtk.main()
