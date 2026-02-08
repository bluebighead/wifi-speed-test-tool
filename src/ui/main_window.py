from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QStatusBar, QMenuBar, QAction, 
                             QMessageBox, QSplitter, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from src.ui.channel_analysis_panel import ChannelAnalysisPanel
from src.ui.recommend_panel import RecommendPanel
from src.utils.logger import logger
from src.utils.exception_handler import exception_handler
from src.services.config_service import config_service


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        self.setWindowTitle(f"{config_service.get_app_name()} v{config_service.get_app_version()}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        # 允许窗口大小调节
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()
    
    def _create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("视图(&V)")
        
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("刷新数据")
        refresh_action.triggered.connect(self._refresh_all)
        view_menu.addAction(refresh_action)
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于程序")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        
        self.channel_analysis_panel = ChannelAnalysisPanel()
        self.recommend_panel = RecommendPanel()
        
        self.recommend_panel.set_analysis_panel(self.channel_analysis_panel)
        
        self.tab_widget.addTab(self.channel_analysis_panel, "信道分析")
        self.tab_widget.addTab(self.recommend_panel, "信道推荐")
        
        layout.addWidget(self.tab_widget)
        
        self.channel_analysis_panel.analysis_completed.connect(self._on_analysis_completed)
    
    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _connect_signals(self):
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_tab_changed(self, index):
        tab_names = ["信道分析", "信道推荐"]
        if 0 <= index < len(tab_names):
            self.status_bar.showMessage(f"当前标签: {tab_names[index]}")
    
    def _on_analysis_completed(self, band):
        self.status_bar.showMessage(f"信道分析完成: {band}")
    
    def _refresh_all(self):
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:
            self.channel_analysis_panel.refresh()
        elif current_tab == 1:
            self.recommend_panel.refresh()
        
        self.status_bar.showMessage("已刷新")
    
    def _show_about(self):
        about_text = f"""
        <h2>{config_service.get_app_name()}</h2>
        <p>版本: {config_service.get_app_version()}</p>
        <p>一款功能完善的电脑端网络测速工具</p>
        <p>功能特点:</p>
        <ul>
            <li>信道占用分析（2.4GHz/5GHz）</li>
            <li>智能信道推荐</li>
        </ul>
        <p>开发团队: WiFi Test Team</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("关于")
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("Application closed by user")
            event.accept()
        else:
            event.ignore()
    
    def handle_error(self, message: str):
        exception_handler.show_warning("错误", message)
        self.status_bar.showMessage(f"错误: {message}")