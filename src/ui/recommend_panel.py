from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QGridLayout, QScrollArea,
                             QFrame, QProgressBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter, QSpinBox, QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QColor
from src.utils.logger import logger
from src.utils.exception_handler import exception_handler, handle_exceptions
from src.services.config_service import config_service
from src.models.data_models import ChannelRecommendation, ChannelInfo, ChannelTestData
from src.ui.channel_analysis_panel import ChannelAnalysisPanel
from src.ui.ui_styles import UIStyles
import random
from datetime import datetime
import statistics


class RecommendWorker(QThread):
    recommendation_completed = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, channels: list):
        super().__init__()
        self.channels = channels
    
    def run(self):
        try:
            recommendation = self._analyze_and_recommend()
            self.recommendation_completed.emit(recommendation)
        except Exception as e:
            logger.error(f"Recommendation failed: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
    
    def _analyze_and_recommend(self) -> ChannelRecommendation:
        if not self.channels:
            raise ValueError("No channel data available")
        
        test_count = config_service.get_test_count()
        
        channel_test_results = {}
        total_tests = len(self.channels) * test_count
        current_test = 0
        
        for channel_info in self.channels:
            test_data_list = []
            for i in range(test_count):
                test_data = self._perform_channel_test(channel_info)
                test_data_list.append(test_data)
                
                current_test += 1
                progress = int((current_test / total_tests) * 100)
                self.progress_updated.emit(progress)
            
            channel_test_results[channel_info.channel] = {
                'channel_info': channel_info,
                'test_data': test_data_list,
                'analysis': self._analyze_test_data(test_data_list)
            }
        
        best_channel_data = self._evaluate_channels(channel_test_results)
        best_channel_info = best_channel_data['channel_info']
        test_data = best_channel_data['test_data']
        analysis = best_channel_data['analysis']
        
        quality_score = self._calculate_weighted_score(analysis)
        
        reason, improvement = self._generate_recommendation_details(analysis, quality_score)
        
        return ChannelRecommendation(
            channel=best_channel_info.channel,
            band=best_channel_info.band,
            quality_score=quality_score,
            reason=reason,
            expected_improvement=improvement,
            test_data=test_data,
            analysis_details=analysis
        )
    
    def _perform_channel_test(self, channel_info: ChannelInfo) -> ChannelTestData:
        base_rssi = channel_info.signal_strength
        base_occupancy = channel_info.occupancy
        base_interference = channel_info.interference
        
        rssi = base_rssi + random.randint(-5, 5)
        snr = (rssi + 100) * random.uniform(0.8, 1.2)
        
        if channel_info.band == "2.4GHz":
            bandwidth = 20.0
            max_throughput = 72.2
        else:
            bandwidth = 80.0
            max_throughput = 433.3
        
        throughput_factor = 1.0 - (base_occupancy + base_interference) / 200.0
        throughput = max_throughput * throughput_factor * random.uniform(0.7, 1.0)
        
        packet_loss = (base_interference / 100.0) * random.uniform(0.5, 1.5)
        packet_loss = min(packet_loss, 10.0)
        
        return ChannelTestData(
            channel=channel_info.channel,
            band=channel_info.band,
            rssi=rssi,
            snr=snr,
            bandwidth=bandwidth,
            throughput=throughput,
            packet_loss=packet_loss,
            timestamp=datetime.now()
        )
    
    def _analyze_test_data(self, test_data_list: list) -> dict:
        rssi_values = [td.rssi for td in test_data_list]
        snr_values = [td.snr for td in test_data_list]
        throughput_values = [td.throughput for td in test_data_list]
        packet_loss_values = [td.packet_loss for td in test_data_list]
        
        return {
            'avg_rssi': statistics.mean(rssi_values),
            'std_rssi': statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0,
            'avg_snr': statistics.mean(snr_values),
            'std_snr': statistics.stdev(snr_values) if len(snr_values) > 1 else 0,
            'avg_throughput': statistics.mean(throughput_values),
            'std_throughput': statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0,
            'avg_packet_loss': statistics.mean(packet_loss_values),
            'std_packet_loss': statistics.stdev(packet_loss_values) if len(packet_loss_values) > 1 else 0,
            'max_throughput': max(throughput_values),
            'min_packet_loss': min(packet_loss_values),
            'consistency_score': self._calculate_consistency_score(rssi_values, throughput_values, packet_loss_values)
        }
    
    def _calculate_consistency_score(self, rssi_values, throughput_values, packet_loss_values) -> float:
        rssi_std = statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0
        throughput_std = statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0
        packet_loss_std = statistics.stdev(packet_loss_values) if len(packet_loss_values) > 1 else 0
        
        consistency = 100.0
        consistency -= min(rssi_std * 2, 30)
        consistency -= min(throughput_std * 0.1, 30)
        consistency -= min(packet_loss_std * 5, 30)
        
        return max(0.0, consistency)
    
    def _evaluate_channels(self, channel_test_results: dict) -> dict:
        best_score = -1
        best_channel_data = None
        
        for channel_data in channel_test_results.values():
            score = self._calculate_weighted_score(channel_data['analysis'])
            if score > best_score:
                best_score = score
                best_channel_data = channel_data
        
        return best_channel_data
    
    def _calculate_weighted_score(self, analysis: dict) -> float:
        weights = {
            'rssi': 0.25,
            'snr': 0.2,
            'throughput': 0.3,
            'packet_loss': 0.15,
            'consistency': 0.1
        }
        
        rssi_score = min((analysis.get('avg_rssi', -100) + 100) * 1.0, 100)
        snr_score = min(analysis.get('avg_snr', 0), 100)
        throughput_score = min(analysis.get('avg_throughput', 0) / 500 * 100, 100)
        packet_loss_score = max(100 - analysis.get('avg_packet_loss', 10) * 10, 0)
        consistency_score = analysis.get('consistency_score', 0)
        
        total_score = (
            rssi_score * weights['rssi'] +
            snr_score * weights['snr'] +
            throughput_score * weights['throughput'] +
            packet_loss_score * weights['packet_loss'] +
            consistency_score * weights['consistency']
        )
        
        return max(0.0, min(100.0, total_score))
    
    def _generate_recommendation_details(self, analysis: dict, quality_score: float) -> tuple:
        if quality_score >= 80:
            reason = f"该信道信号强度良好（平均RSSI: {analysis.get('avg_rssi', -100):.1f}dBm），"
            reason += f"信噪比高（平均SNR: {analysis.get('avg_snr', 0):.1f}dB），"
            reason += f"传输速率快（平均: {analysis.get('avg_throughput', 0):.1f}Mbps），"
            reason += f"丢包率低（平均: {analysis.get('avg_packet_loss', 10):.1f}%），"
            reason += f"网络稳定性好（一致性评分: {analysis.get('consistency_score', 0):.1f}）"
            improvement = "预期网络质量提升 25-35%"
        elif quality_score >= 60:
            reason = f"该信道信号强度适中（平均RSSI: {analysis.get('avg_rssi', -100):.1f}dBm），"
            reason += f"信噪比合理（平均SNR: {analysis.get('avg_snr', 0):.1f}dB），"
            reason += f"传输速率良好（平均: {analysis.get('avg_throughput', 0):.1f}Mbps），"
            reason += f"丢包率可接受（平均: {analysis.get('avg_packet_loss', 10):.1f}%）"
            improvement = "预期网络质量提升 15-25%"
        else:
            reason = f"当前环境所有信道都较为拥挤，"
            reason += f"该信道相对表现较好（信号强度: {analysis.get('avg_rssi', -100):.1f}dBm，"
            reason += f"传输速率: {analysis.get('avg_throughput', 0):.1f}Mbps，"
            reason += f"丢包率: {analysis.get('avg_packet_loss', 10):.1f}%）"
            improvement = "预期网络质量提升 5-15%"
        
        return reason, improvement


class TestCountDialog(QDialog):
    def __init__(self, current_count: int, parent=None):
        super().__init__(parent)
        self.current_count = current_count
        self._setup_ui()
    
    def _setup_ui(self):
        self.setWindowTitle("设置测试次数")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {UIStyles.COLORS['surface']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UIStyles.SPACING['lg'], UIStyles.SPACING['lg'], 
                                UIStyles.SPACING['lg'], UIStyles.SPACING['lg'])
        layout.setSpacing(UIStyles.SPACING['md'])
        
        info_label = QLabel("请输入测试次数（1-1000）：")
        info_label.setFont(UIStyles.get_font('body'))
        info_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(info_label)
        
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 1000)
        self.spin_box.setValue(self.current_count)
        self.spin_box.setMinimumHeight(44)
        self.spin_box.setFont(UIStyles.get_font('body'))
        UIStyles.apply_stylesheet(self.spin_box, 'input')
        layout.addWidget(self.spin_box)
        
        hint_label = QLabel("提示：测试次数越多，结果越准确，但耗时越长。")
        hint_label.setFont(UIStyles.get_font('caption'))
        hint_label.setStyleSheet(f"color: {UIStyles.COLORS['text_hint']};")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.setMinimumHeight(44)
        cancel_button.setFont(UIStyles.get_font('body', 'bold'))
        cancel_button.clicked.connect(self.reject)
        cancel_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(cancel_button, 'button_secondary')
        
        confirm_button = QPushButton("确认")
        confirm_button.setMinimumHeight(44)
        confirm_button.setFont(UIStyles.get_font('body', 'bold'))
        confirm_button.clicked.connect(self.accept)
        confirm_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(confirm_button, 'button_primary')
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)
        layout.addLayout(buttons_layout)
    
    def get_test_count(self) -> int:
        return self.spin_box.value()


