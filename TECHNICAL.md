# 技术架构文档

## 📋 文档概述

本文档详细描述了WiFi Speed Test Tool的技术架构、模块设计、数据流程和接口规范，为开发者提供全面的技术参考。

## 🏗️ 系统架构

### 整体架构

WiFi Speed Test Tool采用分层架构设计，遵循MVC（Model-View-Controller）模式，确保代码的可维护性和可扩展性。

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                  │
│                   (UI Components)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │   Main       │  │   Channel    │  │  Recommend  ││
│  │   Window     │  │   Analysis   │  │    Panel    ││
│  └──────────────┘  └──────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Business Logic Layer                  │
│                    (Services & Managers)                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │   Config     │  │   WiFi       │  │   Analysis  ││
│  │   Service    │  │   Manager    │  │   Manager   ││
│  └──────────────┘  └──────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                        │
│                    (Models & Utils)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│
│  │   Data       │  │   Logger     │  │  Exception  ││
│  │   Models     │  │   Service    │  │   Handler   ││
│  └──────────────┘  └──────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────┘
```

### 架构特点

1. **分层清晰**：UI层、业务逻辑层、数据层职责明确
2. **低耦合**：模块间通过接口通信，降低耦合度
3. **高内聚**：每个模块专注于特定功能
4. **可扩展**：采用插件化设计，便于功能扩展

## 📦 模块设计

### 1. UI层 (src/ui/)

#### MainWindow
**职责**：应用程序主窗口，负责整体布局和标签页管理

**主要功能**：
- 创建菜单栏和状态栏
- 管理多个功能标签页
- 处理全局快捷键
- 协调各面板间的通信

**关键方法**：
```python
def _setup_ui()              # 初始化UI
def _create_menu_bar()       # 创建菜单栏
def _create_central_widget() # 创建中央组件
def _create_status_bar()     # 创建状态栏
def _refresh_all()          # 刷新所有数据
```

#### ChannelAnalysisPanel
**职责**：信道分析面板，负责信道扫描和数据展示

**主要功能**：
- 执行WiFi信道扫描
- 展示信道占用图表
- 显示信道详情表格
- 支持自动刷新功能

**关键方法**：
```python
def refresh()                    # 刷新信道数据
def _scan_channels()             # 扫描信道
def _update_chart()              # 更新图表
def _update_table()              # 更新表格
def _on_auto_refresh_toggled()   # 处理自动刷新
```

**关键信号**：
```python
scan_completed = pyqtSignal()   # 扫描完成信号
```

#### RecommendPanel
**职责**：信道推荐面板，负责信道测试和推荐

**主要功能**：
- 执行信道质量测试
- 计算信道质量评分
- 展示推荐结果
- 支持频段切换

**关键方法**：
```python
def _start_analysis()            # 开始分析
def _execute_channel_scan()      # 执行信道扫描
def _on_recommendation_completed() # 处理推荐完成
def _update_recommendation_display() # 更新推荐显示
def _on_band_toggled()          # 处理频段切换
def _on_test_count_clicked()    # 处理测试次数设置
```

**关键信号**：
```python
scan_completed = pyqtSignal()    # 扫描完成信号
```

### 2. 服务层 (src/services/)

#### ConfigService
**职责**：配置管理服务，负责配置的加载、保存和访问

**主要功能**：
- 加载配置文件
- 保存配置修改
- 提供配置访问接口
- 配置持久化

**关键方法**：
```python
def get(key, default=None)      # 获取配置值
def set(key, value)              # 设置配置值
def save()                      # 保存配置
def get_app_name()               # 获取应用名称
def get_app_version()            # 获取应用版本
def get_test_count()             # 获取测试次数
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

### 3. 数据层 (src/models/)

#### 数据模型

**SpeedTestResult**
```python
@dataclass
class SpeedTestResult:
    download_speed: float    # 下载速度 (Mbps)
    upload_speed: float     # 上传速度 (Mbps)
    latency: float          # 延迟 (ms)
    jitter: float           # 抖动 (ms)
    timestamp: datetime     # 时间戳
    server: str             # 测速服务器
```

