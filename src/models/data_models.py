from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class SpeedTestResult:
    download_speed: float
    upload_speed: float
    latency: float
    jitter: float
    timestamp: datetime
    server: str
    
    def __str__(self):
        return f"下载: {self.download_speed:.2f} Mbps, 上传: {self.upload_speed:.2f} Mbps, 延迟: {self.latency:.2f} ms"


@dataclass
class NetworkInfo:
    ssid: str
    bssid: str
    signal_strength: int
    channel: int
    frequency: float
    encryption_type: str
    
    def __str__(self):
        return f"{self.ssid} (信道: {self.channel}, 信号: {self.signal_strength} dBm)"


@dataclass
class ChannelInfo:
    channel: int
    frequency: float
    band: str
    signal_strength: int
    occupancy: float
    interference: float
    networks: List[str]
    
    def get_quality_score(self) -> float:
        score = 100.0
        score -= self.occupancy * 0.5
        score -= self.interference * 0.3
        score += (self.signal_strength + 100) * 0.2
        return max(0.0, min(100.0, score))


@dataclass
class ChannelTestData:
    channel: int
    band: str
    rssi: int
    snr: float
    bandwidth: float
    throughput: float
    packet_loss: float
    timestamp: datetime
    
    def __str__(self):
        return f"信道 {self.channel}: RSSI={self.rssi}dBm, SNR={self.snr}dB, 带宽={self.bandwidth}MHz, 速率={self.throughput}Mbps, 丢包率={self.packet_loss}%"


@dataclass
class ChannelRecommendation:
    channel: int
    band: str
    quality_score: float
    reason: str
    expected_improvement: str
    test_data: List[ChannelTestData]
    analysis_details: dict
    
    def __str__(self):
        return f"推荐信道: {self.channel} ({self.band}) - 质量评分: {self.quality_score:.1f}"
