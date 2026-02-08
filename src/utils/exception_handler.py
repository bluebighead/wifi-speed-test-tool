import sys
from PyQt5.QtWidgets import QMessageBox
from typing import Optional, Callable
from functools import wraps
from src.utils.logger import logger


class ExceptionHandler:
    _instance: Optional['ExceptionHandler'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._error_callbacks = []
    
    def register_error_callback(self, callback: Callable[[Exception], None]):
        self._error_callbacks.append(callback)
    
    def handle_exception(self, exc: Exception, show_dialog: bool = True):
        logger.error(f"Exception occurred: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        for callback in self._error_callbacks:
            try:
                callback(exc)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
        
        if show_dialog:
            self._show_error_dialog(exc)
    
    def _show_error_dialog(self, exc: Exception):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("错误")
        
        error_type = type(exc).__name__
        error_msg = str(exc)
        
        if error_type == "PermissionError":
            msg_box.setText("权限不足")
            msg_box.setInformativeText("需要管理员权限才能执行此操作。\n请以管理员身份运行程序。")
        elif error_type == "ConnectionError":
            msg_box.setText("网络连接失败")
            msg_box.setInformativeText("无法连接到网络，请检查网络设置。")
        elif error_type == "TimeoutError":
            msg_box.setText("操作超时")
            msg_box.setInformativeText("操作超时，请稍后重试。")
        else:
            msg_box.setText("发生错误")
            msg_box.setInformativeText(f"{error_type}: {error_msg}")
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_warning(self, title: str, message: str):
        logger.warning(f"Warning: {title} - {message}")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_info(self, title: str, message: str):
        logger.info(f"Info: {title} - {message}")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def show_question(self, title: str, message: str) -> bool:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec_() == QMessageBox.Yes


def handle_exceptions(show_dialog: bool = True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ExceptionHandler()
                handler.handle_exception(e, show_dialog)
                return None
        return wrapper
    return decorator


exception_handler = ExceptionHandler()


def setup_global_exception_handler():
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error(
            f"Uncaught exception: {exc_type.__name__}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        exception_handler.handle_exception(exc_value, show_dialog=False)
    
    sys.excepthook = global_exception_handler