class TestDataTable(QWidget):
    def __init__(self, test_data: list):
        super().__init__()
        self.test_data = test_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UIStyles.SPACING['md'], UIStyles.SPACING['md'], 
                                UIStyles.SPACING['md'], UIStyles.SPACING['md'])
        layout.setSpacing(UIStyles.SPACING['sm'])
        
        title_label = QLabel("测试数据详情")
        title_label.setFont(UIStyles.get_font('h3', 'bold'))
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "测试序号", "RSSI (dBm)", "SNR (dB)", 
            "带宽 (MHz)", "速率 (Mbps)", "丢包率 (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        UIStyles.apply_stylesheet(self.table, 'table')
        
        self._populate_table()
        layout.addWidget(self.table)
    
    def _populate_table(self):
        max_rows = 50
        display_data = self.test_data[:max_rows]
        
        self.table.setRowCount(len(display_data))
        
        for row, test in enumerate(display_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(f"{test.rssi:.1f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{test.snr:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{test.bandwidth:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{test.throughput:.1f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{test.packet_loss:.1f}"))
        
        if len(self.test_data) > max_rows:
            info_label = QLabel(f"显示前 {max_rows} 条测试数据，共 {len(self.test_data)} 条")
            info_label.setFont(UIStyles.get_font('caption'))
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet(f"color: {UIStyles.COLORS['text_hint']};")
            layout = self.layout()
            layout.addWidget(info_label)


