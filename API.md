# API文档

## 📋 文档概述

本文档详细描述了WiFi Speed Test Tool的API接口，包括数据模型、服务接口、UI组件接口等，为开发者提供完整的API参考。

## 📦 数据模型API

### SpeedTestResult

测速结果数据模型

**属性**：
- `download_speed: float` - 下载速度 (Mbps)
- `upload_speed: float` - 上传速度 (Mbps)
- `latency: float` - 延迟 (ms)
- `jitter: float` - 抖动 (ms)
- `timestamp: datetime` - 时间戳
- `server: str` - 测速服务器

**方法**：
```python
def __str__(self) -> str
    # 返回格式化的测速结果字符串
    # 示例: "下载: 100.50 Mbps, 上传: 50.25 Mbps, 延迟: 10.00 ms"
```

**使用示例**：
```python
from src.models.data_models import SpeedTestResult
from datetime import datetime

result = SpeedTestResult(
    download_speed=100.5,
    upload_speed=50.25,
    latency=10.0,
    jitter=2.5,
    timestamp=datetime.now(),
    server="Speedtest.net"
)
print(result)
```

---

### NetworkInfo

网络信息数据模型

**属性**：
- `ssid: str` - 网络名称
- `bssid: str` - MAC地址
- `signal_strength: int` - 信号强度 (dBm)
- `channel: int` - 信道
- `frequency: float` - 频率 (GHz)
- `encryption_type: str` - 加密类型

**方法**：
```python
def __str__(self) -> str
    # 返回格式化的网络信息字符串
    # 示例: "MyWiFi (信道: 6, 信号: -45 dBm)"
```

**使用示例**：
```python
from src.models.data_models import NetworkInfo

network = NetworkInfo(
    ssid="MyWiFi",
    bssid="00:11:22:33:44:55",
    signal_strength=-45,
    channel=6,
    frequency=2.437,
    encryption_type="WPA2"
)
print(network)
```

---

### ChannelInfo

信道信息数据模型

**属性**：
- `channel: int` - 信道
- `frequency: float` - 频率 (GHz)
- `band: str` - 频段 ("2.4GHz" 或 "5GHz")
- `signal_strength: int` - 信号强度 (dBm)
- `occupancy: float` - 占用率 (0-100)
- `interference: float` - 干扰程度 (0-100)
- `networks: List[str]` - 网络列表

**方法**：
```python
def get_quality_score(self) -> float
    # 计算信道质量评分
    # 返回值范围: 0-100
    # 算法: 100 - occupancy*0.5 - interference*0.3 + (signal_strength+100)*0.2
```

**使用示例**：
```python
from src.models.data_models import ChannelInfo

channel = ChannelInfo(
    channel=6,
    frequency=2.437,
    band="2.4GHz",
    signal_strength=-45,
    occupancy=30.0,
    interference=20.0,
    networks=["MyWiFi", "NeighborWiFi"]
)
score = channel.get_quality_score()
print(f"信道质量评分: {score:.1f}")
```

---

### ChannelTestData

信道测试数据模型

**属性**：
- `channel: int` - 信道
- `band: str` - 频段
- `rssi: int` - 信号强度 (dBm)
- `snr: float` - 信噪比 (dB)
- `bandwidth: float` - 带宽 (MHz)
- `throughput: float` - 传输速率 (Mbps)
- `packet_loss: float` - 丢包率 (%)
- `timestamp: datetime` - 时间戳

**方法**：
```python
def __str__(self) -> str
    # 返回格式化的测试数据字符串
    # 示例: "信道 6: RSSI=-45dBm, SNR=35dB, 带宽=20MHz, 速率=150Mbps, 丢包率=0.5%"
```

**使用示例**：
```python
from src.models.data_models import ChannelTestData
from datetime import datetime

test_data = ChannelTestData(
    channel=6,
    band="2.4GHz",
    rssi=-45,
    snr=35.0,
    bandwidth=20.0,
    throughput=150.0,
    packet_loss=0.5,
    timestamp=datetime.now()
)
print(test_data)
```