**NetworkInfo**
```python
@dataclass
class NetworkInfo:
    ssid: str              # 网络名称
    bssid: str             # MAC地址
    signal_strength: int    # 信号强度 (dBm)
    channel: int           # 信道
    frequency: float       # 频率 (GHz)
    encryption_type: str   # 加密类型
```

**ChannelInfo**
```python
@dataclass
class ChannelInfo:
    channel: int           # 信道
    frequency: float       # 频率 (GHz)
    band: str             # 频段
    signal_strength: int  # 信号强度 (dBm)
    occupancy: float      # 占用率 (0-100)
    interference: float   # 干扰程度 (0-100)
    networks: List[str]   # 网络列表
    
    def get_quality_score(self) -> float:
        # 计算信道质量评分
        score = 100.0
        score -= self.occupancy * 0.5
        score -= self.interference * 0.3
        score += (self.signal_strength + 100) * 0.2
        return max(0.0, min(100.0, score))
```

**ChannelTestData**
```python
@dataclass
class ChannelTestData:
    channel: int           # 信道
    band: str             # 频段
    rssi: int             # 信号强度 (dBm)
    snr: float            # 信噪比 (dB)
    bandwidth: float      # 带宽 (MHz)
    throughput: float      # 传输速率 (Mbps)
    packet_loss: float    # 丢包率 (%)
    timestamp: datetime   # 时间戳
```

**ChannelRecommendation**
```python
@dataclass
class ChannelRecommendation:
    channel: int                    # 推荐信道
    band: str                      # 频段
    quality_score: float            # 质量评分 (0-100)
    reason: str                    # 推荐理由
    expected_improvement: str       # 预期改善
    test_data: List[ChannelTestData] # 测试数据
    analysis_details: dict          # 分析详情
```

### 4. 工具层 (src/utils/)

#### Logger
**职责**：日志记录服务

**主要功能**：
- 配置日志格式
- 支持多级别日志
- 日志文件轮转
- 异常日志记录

**使用示例**：
```python
from src.utils.logger import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

#### ExceptionHandler
**职责**：异常处理服务

**主要功能**：
- 全局异常捕获
- 异常日志记录
- 用户友好的错误提示
- 异常恢复机制

**使用示例**：
```python
from src.utils.exception_handler import handle_exceptions

@handle_exceptions(show_dialog=True)
def some_function():
    # 可能抛出异常的代码
    pass
```

## 🔄 数据流程

### 信道分析流程

```
用户点击"扫描信道"
    ↓
ChannelAnalysisPanel.refresh()
    ↓
执行WiFi扫描 (pywifi)
    ↓
采集信道数据
    ↓
计算信道质量评分
    ↓
更新图表 (matplotlib)
    ↓
更新表格 (QTableWidget)
    ↓
发送scan_completed信号
    ↓
RecommendPanel接收信号
    ↓
准备信道推荐
```

### 信道推荐流程

```
用户点击"分析并推荐"
    ↓
检查是否有信道数据
    ↓
如果没有，提示用户扫描
    ↓
如果有，启动RecommendWorker线程
    ↓
对每个信道执行N次测试
    ↓
采集测试数据 (RSSI, SNR, 带宽, 速率, 丢包率)
    ↓
计算算术平均值
    ↓
应用加权算法计算评分
    ↓
生成推荐结果
    ↓
发送recommendation_completed信号
    ↓
更新UI显示推荐结果
```

### 配置更新流程

```
用户修改测试次数
    ↓
弹出输入对话框
    ↓
验证输入 (1-1000)
    ↓
保存到config.json
    ↓
更新UI显示
    ↓
下次测试使用新配置
```

## 🔌 接口设计

### 信号-槽机制

#### ChannelAnalysisPanel信号
```python
scan_completed = pyqtSignal()
# 说明：信道扫描完成时发送
# 接收方：RecommendPanel
```

#### RecommendPanel信号
```python
scan_completed = pyqtSignal()
# 说明：信道扫描完成时发送
# 接收方：RecommendPanel内部
```

### 数据访问接口

#### ConfigService接口
```python
class ConfigService:
    def get(key: str, default: Any = None) -> Any
    def set(key: str, value: Any) -> None
    def save() -> None
    def get_app_name() -> str
    def get_app_version() -> str
    def get_test_count() -> int
