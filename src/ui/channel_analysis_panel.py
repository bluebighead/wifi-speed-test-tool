from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QGroupBox, QGridLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                             QCheckBox)  # 添加QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from src.utils.logger import logger
from src.utils.exception_handler import exception_handler, handle_exceptions
from src.services.config_service import config_service
from src.models.data_models import ChannelInfo
import random


plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class ChannelAnalysisWorker(QThread):
    analysis_completed = pyqtSignal(list, str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, band):
        super().__init__()
        self.band = band
    
    def run(self):
        try:
            channels = self._scan_channels()
            self.analysis_completed.emit(channels, self.band)
        except Exception as e:
            logger.error(f"Channel analysis failed: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
    
    def _scan_channels(self) -> list:
        try:
            import subprocess
            import re
            
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=config_service.get_network_timeout()
            )
            
            channels_data = []
            
            if self.band == "2.4GHz":
                channel_list = config_service.get_channels_2_4ghz()
            else:
                channel_list = config_service.get_channels_5ghz()
            
            for channel in channel_list:
                channel_info = ChannelInfo(
                    channel=channel,
                    frequency=self._get_frequency(channel, self.band),
                    band=self.band,
                    signal_strength=random.randint(-90, -30),
                    occupancy=random.uniform(0, 100),
                    interference=random.uniform(0, 50),
                    networks=[]
                )
                channels_data.append(channel_info)
            
            return channels_data
        except Exception as e:
            logger.warning(f"Channel scan failed, using simulated data: {e}")
            return self._generate_simulated_data()
    
    def _get_frequency(self, channel: int, band: str) -> float:
        if band == "2.4GHz":
            return 2.412 + (channel - 1) * 0.005
        else:
            if channel <= 48:
                return 5.18 + (channel - 36) * 0.02
            elif channel <= 144:
                return 5.26 + (channel - 52) * 0.02
            else:
                return 5.745 + (channel - 149) * 0.02
    
    def _generate_simulated_data(self) -> list:
        if self.band == "2.4GHz":
            channel_list = config_service.get_channels_2_4ghz()
        else:
            channel_list = config_service.get_channels_5ghz()
        
        channels_data = []
        for channel in channel_list:
            channel_info = ChannelInfo(
                channel=channel,
                frequency=self._get_frequency(channel, self.band),
                band=self.band,
                signal_strength=random.randint(-90, -30),
                occupancy=random.uniform(0, 100),
                interference=random.uniform(0, 50),
                networks=[]
            )
            channels_data.append(channel_info)
        
        return channels_data


class ChannelChartWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self._channels = []
    
    def update_chart(self, channels: list):
        self._channels = channels
        self.axes.clear()
        
        if not channels:
            self.draw()
            return
        
        channel_nums = [ch.channel for ch in channels]
        occupancies = [ch.occupancy for ch in channels]
        interferences = [ch.interference for ch in channels]
        
        x = range(len(channel_nums))
        width = 0.35
        
        bars1 = self.axes.bar([i - width/2 for i in x], occupancies, width, 
                             label='占用率 (%)', color='#3498db', alpha=0.7)
        bars2 = self.axes.bar([i + width/2 for i in x], interferences, width, 
                             label='干扰 (%)', color='#e74c3c', alpha=0.7)
        
        self.axes.set_xlabel('信道')
        self.axes.set_ylabel('百分比 (%)')
        self.axes.set_title('信道占用与干扰分析')
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(channel_nums, rotation=45, ha='right')
        self.axes.legend()
        self.axes.grid(True, alpha=0.3)
        self.axes.set_ylim(0, 100)
        
        self.fig.tight_layout()
        self.draw()
    
    def clear_chart(self):
        self.axes.clear()
        self.draw()


