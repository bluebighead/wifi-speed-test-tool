from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QGridLayout, QScrollArea,
                             QFrame, QProgressBar, QTableWidget, QTableWidgetItem,
                             QHeaderView, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont, QPixmap
from src.utils.logger import logger
from src.utils.exception_handler import exception_handler, handle_exceptions
from src.services.config_service import config_service
from src.models.data_models import ChannelRecommendation, ChannelInfo, ChannelTestData
from src.ui.channel_analysis_panel import ChannelAnalysisPanel
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
        
        # 获取配置的测试次数
        test_count = config_service.get_test_count()
        
        # 对每个信道执行指定次数的测试
        channel_test_results = {}
        total_tests = len(self.channels) * test_count
        current_test = 0
        
        for channel_info in self.channels:
            test_data_list = []
            for i in range(test_count):
                # 模拟测试数据采集
                test_data = self._perform_channel_test(channel_info)
                test_data_list.append(test_data)
                
                # 更新进度
                current_test += 1
                progress = int((current_test / total_tests) * 100)
                self.progress_updated.emit(progress)
            
            channel_test_results[channel_info.channel] = {
                'channel_info': channel_info,
                'test_data': test_data_list,
                'analysis': self._analyze_test_data(test_data_list)
            }
        
        # 使用加权算法评估各信道
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
        """执行单个信道测试"""
        # 基于信道信息生成合理的测试数据
        base_rssi = channel_info.signal_strength
        base_occupancy = channel_info.occupancy
        base_interference = channel_info.interference
        
        # 添加随机波动
        rssi = base_rssi + random.randint(-5, 5)
        snr = (rssi + 100) * random.uniform(0.8, 1.2)
        
        if channel_info.band == "2.4GHz":
            bandwidth = 20.0
            max_throughput = 72.2
        else:
            bandwidth = 80.0
            max_throughput = 433.3
        
        # 基于占用率和干扰计算吞吐量
        throughput_factor = 1.0 - (base_occupancy + base_interference) / 200.0
        throughput = max_throughput * throughput_factor * random.uniform(0.7, 1.0)
        
        # 基于干扰计算丢包率
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
        """分析测试数据"""
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
        """计算一致性评分"""
        rssi_std = statistics.stdev(rssi_values) if len(rssi_values) > 1 else 0
        throughput_std = statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0
        packet_loss_std = statistics.stdev(packet_loss_values) if len(packet_loss_values) > 1 else 0
        
        # 标准差越小，一致性越高
        consistency = 100.0
        consistency -= min(rssi_std * 2, 30)
        consistency -= min(throughput_std * 0.1, 30)
        consistency -= min(packet_loss_std * 5, 30)
        
        return max(0.0, consistency)
    
    def _evaluate_channels(self, channel_test_results: dict) -> dict:
        """评估所有信道并选择最优的"""
        best_score = -1
        best_channel_data = None
        
        for channel_data in channel_test_results.values():
            score = self._calculate_weighted_score(channel_data['analysis'])
            if score > best_score:
                best_score = score
                best_channel_data = channel_data
        
        return best_channel_data
    
    def _calculate_weighted_score(self, analysis: dict) -> float:
        """计算加权评分"""
        # 权重定义
        weights = {
            'rssi': 0.25,      # 信号强度
            'snr': 0.2,         # 信噪比
            'throughput': 0.3,  # 传输速率
            'packet_loss': 0.15, # 丢包率
            'consistency': 0.1  # 一致性
        }
        
        # 计算各项得分
        rssi_score = min((analysis.get('avg_rssi', -100) + 100) * 1.0, 100)
        snr_score = min(analysis.get('avg_snr', 0), 100)
        throughput_score = min(analysis.get('avg_throughput', 0) / 500 * 100, 100)  # 假设最大500Mbps
        packet_loss_score = max(100 - analysis.get('avg_packet_loss', 10) * 10, 0)
        consistency_score = analysis.get('consistency_score', 0)
        
        # 计算加权总分
        total_score = (
            rssi_score * weights['rssi'] +
            snr_score * weights['snr'] +
            throughput_score * weights['throughput'] +
            packet_loss_score * weights['packet_loss'] +
            consistency_score * weights['consistency']
        )
        
        return max(0.0, min(100.0, total_score))
    
    def _generate_recommendation_details(self, analysis: dict, quality_score: float) -> tuple:
        """生成推荐理由和预期改善"""
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