---

### ChannelRecommendation

信道推荐数据模型

**属性**：
- `channel: int` - 推荐信道
- `band: str` - 频段
- `quality_score: float` - 质量评分 (0-100)
- `reason: str` - 推荐理由
- `expected_improvement: str` - 预期改善
- `test_data: List[ChannelTestData]` - 测试数据
- `analysis_details: dict` - 分析详情

**方法**：
```python
def __str__(self) -> str
    # 返回格式化的推荐结果字符串
    # 示例: "推荐信道: 6 (2.4GHz) - 质量评分: 85.5"
```

**使用示例**：
```python
from src.models.data_models import ChannelRecommendation, ChannelTestData
from datetime import datetime

recommendation = ChannelRecommendation(
    channel=6,
    band="2.4GHz",
    quality_score=85.5,
    reason="该信道占用率低，信号强度高",
    expected_improvement="预计网络性能提升20%",
    test_data=[],
    analysis_details={}
)
print(recommendation)
```

## 🔧 服务API

### ConfigService

配置管理服务

**实例获取**：
```python
from src.services.config_service import config_service

# ConfigService是单例模式，直接使用实例
config_service.get('app.name')
```

**方法**：

#### get()
```python
def get(key: str, default: Any = None) -> Any
    """
    获取配置值
    
    参数:
        key: 配置键，支持点分隔的嵌套键 (如 'app.name')
        default: 默认值，当配置不存在时返回
    
    返回:
        配置值
    
    示例:
        app_name = config_service.get('app.name', 'Default App')
        test_count = config_service.get('wifi.test_count', 50)
    """
```

#### set()
```python
def set(key: str, value: Any) -> None
    """
    设置配置值
    
    参数:
        key: 配置键，支持点分隔的嵌套键 (如 'wifi.test_count')
        value: 配置值
    
    示例:
        config_service.set('wifi.test_count', 100)
        config_service.set('ui.theme', 'dark')
    """
```

#### save()
```python
def save() -> None
    """
    保存配置到文件
    
    示例:
        config_service.set('wifi.test_count', 100)
        config_service.save()
    """
```

#### get_app_name()
```python
def get_app_name() -> str
    """
    获取应用名称
    
    返回:
        应用名称字符串
    
    示例:
        name = config_service.get_app_name()
        print(name)  # 输出: "WiFi Speed Test"
    """
```

#### get_app_version()
```python
def get_app_version() -> str
    """
    获取应用版本
    
    返回:
        版本字符串
    
    示例:
        version = config_service.get_app_version()
        print(version)  # 输出: "1.0.0"
    """
```

#### get_test_count()
```python
def get_test_count() -> int
    """
    获取测试次数配置
    
    返回:
        测试次数 (默认50)
    
    示例:
        count = config_service.get_test_count()
        print(f"每个信道将执行 {count} 次测试")
    """
```

**配置结构**：
```json
{
  "app": {
    "name": "WiFi Speed Test",
    "version": "1.0.0"
  },
  "wifi": {
    "scan_interval": 5,
    "bands": ["2.4GHz", "5GHz"],
    "test_count": 50
  },
  "ui": {
    "chart_update_interval": 2000,
    "theme": "default"
  },
  "logging": {
    "level": "INFO",
    "max_file_size": 10485760,
    "backup_count": 5
  }
}
```

---

## 🎨 UI组件API

### MainWindow

主窗口组件

**初始化**：
```python
from src.ui.main_window import MainWindow

window = MainWindow()
window.show()
```

**信号**：
```python
# 无公开信号
```

**公共方法**：
```python
def _refresh_all(self) -> None
    """
    刷新所有标签页数据
    
    示例:
        window._refresh_all()
    """
```

---

### ChannelAnalysisPanel

信道分析面板

**初始化**：
```python
from src.ui.channel_analysis_panel import ChannelAnalysisPanel

panel = ChannelAnalysisPanel()
```