```

#### 数据模型接口
```python
class ChannelInfo:
    def get_quality_score(self) -> float
    # 返回信道质量评分 (0-100)
```

## 🎨 UI设计规范

### 颜色方案
- **主色调**：#3498db (蓝色)
- **成功色**：#27ae60 (绿色)
- **警告色**：#f39c12 (橙色)
- **错误色**：#e74c3c (红色)
- **背景色**：#f8f9fa (浅灰)
- **文字色**：#2c3e50 (深灰)

### 字体规范
- **标题**：Arial, 16pt, Bold
- **副标题**：Arial, 14pt, Bold
- **正文**：Arial, 11pt, Normal
- **小字**：Arial, 9pt, Normal

### 间距规范
- **组件间距**：10px
- **卡片内边距**：20px
- **按钮内边距**：5px 15px
- **表格行高**：30px

## 🚀 性能优化

### 1. 异步处理
- 使用QThread执行耗时操作
- 避免阻塞UI线程
- 信号-槽机制实现线程间通信

### 2. 数据优化
- 限制表格显示行数（最多50行）
- 使用分页或虚拟滚动
- 延迟加载大数据集

### 3. 图表优化
- 使用matplotlib的优化渲染
- 减少不必要的重绘
- 合理设置更新频率

### 4. 内存管理
- 及时释放不再使用的对象
- 使用弱引用避免循环引用
- 定期清理缓存数据

## 🔒 安全考虑

### 1. 权限管理
- WiFi扫描需要管理员权限
- 提供友好的权限提示
- 优雅处理权限不足情况

### 2. 数据验证
- 严格验证用户输入
- 防止SQL注入（虽然不使用数据库）
- 防止XSS攻击（虽然不涉及Web）

### 3. 异常处理
- 完善的异常捕获机制
- 不暴露敏感信息
- 提供用户友好的错误提示

## 📊 测试策略

### 单元测试
- 测试各个模块的独立功能
- 使用unittest或pytest框架
- 覆盖率目标：≥80%

### 集成测试
- 测试模块间的交互
- 测试数据流程
- 测试信号-槽机制

### UI测试
- 测试用户界面响应
- 测试用户交互流程
- 测试异常情况处理

## 🔄 版本控制

### Git工作流
- 使用Git进行版本控制
- 采用分支管理策略
- 规范的提交信息格式

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型(type)**：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关

## 📝 开发规范

### 代码风格
- 遵循PEP 8规范
- 使用类型提示
- 添加必要的注释
- 保持代码简洁清晰

### 命名规范
- **类名**：大驼峰命名法 (PascalCase)
- **函数名**：小写加下划线 (snake_case)
- **常量名**：大写加下划线 (UPPER_SNAKE_CASE)
- **私有成员**：前缀下划线 (_private)

### 文档规范
- 添加docstring说明函数用途
- 复杂逻辑添加注释
- 保持文档与代码同步

## 🔧 依赖管理

### 核心依赖
```
PyQt5>=5.15.0          # GUI框架
pywifi>=0.1.0          # WiFi操作
matplotlib>=3.5.0       # 图表绘制
requests>=2.28.0        # 网络请求
numpy>=1.21.0          # 数据处理
```

### 开发依赖
```
pytest>=7.0.0           # 测试框架
black>=22.0.0           # 代码格式化
flake8>=4.0.0           # 代码检查
mypy>=0.950            # 类型检查
```

## 📚 参考资料

- [PyQt5官方文档](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [pywifi文档](https://github.com/awkman/pywifi)
- [matplotlib文档](https://matplotlib.org/stable/contents.html)
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)

---

**文档版本**：1.0.0  
**最后更新**：2026-02-08  
**维护者**：WiFi Test Team
