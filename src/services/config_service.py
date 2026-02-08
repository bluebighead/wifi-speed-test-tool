import json
import os
from typing import Any, Dict, Optional
from src.utils.logger import logger


class ConfigService:
    _instance: Optional['ConfigService'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self._load_config()
    
    def _load_config(self):
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'config.json'
            )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "app": {
                "name": "WiFi Speed Test",
                "version": "1.0.0"
            },
            "network": {
                "test_servers": [],
                "upload_server": "",
                "ping_server": "8.8.8.8",
                "timeout": 30,
                "retry_count": 3
            },
            "wifi": {
                "scan_interval": 5,
                "bands": ["2.4GHz", "5GHz"],
                "test_count": 50
            },
            "ui": {
                "refresh_interval": 1000,
                "chart_update_interval": 2000,
                "theme": "default"
            },
            "logging": {
                "level": "INFO",
                "file": "wifi_test.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Config updated: {key} = {value}")
    
    def save(self):
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'config.json'
            )
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_app_name(self) -> str:
        return self.get('app.name', 'WiFi Speed Test')
    
    def get_app_version(self) -> str:
        return self.get('app.version', '1.0.0')
    
    def get_test_servers(self) -> list:
        return self.get('network.test_servers', [])
    
    def get_upload_server(self) -> str:
        return self.get('network.upload_server', '')
    
    def get_ping_server(self) -> str:
        return self.get('network.ping_server', '8.8.8.8')
    
    def get_network_timeout(self) -> int:
        return self.get('network.timeout', 30)
    
    def get_retry_count(self) -> int:
        return self.get('network.retry_count', 3)
    
    def get_scan_interval(self) -> int:
        return self.get('wifi.scan_interval', 5)
    
    def get_bands(self) -> list:
        return self.get('wifi.bands', ['2.4GHz', '5GHz'])
    
    def get_channels_2_4ghz(self) -> list:
        return self.get('wifi.channels_2.4ghz', list(range(1, 15)))
    
    def get_channels_5ghz(self) -> list:
        return self.get('wifi.channels_5ghz', [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165])
    
    def get_refresh_interval(self) -> int:
        return self.get('ui.refresh_interval', 1000)
    
    def get_chart_update_interval(self) -> int:
        return self.get('ui.chart_update_interval', 2000)
    
    def get_theme(self) -> str:
        return self.get('ui.theme', 'default')
    
    def get_test_count(self) -> int:
        return self.get('wifi.test_count', 50)


config_service = ConfigService()