**信号**：
```python
scan_completed = pyqtSignal()
# 说明: 信道扫描完成时发送
# 参数: 无
# 使用:
    panel.scan_completed.connect(on_scan_completed)
    
    def on_scan_completed():
        print("扫描完成")
```

**公共方法**：
```python
def refresh(self) -> None
    """
    刷新信道数据
    
    示例:
        panel.refresh()
    """

def get_channels(self) -> List[ChannelInfo]
    """
    获取当前信道数据
    
    返回:
        信道信息列表
    
    示例:
        channels = panel.get_channels()
        for channel in channels:
            print(f"信道 {channel.channel}: {channel.get_quality_score()}")
    """
```

---

### RecommendPanel

信道推荐面板

**初始化**：
```python
from src.ui.recommend_panel import RecommendPanel

panel = RecommendPanel()
```

**信号**：
```python
scan_completed = pyqtSignal()
# 说明: 信道扫描完成时发送
# 参数: 无
# 使用:
    panel.scan_completed.connect(on_scan_completed)
    
    def on_scan_completed():
        print("扫描完成")
```

**公共方法**：
```python
def set_analysis_panel(self, panel: ChannelAnalysisPanel) -> None
    """
    设置关联的信道分析面板
    
    参数:
        panel: ChannelAnalysisPanel实例
    
    示例:
        recommend_panel.set_analysis_panel(analysis_panel)
    """
```

---

## 🛠️ 工具API

### Logger

日志记录工具

**初始化**：
```python
from src.utils.logger import logger

# Logger是全局单例，直接使用
logger.info("Information message")
```

**方法**：

#### debug()
```python
def debug(message: str, *args, **kwargs) -> None
    """
    记录DEBUG级别日志
    
    参数:
        message: 日志消息
        *args: 格式化参数
        **kwargs: 额外参数 (如 exc_info=True 记录异常堆栈)
    
    示例:
        logger.debug("Debug message")
        logger.debug("Value: %s", value)
        logger.debug("Error occurred", exc_info=True)
    """
```

#### info()
```python
def info(message: str, *args, **kwargs) -> None
    """
    记录INFO级别日志
    
    参数:
        message: 日志消息
        *args: 格式化参数
        **kwargs: 额外参数
    
    示例:
        logger.info("Application started")
        logger.info("User: %s", username)
    """
```

#### warning()
```python
def warning(message: str, *args, **kwargs) -> None
    """
    记录WARNING级别日志
    
    参数:
        message: 日志消息
        *args: 格式化参数
        **kwargs: 额外参数
    
    示例:
        logger.warning("Configuration file not found, using defaults")
    """
```

#### error()
```python
def error(message: str, *args, **kwargs) -> None
    """
    记录ERROR级别日志
    
    参数:
        message: 日志消息
        *args: 格式化参数
        **kwargs: 额外参数 (如 exc_info=True 记录异常堆栈)
    
    示例:
        logger.error("Failed to connect to server")
        logger.error("Exception occurred", exc_info=True)
    """
```

#### critical()
```python
def critical(message: str, *args, **kwargs) -> None
    """
    记录CRITICAL级别日志
    
    参数:
        message: 日志消息
        *args: 格式化参数
        **kwargs: 额外参数
    
    示例:
        logger.critical("System failure")
    """
```

---

### ExceptionHandler

异常处理工具

**初始化**：
```python
from src.utils.exception_handler import exception_handler, handle_exceptions

# exception_handler是全局单例，直接使用
exception_handler.show_warning("Warning", "Warning message")
```

**方法**：

#### show_warning()
```python
def show_warning(title: str, message: str) -> None
    """
    显示警告对话框
    
    参数:
        title: 对话框标题
        message: 警告消息
    
    示例:
        exception_handler.show_warning(
            "警告",
            "WiFi扫描失败，请检查权限"
        )
    """
```

#### show_error()
```python
def show_error(title: str, message: str) -> None
    """
    显示错误对话框
    
    参数:
        title: 对话框标题
        message: 错误消息
    
    示例:
        exception_handler.show_error(
            "错误",
            "无法连接到服务器"
        )
    """
```