class AnalysisDetailsPanel(QWidget):
    def __init__(self, analysis_details: dict):
        super().__init__()
        self.analysis_details = analysis_details
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UIStyles.SPACING['md'], UIStyles.SPACING['md'], 
                                UIStyles.SPACING['md'], UIStyles.SPACING['md'])
        layout.setSpacing(UIStyles.SPACING['md'])
        
        title_label = QLabel("分析结果")
        title_label.setFont(UIStyles.get_font('h3', 'bold'))
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        signal_group = QFrame()
        signal_group.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['md']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        signal_layout = QGridLayout(signal_group)
        signal_layout.setSpacing(UIStyles.SPACING['sm'])
        
        signal_metrics = [
            ("平均信号强度", f"{self.analysis_details.get('avg_rssi', -100):.1f} dBm"),
            ("信号强度标准差", f"{self.analysis_details.get('std_rssi', 0):.1f} dBm"),
            ("平均信噪比", f"{self.analysis_details.get('avg_snr', 0):.1f} dB"),
            ("信噪比标准差", f"{self.analysis_details.get('std_snr', 0):.1f} dB")
        ]
        
        for i, (label_text, value_text) in enumerate(signal_metrics):
            label = QLabel(label_text + ":")
            label.setFont(UIStyles.get_font('body', 'bold'))
            label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
            value = QLabel(value_text)
            value.setFont(UIStyles.get_font('body'))
            value.setStyleSheet(f"color: {UIStyles.COLORS['text_secondary']};")
            signal_layout.addWidget(label, i // 2, (i % 2) * 2)
            signal_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(signal_group)
        
        throughput_group = QFrame()
        throughput_group.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['md']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        throughput_layout = QGridLayout(throughput_group)
        throughput_layout.setSpacing(UIStyles.SPACING['sm'])
        
        throughput_metrics = [
            ("平均传输速率", f"{self.analysis_details.get('avg_throughput', 0):.1f} Mbps"),
            ("传输速率标准差", f"{self.analysis_details.get('std_throughput', 0):.1f} Mbps"),
            ("最大传输速率", f"{self.analysis_details.get('max_throughput', 0):.1f} Mbps"),
            ("平均丢包率", f"{self.analysis_details.get('avg_packet_loss', 10):.1f}%"),
            ("丢包率标准差", f"{self.analysis_details.get('std_packet_loss', 0):.1f}%"),
            ("最小丢包率", f"{self.analysis_details.get('min_packet_loss', 10):.1f}%")
        ]
        
        for i, (label_text, value_text) in enumerate(throughput_metrics):
            label = QLabel(label_text + ":")
            label.setFont(UIStyles.get_font('body', 'bold'))
            label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
            value = QLabel(value_text)
            value.setFont(UIStyles.get_font('body'))
            value.setStyleSheet(f"color: {UIStyles.COLORS['text_secondary']};")
            throughput_layout.addWidget(label, i // 2, (i % 2) * 2)
            throughput_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(throughput_group)
        
        consistency_group = QFrame()
        consistency_group.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['md']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        consistency_layout = QVBoxLayout(consistency_group)
        
        consistency_score = self.analysis_details.get('consistency_score', 0)
        consistency_label = QLabel(f"一致性评分: {consistency_score:.1f}")
        consistency_label.setFont(UIStyles.get_font('h3', 'bold'))
        consistency_label.setAlignment(Qt.AlignCenter)
        
        if consistency_score >= 80:
            consistency_label.setStyleSheet(f"color: {UIStyles.COLORS['success']};")
        elif consistency_score >= 60:
            consistency_label.setStyleSheet(f"color: {UIStyles.COLORS['warning']};")
        else:
            consistency_label.setStyleSheet(f"color: {UIStyles.COLORS['error']};")
        
        consistency_layout.addWidget(consistency_label)
        
        consistency_desc = QLabel("一致性评分反映了信道性能的稳定性，标准差越小，评分越高。")
        consistency_desc.setFont(UIStyles.get_font('body'))
        consistency_desc.setWordWrap(True)
        consistency_desc.setStyleSheet(f"color: {UIStyles.COLORS['text_hint']};")
        consistency_layout.addWidget(consistency_desc)
        
        layout.addWidget(consistency_group)


class RecommendationCard(QFrame):
    def __init__(self, recommendation: ChannelRecommendation):
        super().__init__()
        self.recommendation = recommendation
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border: 2px solid {UIStyles.COLORS['primary']};
                border-radius: {UIStyles.RADIUS['lg']}px;
                padding: {UIStyles.SPACING['lg']}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(UIStyles.SPACING['md'])
        
        title_label = QLabel("推荐信道")
        title_label.setFont(UIStyles.get_font('h2', 'bold'))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(title_label)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(UIStyles.SPACING['md'])
        
        channel_label = QLabel("信道编号:")
        channel_label.setFont(UIStyles.get_font('body', 'bold'))
        channel_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        channel_value = QLabel(str(self.recommendation.channel))
        channel_value.setFont(UIStyles.get_font('h2', 'bold'))
        channel_value.setStyleSheet(f"color: {UIStyles.COLORS['primary']};")
        
        band_label = QLabel("频段:")
        band_label.setFont(UIStyles.get_font('body', 'bold'))
        band_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        band_value = QLabel(self.recommendation.band)
        band_value.setFont(UIStyles.get_font('h3', 'bold'))
        band_value.setStyleSheet(f"color: {UIStyles.COLORS['error']};")
        
        score_label = QLabel("质量评分:")
        score_label.setFont(UIStyles.get_font('body', 'bold'))
        score_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        score_value = QLabel(f"{self.recommendation.quality_score:.1f}")
        score_value.setFont(UIStyles.get_font('h2', 'bold'))
        
        if self.recommendation.quality_score >= 80:
            score_value.setStyleSheet(f"color: {UIStyles.COLORS['success']};")
        elif self.recommendation.quality_score >= 60:
            score_value.setStyleSheet(f"color: {UIStyles.COLORS['warning']};")
        else:
            score_value.setStyleSheet(f"color: {UIStyles.COLORS['error']};")
        
        grid_layout.addWidget(channel_label, 0, 0)
        grid_layout.addWidget(channel_value, 0, 1)
        grid_layout.addWidget(band_label, 1, 0)
        grid_layout.addWidget(band_value, 1, 1)
        grid_layout.addWidget(score_label, 2, 0)
        grid_layout.addWidget(score_value, 2, 1)
        
        layout.addLayout(grid_layout)
        
        score_bar = QProgressBar()
        score_bar.setRange(0, 100)
        score_bar.setValue(int(self.recommendation.quality_score))
        UIStyles.apply_stylesheet(score_bar, 'progress_bar')
        layout.addWidget(score_bar)
        
        reason_label = QLabel("推荐理由:")
        reason_label.setFont(UIStyles.get_font('body', 'bold'))
        reason_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(reason_label)
        
        reason_text = QLabel(self.recommendation.reason)
        reason_text.setFont(UIStyles.get_font('body'))
        reason_text.setWordWrap(True)
        reason_text.setStyleSheet(f"color: {UIStyles.COLORS['text_secondary']};")
        layout.addWidget(reason_text)
        
        improvement_label = QLabel("预期改善:")
        improvement_label.setFont(UIStyles.get_font('body', 'bold'))
        improvement_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        layout.addWidget(improvement_label)
        
        improvement_text = QLabel(self.recommendation.expected_improvement)
        improvement_text.setFont(UIStyles.get_font('body', 'bold'))
        improvement_text.setStyleSheet(f"color: {UIStyles.COLORS['success']};")
        layout.addWidget(improvement_text)


class RecommendPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None
        self._current_band = "2.4GHz"
        self._analysis_panel = None
        self._recommendation = None
        self._setup_ui()
        self._apply_styles()
        logger.info("Recommend panel initialized")
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(UIStyles.SPACING['lg'], UIStyles.SPACING['lg'], 
                                UIStyles.SPACING['lg'], UIStyles.SPACING['lg'])
        layout.setSpacing(UIStyles.SPACING['md'])
        
        self._create_control_section(layout)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(10)
        splitter.setOpaqueResize(True)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {UIStyles.COLORS['border']};
            }}
            QSplitter::handle:hover {{
                background-color: {UIStyles.COLORS['primary']};
            }}
        """)
        
        progress_widget = self._create_progress_section()
        result_widget = self._create_recommendation_section()
        
        splitter.addWidget(progress_widget)
        splitter.addWidget(result_widget)
        splitter.setSizes([150, 500])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
    
    def _create_control_section(self, parent_layout):
        control_frame = QFrame()
        control_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['lg']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(UIStyles.SPACING['md'], UIStyles.SPACING['md'], 
                                          UIStyles.SPACING['md'], UIStyles.SPACING['md'])
        control_layout.setSpacing(UIStyles.SPACING['md'])
        
        title_label = QLabel("信道推荐控制")
        title_label.setFont(UIStyles.get_font('h3', 'bold'))
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        control_layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {UIStyles.COLORS['border']}; max-width: 1px;")
        control_layout.addWidget(line)
        
        band_label = QLabel("频段:")
        band_label.setFont(UIStyles.get_font('body'))
        band_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        control_layout.addWidget(band_label)
        
        self.band_2_4_button = QPushButton("2.4GHz")
        self.band_2_4_button.setMinimumHeight(44)
        self.band_2_4_button.setFont(UIStyles.get_font('body', 'bold'))
        self.band_2_4_button.setCheckable(True)
        self.band_2_4_button.setChecked(True)
        self.band_2_4_button.clicked.connect(lambda: self._on_band_toggled("2.4GHz"))
        self.band_2_4_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(self.band_2_4_button, 'button_toggle')
        
        self.band_5_button = QPushButton("5GHz")
        self.band_5_button.setMinimumHeight(44)
        self.band_5_button.setFont(UIStyles.get_font('body', 'bold'))
        self.band_5_button.setCheckable(True)
        self.band_5_button.clicked.connect(lambda: self._on_band_toggled("5GHz"))
        self.band_5_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(self.band_5_button, 'button_toggle')
        
        control_layout.addWidget(self.band_2_4_button)
        control_layout.addWidget(self.band_5_button)
        
        test_count_label = QLabel("测试次数:")
        test_count_label.setFont(UIStyles.get_font('body'))
        test_count_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        control_layout.addWidget(test_count_label)
        
        self.test_count_button = QPushButton(str(config_service.get_test_count()))
        self.test_count_button.setMinimumHeight(44)
        self.test_count_button.setFont(UIStyles.get_font('body'))
        self.test_count_button.clicked.connect(self._on_test_count_clicked)
        self.test_count_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(self.test_count_button, 'button_outline')
        
        control_layout.addWidget(self.test_count_button)
        
        control_layout.addStretch()
        
        self.analyze_button = QPushButton("分析并推荐")
        self.analyze_button.setMinimumHeight(44)
        self.analyze_button.setFont(UIStyles.get_font('body', 'bold'))
        self.analyze_button.clicked.connect(self._start_analysis)
        self.analyze_button.setCursor(Qt.PointingHandCursor)
        UIStyles.apply_stylesheet(self.analyze_button, 'button_success')
        
        control_layout.addWidget(self.analyze_button)
        
        parent_layout.addWidget(control_frame)
    
    def _create_progress_section(self) -> QWidget:
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['lg']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(UIStyles.SPACING['md'], UIStyles.SPACING['md'], 
                                          UIStyles.SPACING['md'], UIStyles.SPACING['md'])
        progress_layout.setSpacing(UIStyles.SPACING['sm'])
        
        title_label = QLabel("测试进度")
        title_label.setFont(UIStyles.get_font('h3', 'bold'))
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        progress_layout.addWidget(title_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        UIStyles.apply_stylesheet(self.progress_bar, 'progress_bar')
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("准备开始测试")
        self.progress_label.setFont(UIStyles.get_font('body'))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {UIStyles.COLORS['text_secondary']};")
        progress_layout.addWidget(self.progress_label)
        
        return progress_frame
    
    def _create_recommendation_section(self) -> QWidget:
        result_frame = QFrame()
        result_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {UIStyles.COLORS['surface']};
                border-radius: {UIStyles.RADIUS['lg']}px;
                border: 1px solid {UIStyles.COLORS['border']};
                padding: {UIStyles.SPACING['md']}px;
            }}
        """)
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(UIStyles.SPACING['md'], UIStyles.SPACING['md'], 
                                       UIStyles.SPACING['md'], UIStyles.SPACING['md'])
        result_layout.setSpacing(UIStyles.SPACING['md'])
        
        title_label = QLabel("推荐结果")
        title_label.setFont(UIStyles.get_font('h3', 'bold'))
        title_label.setStyleSheet(f"color: {UIStyles.COLORS['text_primary']};")
        result_layout.addWidget(title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {UIStyles.COLORS['background']};
                width: 12px;
                border-radius: {UIStyles.RADIUS['sm']}px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {UIStyles.COLORS['border']};
                border-radius: {UIStyles.RADIUS['sm']}px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {UIStyles.COLORS['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.recommendation_container = QWidget()
        self.recommendation_layout = QVBoxLayout(self.recommendation_container)
        self.recommendation_layout.setAlignment(Qt.AlignTop)
        self.recommendation_layout.setSpacing(UIStyles.SPACING['md'])
        
        self.placeholder_label = QLabel('点击"分析并推荐"按钮开始分析')
        self.placeholder_label.setFont(UIStyles.get_font('body'))
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet(f"color: {UIStyles.COLORS['text_hint']};")
        self.recommendation_layout.addWidget(self.placeholder_label)
        
        scroll_area.setWidget(self.recommendation_container)
        result_layout.addWidget(scroll_area)
        
        return result_frame
    
    def _apply_styles(self):
        """应用面板样式"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {UIStyles.COLORS['background']};
            }}
        """)
    
    def set_analysis_panel(self, panel):
        self._analysis_panel = panel
    
    def _on_band_toggled(self, band: str):
        self._current_band = band
        if band == "2.4GHz":
            self.band_2_4_button.setChecked(True)
            self.band_5_button.setChecked(False)
            UIStyles.apply_stylesheet(self.band_2_4_button, 'button_primary')
            UIStyles.apply_stylesheet(self.band_5_button, 'button_secondary')
        else:
            self.band_2_4_button.setChecked(False)
            self.band_5_button.setChecked(True)
            UIStyles.apply_stylesheet(self.band_2_4_button, 'button_secondary')
            UIStyles.apply_stylesheet(self.band_5_button, 'button_primary')
    
    def _on_test_count_clicked(self):
        dialog = TestCountDialog(config_service.get_test_count(), self)
        if dialog.exec_() == QDialog.Accepted:
            new_count = dialog.get_test_count()
            config_service.set_test_count(new_count)
            self.test_count_button.setText(str(new_count))
            logger.info(f"Test count updated to {new_count}")
    
    @handle_exceptions(show_dialog=True)
    def _start_analysis(self):
        if self._worker and self._worker.isRunning():
            return
        
        if not self._analysis_panel:
            exception_handler.show_warning("错误", "信道分析面板未初始化")
            return
        
        channels = self._analysis_panel.get_channels()
        
        if not channels:
            reply = QMessageBox.question(
                self,
                "提示",
                "尚未执行信道扫描，是否立即扫描？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._analysis_panel._start_scan()
                self._analysis_panel.scan_completed.connect(self._on_scan_completed)
            return
        
        self._perform_analysis(channels)
    
    def _on_scan_completed(self):
        self._analysis_panel.scan_completed.disconnect(self._on_scan_completed)
        channels = self._analysis_panel.get_channels()
        if channels:
            self._perform_analysis(channels)
    
    def _perform_analysis(self, channels: list):
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("分析中...")
        self.progress_bar.setValue(0)
        self.progress_label.setText("开始分析...")
        
        self._worker = RecommendWorker(channels)
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.recommendation_completed.connect(self._on_recommendation_completed)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()
        
        logger.info(f"Channel recommendation started for {self._current_band}")
    
    def _on_progress_updated(self, progress: int):
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"分析进度: {progress}%")
    
    def _on_recommendation_completed(self, recommendation: ChannelRecommendation):
        self._recommendation = recommendation
        self._display_recommendation(recommendation)
        self._reset_ui()
        logger.info(f"Channel recommendation completed: {recommendation.channel}")
    
    def _on_error(self, error_message: str):
        self._reset_ui()
        exception_handler.show_warning("分析失败", error_message)
    
    def _display_recommendation(self, recommendation: ChannelRecommendation):
        if self.placeholder_label:
            self.placeholder_label.deleteLater()
            self.placeholder_label = None
        
        self._clear_recommendation_layout()
        
        recommendation_card = RecommendationCard(recommendation)
        self.recommendation_layout.addWidget(recommendation_card)
        
        analysis_details = AnalysisDetailsPanel(recommendation.analysis_details)
        self.recommendation_layout.addWidget(analysis_details)
        
        test_data_table = TestDataTable(recommendation.test_data)
        self.recommendation_layout.addWidget(test_data_table)
    
    def _clear_recommendation_layout(self):
        while self.recommendation_layout.count():
            item = self.recommendation_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _reset_ui(self):
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("分析并推荐")
    
    def refresh(self):
        if self._analysis_panel:
            self._analysis_panel.refresh()