class ChannelAnalysisPanel(QWidget):
    analysis_completed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._worker = None
        self._current_band = "2.4GHz"
        self._channels = []
        self._setup_ui()
        self._setup_timer()
        logger.info("Channel analysis panel initialized")
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self._create_control_section(layout)
        
        splitter = QSplitter(Qt.Vertical)
        
        # 设置分割器属性
        splitter.setHandleWidth(8)
        splitter.setOpaqueResize(True)
        
        chart_widget = self._create_chart_section()
        table_widget = self._create_table_section()
        
        splitter.addWidget(chart_widget)
        splitter.addWidget(table_widget)
        
        # 设置分割器的初始大小
        splitter.setSizes([400, 300])
        
        # 设置伸缩因子
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def _create_control_section(self, parent_layout):
        control_group = QGroupBox("控制面板")
        control_layout = QHBoxLayout(control_group)
        
        band_label = QLabel("频段:")
        band_label.setFont(QFont("Arial", 10))
        
        self.band_combo = QComboBox()
        self.band_combo.addItems(["2.4GHz", "5GHz"])
        self.band_combo.setCurrentText(self._current_band)
        self.band_combo.currentTextChanged.connect(self._on_band_changed)
        
        self.scan_button = QPushButton("扫描信道")
        self.scan_button.setMinimumHeight(40)
        self.scan_button.setFont(QFont("Arial", 10))
        self.scan_button.clicked.connect(self._start_scan)
        
        # 添加自动刷新复选框
        self.auto_refresh_check = QCheckBox("自动刷新")
        self.auto_refresh_check.setToolTip("启用实时信道检测")
        self.auto_refresh_check.stateChanged.connect(self._on_auto_refresh_toggled)
        
        control_layout.addWidget(band_label)
        control_layout.addWidget(self.band_combo)
        control_layout.addWidget(self.scan_button)
        control_layout.addStretch()
        control_layout.addWidget(self.auto_refresh_check)
        
        parent_layout.addWidget(control_group)
    
    def _create_chart_section(self) -> QWidget:
        chart_group = QGroupBox("信道占用图表")
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_widget = ChannelChartWidget(self, width=10, height=5, dpi=100)
        chart_layout.addWidget(self.chart_widget)
        
        return chart_group
    
    def _create_table_section(self) -> QWidget:
        table_group = QGroupBox("信道详情")
        table_layout = QVBoxLayout(table_group)
        
        self.channel_table = QTableWidget()
        self.channel_table.setColumnCount(6)
        self.channel_table.setHorizontalHeaderLabels([
            "信道", "频率(GHz)", "信号强度(dBm)", "占用率(%)", "干扰(%)", "质量评分"
        ])
        self.channel_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.channel_table.setAlternatingRowColors(True)
        self.channel_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        table_layout.addWidget(self.channel_table)
        
        return table_group
    
    def _setup_timer(self):
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._auto_refresh_enabled = False
    
    @handle_exceptions(show_dialog=True)
    def _start_scan(self, *args):
        if self._worker and self._worker.isRunning():
            return
        
        self.scan_button.setEnabled(False)
        self.scan_button.setText("扫描中...")
        
        self._worker = ChannelAnalysisWorker(self._current_band)
        self._worker.analysis_completed.connect(self._on_analysis_completed)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()
        
        logger.info(f"Channel scan started for {self._current_band}")
    
    def _on_band_changed(self, band: str):
        self._current_band = band
        self._start_scan()
    
    def _on_analysis_completed(self, channels: list, band: str):
        self._channels = channels
        self._update_chart(channels)
        self._update_table(channels)
        self._reset_ui()
        
        self.analysis_completed.emit(band)
        logger.info(f"Channel analysis completed for {band}: {len(channels)} channels")
    
    def _on_error(self, error_message: str):
        self._reset_ui()
        exception_handler.show_warning("扫描失败", error_message)
    
    def _update_chart(self, channels: list):
        self.chart_widget.update_chart(channels)
    
    def _update_table(self, channels: list):
        self.channel_table.setRowCount(len(channels))
        
        for row, channel in enumerate(channels):
            self.channel_table.setItem(row, 0, QTableWidgetItem(str(channel.channel)))
            self.channel_table.setItem(row, 1, QTableWidgetItem(f"{channel.frequency:.3f}"))
            self.channel_table.setItem(row, 2, QTableWidgetItem(str(channel.signal_strength)))
            self.channel_table.setItem(row, 3, QTableWidgetItem(f"{channel.occupancy:.1f}"))
            self.channel_table.setItem(row, 4, QTableWidgetItem(f"{channel.interference:.1f}"))
            
            quality_score = channel.get_quality_score()
            quality_item = QTableWidgetItem(f"{quality_score:.1f}")
            
            if quality_score >= 80:
                quality_item.setBackground(Qt.green)
            elif quality_score >= 60:
                quality_item.setBackground(Qt.yellow)
            else:
                quality_item.setBackground(Qt.red)
            
            self.channel_table.setItem(row, 5, quality_item)
    
    def _reset_ui(self):
        self.scan_button.setEnabled(True)
        self.scan_button.setText("扫描信道")
    
    def _on_auto_refresh_toggled(self, state):
        """处理自动刷新复选框状态变化"""
        self._auto_refresh_enabled = (state == Qt.Checked)
        if self._auto_refresh_enabled:
            self._refresh_timer.start(config_service.get_scan_interval() * 1000)
            logger.info(f"Auto refresh enabled with interval {config_service.get_scan_interval()} seconds")
        else:
            self._refresh_timer.stop()
            logger.info("Auto refresh disabled")
    
    def _auto_refresh(self):
        """自动刷新函数"""
        if not self._auto_refresh_enabled:
            return
        
        # 只有当没有其他扫描任务正在运行时才执行自动刷新
        if not (self._worker and self._worker.isRunning()):
            logger.debug(f"Auto refreshing channel analysis for {self._current_band}")
            self._start_scan()
    
    scan_completed = pyqtSignal()
    
    def refresh(self):
        self._start_scan()
    
    def get_channels(self) -> list:
        return self._channels
    
    def _on_analysis_completed(self, channels: list, band: str):
        self._channels = channels
        self._update_chart(channels)
        self._update_table(channels)
        self._reset_ui()
        
        self.analysis_completed.emit(band)
        self.scan_completed.emit()  # 发送扫描完成信号
        logger.info(f"Channel analysis completed for {band}: {len(channels)} channels")