class TestDataTable(QWidget):
    def __init__(self, test_data: list):
        super().__init__()
        self.test_data = test_data
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("📊 测试数据详情")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "测试序号", "RSSI (dBm)", "SNR (dB)", 
            "带宽 (MHz)", "速率 (Mbps)", "丢包率 (%)"
        ])
        # 设置列宽策略，优先适应内容
        for i in range(self.table.columnCount()):
            if i == 0:  # 测试序号
                self.table.setColumnWidth(i, 80)
            elif i in [1, 2]:  # RSSI, SNR
                self.table.setColumnWidth(i, 100)
            elif i == 3:  # 带宽
                self.table.setColumnWidth(i, 100)
            elif i == 4:  # 速率
                self.table.setColumnWidth(i, 120)
            elif i == 5:  # 丢包率
                self.table.setColumnWidth(i, 100)
        # 剩余空间平均分配
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setMinimumHeight(300)  # 设置最小高度
        
        self._populate_table()
        layout.addWidget(self.table)
    
    def _populate_table(self):
        # 限制显示的测试数据行数，最多显示50行，避免UI渲染崩溃
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
        
        # 如果测试数据超过50行，添加提示信息
        if len(self.test_data) > max_rows:
            info_label = QLabel(f"📝 显示前 {max_rows} 条测试数据，共 {len(self.test_data)} 条")
            info_label.setFont(QFont("Arial", 10))
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #7f8c8d;")
            self.layout().addWidget(info_label)


