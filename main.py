import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow
from src.utils.logger import logger
from src.utils.exception_handler import setup_global_exception_handler
from src.services.config_service import config_service


def main():
    setup_global_exception_handler()
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName(config_service.get_app_name())
    app.setApplicationVersion(config_service.get_app_version())
    
    try:
        window = MainWindow()
        window.show()
        
        logger.info(f"{config_service.get_app_name()} started successfully")
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
