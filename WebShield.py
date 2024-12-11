import os
import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QAction, QMessageBox,
    QDialog, QVBoxLayout, QLabel, QTabWidget, QInputDialog, QLineEdit, QFileDialog, QPushButton, QToolBar, QComboBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import QIcon


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        ad_keywords = ["ads", "tracker", "doubleclick", "adservice"]
        if any(keyword in url for keyword in ad_keywords):
            info.block(True)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebShield: A Secure Web Browser")
        self.setGeometry(100, 100, 1024, 768)

        # Browser State
        self.is_dark_mode = False
        self.incognito_mode = False
        self.bookmarks_file = "bookmarks.txt"
        self.bookmarks = self.load_bookmarks()
        self.history = []
        self.search_engine = "https://www.google.com"
        self.pin_code = None
        self.adblocker = None

        # Browser Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_tab_title)
        self.setCentralWidget(self.tabs)

        # Add default tab
        self.add_new_tab(QUrl("https://www.google.com"), "Homepage")

        # UI Components
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

    def create_toolbar(self):
        toolbar = QToolBar("Navigation")
        self.addToolBar(toolbar)

        # Back Button
        back_btn = QAction(QIcon('icons/back.png'), 'Back', self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        toolbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction(QIcon('icons/forward.png'), 'Forward', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        toolbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction(QIcon('icons/reload.png'), 'Reload', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction(QIcon('icons/home.png'), 'Home', self)
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        # Address Bar
        self.address_bar = QLineEdit(self)
        self.address_bar.setPlaceholderText("Enter URL here...")
        self.address_bar.returnPressed.connect(self.load_url_from_address_bar)
        toolbar.addWidget(self.address_bar)

        # Bookmark Button
        bookmark_btn = QAction(QIcon('icons/bookmark.png'), 'Bookmark', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        toolbar.addAction(bookmark_btn)

        # Incognito Button
        incognito_btn = QAction(QIcon('icons/incognito.png'), 'Incognito', self)
        incognito_btn.triggered.connect(self.toggle_incognito)
        toolbar.addAction(incognito_btn)

        # Search Engine Dropdown
        self.search_dropdown = QComboBox(self)
        self.search_dropdown.addItem("Google", "https://www.google.com")
        self.search_dropdown.addItem("Bing", "https://www.bing.com")
        self.search_dropdown.addItem("DuckDuckGo", "https://duckduckgo.com")
        self.search_dropdown.currentIndexChanged.connect(self.change_search_engine)
        toolbar.addWidget(self.search_dropdown)

    def create_menus(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu('File')
        new_window_action = QAction('New Window', self)
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)

        save_as_pdf_action = QAction('Save Page as PDF', self)
        save_as_pdf_action.triggered.connect(self.save_page_as_pdf)
        file_menu.addAction(save_as_pdf_action)

        # View Menu
        view_menu = menu_bar.addMenu('View')
        toggle_full_screen_action = QAction('Toggle Full Screen', self)
        toggle_full_screen_action.triggered.connect(self.toggle_full_screen)
        view_menu.addAction(toggle_full_screen_action)

        toggle_dark_mode_action = QAction('Toggle Dark Mode', self)
        toggle_dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(toggle_dark_mode_action)

        # Tools Menu
        tools_menu = menu_bar.addMenu('Tools')
        bookmark_manager_action = QAction('Manage Bookmarks', self)
        bookmark_manager_action.triggered.connect(self.manage_bookmarks)
        tools_menu.addAction(bookmark_manager_action)

        clear_history_action = QAction('Clear History', self)
        clear_history_action.triggered.connect(self.clear_history)
        tools_menu.addAction(clear_history_action)

        # Privacy Menu
        privacy_menu = menu_bar.addMenu('Privacy')
        toggle_incognito_action = QAction('Toggle Incognito', self)
        toggle_incognito_action.triggered.connect(self.toggle_incognito)
        privacy_menu.addAction(toggle_incognito_action)

        set_pin_action = QAction('Set PIN', self)
        set_pin_action.triggered.connect(self.set_pin)
        privacy_menu.addAction(set_pin_action)

        enable_adblock_action = QAction('Enable Adblocker', self)
        enable_adblock_action.triggered.connect(self.enable_adblocker)
        privacy_menu.addAction(enable_adblock_action)

    def create_status_bar(self):
        self.status_bar = self.statusBar()

    # Tabs Management
    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        browser.setUrl(qurl)
        self.tabs.addTab(browser, label)
        self.tabs.setCurrentWidget(browser)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_tab_title(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            self.setWindowTitle(current_browser.title())

    # Actions
    def current_browser(self):
        return self.tabs.currentWidget()

    def load_url_from_address_bar(self):
        url = self.address_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.current_browser().setUrl(QUrl(url))

    def go_home(self):
        self.current_browser().setUrl(QUrl(self.search_engine))

    def add_bookmark(self):
        current_url = self.current_browser().url().toString()
        if current_url not in self.bookmarks:
            self.bookmarks.append(current_url)
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", f"Bookmarked: {current_url}")

    def toggle_incognito(self):
        self.incognito_mode = not self.incognito_mode
        profile = QWebEngineProfile.defaultProfile()
        if self.incognito_mode:
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        else:
            profile.setHttpCacheType(QWebEngineProfile.DefaultHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AcceptCookies)
        self.status_bar.showMessage("Incognito Mode " + ("Activated" if self.incognito_mode else "Deactivated"))

    def toggle_full_screen(self):
        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)

    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("QMainWindow { background-color: #2e2e2e; color: white; }")
        self.is_dark_mode = not self.is_dark_mode

    def change_search_engine(self, index):
        self.search_engine = self.search_dropdown.currentData()

    def manage_bookmarks(self):
        dialog = QDialog(self)
        layout = QVBoxLayout()
        for bookmark in self.bookmarks:
            layout.addWidget(QLabel(bookmark))
        dialog.setLayout(layout)
        dialog.exec_()

    def save_bookmarks(self):
        with open(self.bookmarks_file, 'w') as file:
            file.write('\n'.join(self.bookmarks))

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, 'r') as file:
                return file.read().splitlines()
        return []

    def set_pin(self):
        pin, ok = QInputDialog.getText(self, "Set PIN", "Enter a PIN:", QLineEdit.Password)
        if ok and pin:
            self.pin_code = pin
            QMessageBox.information(self, "PIN Set", "PIN has been set successfully.")

    def enable_adblocker(self):
        if not self.adblocker:
            self.adblocker = AdBlocker()
            QWebEngineProfile.defaultProfile().setRequestInterceptor(self.adblocker)
            self.status_bar.showMessage("Adblocker Enabled")

    def clear_history(self):
        self.history.clear()
        QMessageBox.information(self, "History Cleared", "Browsing history has been cleared")

    def save_page_as_pdf(self):
        current_browser = self.current_browser()
        if current_browser:
            path, _ = QFileDialog.getSaveFileName(self, "Save Page as PDF", "", "PDF Files (*.pdf)")
            if path:
                current_browser.page().printToPdf(path)
                QMessageBox.information(self, "PDF Saved", f"Page saved as PDF at {path}")

    def new_window(self):
        new_browser = Browser()
        new_browser.show()

    def check_load_status(self, success):
        if not success:
            QMessageBox.warning(self, "Error", "Failed to load the page.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("WebShield: A Secure Web Browser")
    try:
        browser = Browser()  # Correct instantiation of Browser class.
        browser.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Application Error", str(e))
        sys.exit(1)