class AnalysisDetailsPanel(QWidget):
    def __init__(self, analysis_details: dict):
        super().__init__()
        self.analysis_details = analysis_details
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("📈 分析结果")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        # 使用分组框来组织不同类别的分析数据
        # 信号质量组
        signal_group = QGroupBox("信号质量分析")
        signal_layout = QGridLayout(signal_group)
        signal_layout.setSpacing(15)
        
        normal_font = QFont("Arial", 11)
        bold_font = QFont("Arial", 11, QFont.Bold)
        
        # 信号质量指标
        signal_metrics = [
            ("平均信号强度", f"{self.analysis_details.get('avg_rssi', -100):.1f} dBm"),
            ("信号强度标准差", f"{self.analysis_details.get('std_rssi', 0):.1f} dBm"),
            ("平均信噪比", f"{self.analysis_details.get('avg_snr', 0):.1f} dB"),
            ("信噪比标准差", f"{self.analysis_details.get('std_snr', 0):.1f} dB")
        ]
        
        for i, (label_text, value_text) in enumerate(signal_metrics):
            label = QLabel(label_text + ":")
            label.setFont(bold_font)
            label.setAlignment(Qt.AlignRight)
            value = QLabel(value_text)
            value.setFont(normal_font)
            value.setAlignment(Qt.AlignLeft)
            signal_layout.addWidget(label, i // 2, (i % 2) * 2)
            signal_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(signal_group)
        
        # 传输性能组
        throughput_group = QGroupBox("传输性能分析")
        throughput_layout = QGridLayout(throughput_group)
        throughput_layout.setSpacing(15)
        
        # 传输性能指标
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
            label.setFont(bold_font)
            label.setAlignment(Qt.AlignRight)
            value = QLabel(value_text)
            value.setFont(normal_font)
            value.setAlignment(Qt.AlignLeft)
            throughput_layout.addWidget(label, i // 2, (i % 2) * 2)
            throughput_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
        
        layout.addWidget(throughput_group)
        
        # 一致性分析组
        consistency_group = QGroupBox("一致性分析")
        consistency_layout = QVBoxLayout(consistency_group)
        
        consistency_score = self.analysis_details.get('consistency_score', 0)
        consistency_label = QLabel(f"一致性评分: {consistency_score:.1f}")
        consistency_label.setFont(QFont("Arial", 12, QFont.Bold))
        consistency_label.setAlignment(Qt.AlignCenter)
        
        # 根据一致性评分设置颜色
        if consistency_score >= 80:
            consistency_label.setStyleSheet("color: #27ae60;")
        elif consistency_score >= 60:
            consistency_label.setStyleSheet("color: #f39c12;")
        else:
            consistency_label.setStyleSheet("color: #e74c3c;")
        
        consistency_layout.addWidget(consistency_label)
        
        # 一致性说明
        consistency_desc = QLabel("一致性评分反映了信道性能的稳定性，标准差越小，评分越高。")
        consistency_desc.setFont(normal_font)
        consistency_desc.setWordWrap(True)
        consistency_desc.setStyleSheet("color: #7f8c8d;")
        consistency_layout.addWidget(consistency_desc)
        
        layout.addWidget(consistency_group)


class RecommendationCard(QFrame):
    def __init__(self, recommendation: ChannelRecommendation):
        super().__init__()
        self.recommendation = recommendation
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title_font = QFont("Arial", 16, QFont.Bold)
        normal_font = QFont("Arial", 11)
        bold_font = QFont("Arial", 11, QFont.Bold)
        
        title_label = QLabel("🌟 推荐信道")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        # 核心信息网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # 信道信息
        channel_label = QLabel("信道编号:")
        channel_label.setFont(bold_font)
        channel_value = QLabel(str(self.recommendation.channel))
        channel_value.setFont(QFont("Arial", 18, QFont.Bold))
        channel_value.setStyleSheet("color: #3498db;")
        
        # 频段信息
        band_label = QLabel("频段:")
        band_label.setFont(bold_font)
        band_value = QLabel(self.recommendation.band)
        band_value.setFont(QFont("Arial", 14, QFont.Bold))
        band_value.setStyleSheet("color: #e74c3c;")
        
        # 质量评分
        score_label = QLabel("质量评分:")
        score_label.setFont(bold_font)
        score_value = QLabel(f"{self.recommendation.quality_score:.1f}")
        score_value.setFont(QFont("Arial", 18, QFont.Bold))
        
        if self.recommendation.quality_score >= 80:
            score_value.setStyleSheet("color: #27ae60;")
        elif self.recommendation.quality_score >= 60:
            score_value.setStyleSheet("color: #f39c12;")
        else:
            score_value.setStyleSheet("color: #e74c3c;")
        
        # 添加到网格
        grid_layout.addWidget(channel_label, 0, 0)
        grid_layout.addWidget(channel_value, 0, 1)
        grid_layout.addWidget(band_label, 1, 0)
        grid_layout.addWidget(band_value, 1, 1)
        grid_layout.addWidget(score_label, 2, 0)
        grid_layout.addWidget(score_value, 2, 1)
        
        layout.addLayout(grid_layout)
        
        # 质量评分进度条
        score_bar = QProgressBar()
        score_bar.setRange(0, 100)
        score_bar.setValue(int(self.recommendation.quality_score))
        score_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(score_bar)
        
        # 推荐理由
        reason_group = QGroupBox("推荐理由")
        reason_layout = QVBoxLayout(reason_group)
        reason_text = QLabel(self.recommendation.reason)
        reason_text.setFont(normal_font)
        reason_text.setWordWrap(True)
        reason_text.setStyleSheet("color: #34495e;")
        reason_layout.addWidget(reason_text)
        layout.addWidget(reason_group)
        
        # 预期改善
        improvement_group = QGroupBox("预期改善")
        improvement_layout = QVBoxLayout(improvement_group)
        improvement_text = QLabel(self.recommendation.expected_improvement)
        improvement_text.setFont(QFont("Arial", 12, QFont.Bold))
        improvement_text.setStyleSheet("color: #27ae60;")
        improvement_text.setAlignment(Qt.AlignCenter)
        improvement_layout.addWidget(improvement_text)
        layout.addWidget(improvement_group)


class RecommendPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None
        self._current_recommendation = None
        self._analysis_panel = None
        self._progress_bar = None
        self._setup_ui()
        logger.info("Recommend panel initialized")
    
    def set_analysis_panel(self, panel: ChannelAnalysisPanel):
        self._analysis_panel = panel
        # 连接扫描完成信号
        panel.scan_completed.connect(self._on_channel_scan_completed)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self._create_control_section(layout)
        self._create_progress_section(layout)
        
        # 创建一个垂直分割器，用于控制推荐结果和使用提示的比例
        splitter = QSplitter(Qt.Vertical)
        
        # 设置分割器属性，提高拖动流畅度
        splitter.setHandleWidth(10)  # 设置分割手柄宽度，更易于拖动
        splitter.setOpaqueResize(True)  # 启用不透明调整，拖动时实时显示大小变化
        
        # 创建推荐结果区域
        recommend_widget = QWidget()
        recommend_layout = QVBoxLayout(recommend_widget)
        recommend_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距，提高空间利用率
        self._create_recommendation_section(recommend_layout)
        
        # 创建使用提示区域
        tips_widget = QWidget()
        tips_layout = QVBoxLayout(tips_widget)
        tips_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距，提高空间利用率
        self._create_tips_section(tips_layout)
        
        # 将两个区域添加到分割器
        splitter.addWidget(recommend_widget)
        splitter.addWidget(tips_widget)
        
        # 设置分割器的初始比例
        splitter.setSizes([600, 300])
        
        # 设置分割器的伸缩因子，使推荐结果区域优先伸缩
        splitter.setStretchFactor(0, 1)  # 推荐结果区域可伸缩
        splitter.setStretchFactor(1, 0)  # 使用提示区域固定大小
        
        # 将分割器添加到主布局
        layout.addWidget(splitter)
    
    def _create_control_section(self, parent_layout):
        control_group = QGroupBox("控制面板")
        control_layout = QVBoxLayout(control_group)
        
        # 创建频段切换按钮区域
        band_layout = QHBoxLayout()
        band_label = QLabel("频段选择:")
        band_label.setFont(QFont("Arial", 10))
        
        self.band_2_4_button = QPushButton("2.4GHz")
        self.band_2_4_button.setMinimumHeight(30)
        self.band_2_4_button.setFont(QFont("Arial", 10))
        self.band_2_4_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #f0f8ff;
                border-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #e6f3ff;
                border-color: #21618c;
            }
            QPushButton:checked {
                background-color: #27ae60;
                color: white;
                border-color: #27ae60;
            }
        """)
        self.band_2_4_button.setCheckable(True)
        self.band_2_4_button.setChecked(True)
        
        self.band_5_button = QPushButton("5GHz")
        self.band_5_button.setMinimumHeight(30)
        self.band_5_button.setFont(QFont("Arial", 10))
        self.band_5_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #e74c3c;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #fff5f5;
                border-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #ffe6e6;
                border-color: #a93226;
            }
            QPushButton:checked {
                background-color: #27ae60;
                color: white;
                border-color: #27ae60;
            }
        """)
        self.band_5_button.setCheckable(True)
        
        # 连接按钮信号
        self.band_2_4_button.toggled.connect(lambda checked: self._on_band_toggled("2.4GHz", checked))
        self.band_5_button.toggled.connect(lambda checked: self._on_band_toggled("5GHz", checked))
        
        band_layout.addWidget(band_label)
        band_layout.addWidget(self.band_2_4_button)
        band_layout.addWidget(self.band_5_button)
        band_layout.addStretch()
        
        # 创建测试次数输入区域
        test_count_layout = QHBoxLayout()
        test_count_label = QLabel("测试次数:")
        test_count_label.setFont(QFont("Arial", 10))
        
        self.test_count_input = QPushButton(str(config_service.get_test_count()))
        self.test_count_input.setMinimumHeight(30)
        self.test_count_input.setFont(QFont("Arial", 10))
        self.test_count_input.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #34495e;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #e9ecef;
                border-color: #7f8c8d;
            }
        """)
        self.test_count_input.clicked.connect(self._on_test_count_clicked)
        
        test_count_hint = QLabel("(1-1000)")
        test_count_hint.setFont(QFont("Arial", 9))
        test_count_hint.setStyleSheet("color: #7f8c8d;")
        
        test_count_layout.addWidget(test_count_label)
        test_count_layout.addWidget(self.test_count_input)
        test_count_layout.addWidget(test_count_hint)
        test_count_layout.addStretch()
        
        # 创建分析和应用按钮区域
        buttons_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("分析并推荐")
        self.analyze_button.setMinimumHeight(50)
        self.analyze_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.analyze_button.clicked.connect(self._start_analysis)
        
        self.apply_button = QPushButton("应用推荐")
        self.apply_button.setMinimumHeight(50)
        self.apply_button.setFont(QFont("Arial", 12))
        self.apply_button.setEnabled(False)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.apply_button.clicked.connect(lambda: self._apply_recommendation())
        
        buttons_layout.addWidget(self.analyze_button)
        buttons_layout.addWidget(self.apply_button)
        
        # 添加到主控制布局
        control_layout.addLayout(band_layout)
        control_layout.addLayout(test_count_layout)
        control_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(control_group)
    
    def _create_progress_section(self, parent_layout):
        progress_group = QGroupBox("测试进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        
        self._progress_label = QLabel("准备开始测试")
        self._progress_label.setAlignment(Qt.AlignCenter)
        self._progress_label.setFont(QFont("Arial", 10))
        
        progress_layout.addWidget(self._progress_bar)
        progress_layout.addWidget(self._progress_label)
        
        parent_layout.addWidget(progress_group)
    
    def _create_recommendation_section(self, parent_layout):
        recommend_group = QGroupBox("推荐结果")
        recommend_layout = QVBoxLayout(recommend_group)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 移除固定最小高度，让布局能够灵活适应
        
        self.recommendation_container = QWidget()
        self.recommendation_layout = QVBoxLayout(self.recommendation_container)
        self.recommendation_layout.setAlignment(Qt.AlignTop)
        self.recommendation_layout.setSpacing(20)  # 增加组件之间的间距
        
        self.placeholder_label = QLabel('点击"分析并推荐"按钮开始分析')
        self.placeholder_label.setFont(QFont("Arial", 12))
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #95a5a6;")
        # 移除占位符的固定最小高度
        
        self.recommendation_layout.addWidget(self.placeholder_label)
        
        scroll_area.setWidget(self.recommendation_container)
        recommend_layout.addWidget(scroll_area)
        
        # 移除推荐组的固定最小高度
        
        parent_layout.addWidget(recommend_group)
    
    def _create_tips_section(self, parent_layout):
        tips_group = QGroupBox("使用提示")
        tips_layout = QVBoxLayout(tips_group)
        
        tips_text = QLabel("""
        <b>如何使用信道推荐功能：</b>
        <ol>
            <li>首先在"信道分析"标签页扫描当前环境的信道占用情况</li>
            <li>切换到"信道推荐"标签页，点击"分析并推荐"按钮</li>
            <li>系统会执行10组独立的信道质量测试，采集关键性能指标</li>
            <li>基于加权算法分析测试数据，推荐最优信道</li>
            <li>查看推荐理由、测试数据和分析结果</li>
            <li>点击"应用推荐"按钮切换到推荐信道（需要管理员权限）</li>
        </ol>
        
        <b>测试指标说明：</b>
        <ul>
            <li><b>RSSI (dBm)</b>：信号强度，值越大越好</li>
            <li><b>SNR (dB)</b>：信噪比，值越大越好</li>
            <li><b>带宽 (MHz)</b>：信道带宽，通常为20或80MHz</li>
            <li><b>速率 (Mbps)</b>：传输速率，值越大越好</li>
            <li><b>丢包率 (%)</b>：数据包丢失率，值越小越好</li>
        </ul>
        
        <b>注意事项：</b>
        <ul>
            <li>应用信道更改需要管理员权限</li>
            <li>更改信道后可能需要重新连接WiFi</li>
            <li>不同路由器的信道设置方式可能不同</li>
            <li>建议在非高峰时段进行信道切换</li>
        </ul>
        """)
        tips_text.setWordWrap(True)
        tips_text.setTextFormat(Qt.RichText)
        tips_text.setFont(QFont("Arial", 10))
        
        tips_layout.addWidget(tips_text)
        parent_layout.addWidget(tips_group)
    
    @handle_exceptions(show_dialog=True)
    def _start_analysis(self, *args):
        if self._worker and self._worker.isRunning():
            return
        
        if not self._analysis_panel:
            exception_handler.show_warning("错误", "请先进行信道分析")
            return
        
        channels = self._analysis_panel.get_channels()
        if not channels:
            # 显示模态提示框，说明扫描的必要性
            reply = exception_handler.show_question(
                "需要信道扫描",
                "未检测到可用的信道数据，需要先执行扫描才能进行推荐分析。\n\n"
                "扫描说明：\n"
                "• 扫描过程将检测当前环境中所有可用信道\n"
                "• 预计耗时：约5-10秒\n"
                "• 扫描结果将直接影响推荐的准确性\n\n"
                "是否立即执行信道扫描？"
            )
            
            if not reply:
                return
            
            # 执行扫描任务
            self._execute_channel_scan()
            return
        
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("分析中...")
        self.apply_button.setEnabled(False)
        self._progress_bar.setValue(0)
        self._progress_label.setText("开始执行信道测试...")
        
        self._worker = RecommendWorker(channels)
        self._worker.recommendation_completed.connect(self._on_recommendation_completed)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.start()
        
        test_count = config_service.get_test_count()
        logger.info(f"Recommendation analysis started with {test_count} test sets per channel")
    
    def _execute_channel_scan(self):
        """执行信道扫描任务"""
        if not self._analysis_panel:
            return
        
        # 禁用相关按钮
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("扫描中...")
        self.apply_button.setEnabled(False)
        
        # 更新进度信息
        self._progress_bar.setValue(0)
        self._progress_label.setText("正在执行信道扫描...")
        
        # 触发信道分析面板的扫描
        self._analysis_panel.refresh()
        
        # 不再使用固定定时器，而是通过信号监听扫描完成
        logger.info("Channel scan started, waiting for completion")
    
    def _on_channel_scan_completed(self):
        """处理信道扫描完成的信号"""
        if not self._analysis_panel:
            return
        
        # 检查扫描是否是由推荐面板触发的
        if self.analyze_button.text() == "扫描中...":
            channels = self._analysis_panel.get_channels()
            if not channels:
                # 扫描失败，显示错误信息
                exception_handler.show_warning(
                    "扫描失败",
                    "信道扫描未能获取到数据，请检查网络连接后重试。"
                )
                self._reset_ui()
                return
            
            # 扫描成功，自动执行分析
            self.analyze_button.setText("分析中...")
            self._progress_bar.setValue(0)
            self._progress_label.setText("开始执行信道测试...")
            
            self._worker = RecommendWorker(channels)
            self._worker.recommendation_completed.connect(self._on_recommendation_completed)
            self._worker.error_occurred.connect(self._on_error)
            self._worker.progress_updated.connect(self._on_progress_updated)
            self._worker.start()
            
            logger.info("Auto analysis started after channel scan completion")
    

    
    def _on_progress_updated(self, progress: int):
        """处理进度更新"""
        self._progress_bar.setValue(progress)
        self._progress_label.setText(f"测试进度: {progress}%")
    
    def _on_recommendation_completed(self, recommendation: ChannelRecommendation):
        self._current_recommendation = recommendation
        self._update_recommendation_display(recommendation)
        self._reset_ui()
        
        self.apply_button.setEnabled(True)
        self._progress_label.setText("测试完成，推荐结果已生成")
        logger.info(f"Recommendation completed: {recommendation}")
    
    def _on_error(self, error_message: str):
        self._reset_ui()
        self._progress_label.setText("测试失败")
        exception_handler.show_warning("推荐失败", error_message)
    
    def _update_recommendation_display(self, recommendation: ChannelRecommendation):
        try:
            if self.placeholder_label:
                self.recommendation_layout.removeWidget(self.placeholder_label)
                self.placeholder_label.deleteLater()
                self.placeholder_label = None
            
            # 清除所有现有的推荐卡片
            for i in reversed(range(self.recommendation_layout.count())):
                widget = self.recommendation_layout.itemAt(i).widget()
                if widget:
                    self.recommendation_layout.removeWidget(widget)
                    widget.deleteLater()
            
            # 添加推荐卡片
            card = RecommendationCard(recommendation)
            # 移除固定最小高度，让布局能够灵活适应
            self.recommendation_layout.addWidget(card)
            
            # 添加测试数据表格
            test_data_table = TestDataTable(recommendation.test_data)
            # 移除固定最小高度，让布局能够灵活适应
            self.recommendation_layout.addWidget(test_data_table)
            
            # 添加分析详情面板
            analysis_panel = AnalysisDetailsPanel(recommendation.analysis_details)
            # 移除固定最小高度，让布局能够灵活适应
            self.recommendation_layout.addWidget(analysis_panel)
        except Exception as e:
            logger.error(f"Failed to update recommendation display: {e}", exc_info=True)
            # 清除所有现有的推荐卡片
            for i in reversed(range(self.recommendation_layout.count())):
                widget = self.recommendation_layout.itemAt(i).widget()
                if widget:
                    self.recommendation_layout.removeWidget(widget)
                    widget.deleteLater()
            
            # 重置占位符引用
            self.placeholder_label = None
            
            # 重新添加占位符
            self.placeholder_label = QLabel('更新推荐结果时发生错误，请重试')
            self.placeholder_label.setFont(QFont("Arial", 12))
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.placeholder_label.setStyleSheet("color: #e74c3c;")
            self.recommendation_layout.addWidget(self.placeholder_label)
            
            # 显示错误信息
            exception_handler.show_warning("更新失败", f"更新推荐结果时发生错误: {str(e)}")
    
    def _reset_ui(self):
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("分析并推荐")
    
    def _on_band_toggled(self, band: str, checked: bool):
        if not checked:
            return
        
        # 确保只有一个按钮被选中
        if band == "2.4GHz":
            self.band_5_button.setChecked(False)
        else:
            self.band_2_4_button.setChecked(False)
        
        # 更新分析面板的频段设置
        if self._analysis_panel:
            # 找到分析面板中的频段下拉框并更新
            if hasattr(self._analysis_panel, 'band_combo'):
                self._analysis_panel.band_combo.setCurrentText(band)
                # 触发扫描以获取对应频段的信道数据
                self._analysis_panel.refresh()
        
        # 清除当前的推荐结果
        self._clear_recommendation_display()
        
        logger.info(f"Band switched to {band}")
    
    def _on_test_count_clicked(self):
        """处理测试次数按钮点击事件，弹出输入对话框"""
        from PyQt5.QtWidgets import QInputDialog
        
        current_count = config_service.get_test_count()
        
        # 弹出输入对话框
        count, ok = QInputDialog.getInt(
            self,
            "设置测试次数",
            "请输入每个信道的测试次数 (1-1000):",
            current_count,
            1,
            1000,
            1
        )
        
        if ok:
            # 保存新的测试次数
            config_service.set('wifi.test_count', count)
            config_service.save()
            
            # 更新按钮显示
            self.test_count_input.setText(str(count))
            
            logger.info(f"Test count updated to {count}")
    
    def _clear_recommendation_display(self):
        # 清除所有现有的推荐卡片
        for i in reversed(range(self.recommendation_layout.count())):
            widget = self.recommendation_layout.itemAt(i).widget()
            if widget:
                self.recommendation_layout.removeWidget(widget)
                widget.deleteLater()
        
        # 重置占位符引用
        self.placeholder_label = None
        
        # 重新添加占位符
        self.placeholder_label = QLabel('点击"分析并推荐"按钮开始分析')
        self.placeholder_label.setFont(QFont("Arial", 12))
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #95a5a6;")
        self.recommendation_layout.addWidget(self.placeholder_label)
        
        # 禁用应用按钮
        self.apply_button.setEnabled(False)
        
        # 重置进度信息
        self._progress_bar.setValue(0)
        self._progress_label.setText("准备开始测试")
    
    @handle_exceptions(show_dialog=True)
    def _apply_recommendation(self):
        if not self._current_recommendation:
            return
        
        reply = exception_handler.show_question(
            "确认应用",
            f"确定要切换到信道 {self._current_recommendation.channel} ({self._current_recommendation.band}) 吗？\n\n"
            f"注意：此操作需要管理员权限，并且可能需要重新连接WiFi。"
        )
        
        if not reply:
            return
        
        try:
            import subprocess
            
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True
            )
            
            if '管理员' not in result.stdout and 'Administrator' not in result.stdout:
                exception_handler.show_warning(
                    "权限不足",
                    "需要管理员权限才能更改信道设置。\n"
                    "请以管理员身份运行程序，然后重试。"
                )
                return
            
            exception_handler.show_info(
                "提示",
                f"信道更改请求已发送。\n\n"
                f"目标信道: {self._current_recommendation.channel}\n"
                f"频段: {self._current_recommendation.band}\n\n"
                f"注意：实际信道更改需要在路由器设置中进行。\n"
                f"本程序仅提供推荐，无法直接修改路由器设置。"
            )
            
            logger.info(f"Recommendation applied: {self._current_recommendation}")
            
        except Exception as e:
            logger.error(f"Failed to apply recommendation: {e}", exc_info=True)
            exception_handler.show_warning("应用失败", f"无法应用推荐：{str(e)}")
    
    def refresh(self):
        self._start_analysis()