#### handle_exceptions()
```python
def handle_exceptions(show_dialog: bool = True)
    """
    异常处理装饰器
    
    参数:
        show_dialog: 是否显示错误对话框
    
    使用:
        @handle_exceptions(show_dialog=True)
        def some_function():
            # 可能抛出异常的代码
            pass
    
    示例:
        @handle_exceptions(show_dialog=True)
        def risky_operation():
            result = 1 / 0  # 会抛出ZeroDivisionError
    """
```

#### setup_global_exception_handler()
```python
def setup_global_exception_handler() -> None
    """
    设置全局异常处理器
    
    示例:
        from src.utils.exception_handler import setup_global_exception_handler
        setup_global_exception_handler()
    """
```

---

## 🔄 信号-槽API

### ChannelAnalysisPanel信号

#### scan_completed
```python
scan_completed = pyqtSignal()

# 说明: 信道扫描完成时发送
# 参数: 无
# 连接示例:
    panel.scan_completed.connect(on_scan_completed)
    
    def on_scan_completed():
        print("信道扫描完成")
        channels = panel.get_channels()
```

---

### RecommendPanel信号

#### scan_completed
```python
scan_completed = pyqtSignal()

# 说明: 信道扫描完成时发送
# 参数: 无
# 连接示例:
    panel.scan_completed.connect(on_scan_completed)
    
    def on_scan_completed():
        print("信道扫描完成，准备推荐分析")
```

---

## 📊 数据流程API

### 信道扫描流程

```python
# 1. 触发扫描
panel.refresh()

# 2. 执行扫描 (内部自动执行)
# - 使用pywifi扫描WiFi网络
# - 采集信道数据
# - 计算信道质量评分

# 3. 更新UI (内部自动执行)
# - 更新图表
# - 更新表格

# 4. 发送完成信号 (内部自动执行)
# panel.scan_completed.emit()

# 5. 处理完成信号
def on_scan_completed():
    channels = panel.get_channels()
    for channel in channels:
        print(f"信道 {channel.channel}: {channel.get_quality_score()}")

panel.scan_completed.connect(on_scan_completed)
```

### 信道推荐流程

```python
# 1. 设置关联面板
recommend_panel.set_analysis_panel(analysis_panel)

# 2. 触发分析 (用户点击按钮)
# 内部自动执行:
# - 检查是否有信道数据
# - 如果没有，提示用户扫描
# - 如果有，启动分析线程

# 3. 执行分析 (内部自动执行)
# - 获取测试次数配置
# - 对每个信道执行N次测试
# - 采集测试数据
# - 计算算术平均值
# - 应用加权算法
# - 生成推荐结果

# 4. 更新UI (内部自动执行)
# - 显示推荐卡片
# - 显示测试数据表格
# - 显示分析详情
```

---

## 🔐 权限要求

### WiFi扫描权限

**要求**: 管理员权限

**原因**: Windows系统要求管理员权限才能访问WiFi适配器进行网络扫描

**处理方式**:
```python
try:
    # 尝试执行WiFi扫描
    wifi.scan()
except PermissionError:
    # 权限不足，显示提示
    exception_handler.show_warning(
        "权限不足",
        "请以管理员身份运行程序"
    )
```

---

## 📝 使用示例

### 完整示例

```python
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.exception_handler import setup_global_exception_handler
from src.services.config_service import config_service
from src.utils.logger import logger

def main():
    # 设置全局异常处理器
    setup_global_exception_handler()
    
    # 创建应用
    app = QApplication([])
    
    # 获取配置
    app_name = config_service.get_app_name()
    app_version = config_service.get_app_version()
    
    # 记录日志
    logger.info(f"{app_name} v{app_version} starting")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    app.exec_()

if __name__ == '__main__':
    main()
```

---

## 📚 相关文档

- [技术架构文档](TECHNICAL.md)
- [使用教程](USER_GUIDE.md)
- [常见问题](FAQ.md)

---

**文档版本**：1.0.0  
**最后更新**：2026-02-08  
**维护者**：WiFi Test Team
