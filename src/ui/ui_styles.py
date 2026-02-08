"""
UI样式配置模块
提供统一的UI样式和设计规范
"""

from PyQt5.QtGui import QFont


class UIStyles:
    """UI样式常量类"""
    
    # 颜色方案 - 现代配色
    COLORS = {
        # 主色调
        'primary': '#2196F3',           # 现代蓝色
        'primary_dark': '#1976D2',       # 深蓝色
        'primary_light': '#BBDEFB',       # 浅蓝色
        
        # 功能色
        'success': '#4CAF50',            # 柔和绿色
        'success_dark': '#388E3C',       # 深绿色
        'warning': '#FF9800',            # 明亮橙色
        'warning_dark': '#F57C00',       # 深橙色
        'error': '#F44336',             # 醒目红色
        'error_dark': '#D32F2F',        # 深红色
        
        # 中性色
        'background': '#F5F5F5',         # 柔和浅灰背景
        'surface': '#FFFFFF',             # 白色表面
        'text_primary': '#212121',        # 主要文字
        'text_secondary': '#757575',      # 次要文字
        'text_hint': '#BDBDBD',          # 提示文字
        'divider': '#E0E0E0',           # 分割线
        'border': '#E0E0E0',            # 边框
        
        # 特殊色
        'overlay': 'rgba(0, 0, 0, 0.0.5)',  # 遮罩层
        'shadow': 'rgba(0, 0, 0, 0.1)',     # 阴影
    }
    
    # 字体系统
    FONTS = {
        'family': 'Microsoft YaHei UI',  # 微软雅黑
        'size': {
            'h1': 24,      # 一级标题
            'h2': 20,      # 二级标题
            'h3': 16,      # 三级标题
            'body': 14,     # 正文
            'caption': 12,   # 说明文字
            'small': 10,     # 小字
        },
        'weight': {
            'bold': 'bold',
            'normal': 'normal',
            'light': '300',
        }
    }
    
    # 间距系统
    SPACING = {
        'xs': 4,       # 极小间距
        'sm': 8,       # 小间距
        'md': 16,      # 中等间距
        'lg': 24,      # 大间距
        'xl': 32,      # 超大间距
    }
    
    # 圆角
    RADIUS = {
        'sm': 4,       # 小圆角
        'md': 8,       # 中等圆角
        'lg': 12,      # 大圆角
        'xl': 16,      # 超大圆角
    }
    
    # 阴影
    SHADOWS = {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.1)',
        'md': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'lg': '0 4px 8px rgba(0, 0, 0, 0.1)',
        'xl': '0 8px 16px rgba(0, 0, 0, 0.1)',
    }
    
    # 按钮样式
    BUTTON_STYLES = {
        'primary': f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['bold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
                box-shadow: {SHADOWS['md']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_dark']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
                box-shadow: {SHADOWS['sm']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['text_hint']};
                color: {COLORS['text_secondary']};
            }}
        """,
        
        'secondary': f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['bold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
                border-color: {COLORS['primary_dark']};
                box-shadow: {SHADOWS['md']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_light']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
                box-shadow: {SHADOWS['sm']};
            }}
        """,
        
        'success': f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['bold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
                box-shadow: {SHADOWS['md']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['success_dark']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
                box-shadow: {SHADOWS['sm']};
            }}
        """,
        
        'danger': f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['bold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error_dark']};
                box-shadow: {SHADOWS['md']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['error_dark']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
                box-shadow: {SHADOWS['sm']};
            }}
        """,
        
        'warning': f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                border: none;
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['bold']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['warning_dark']};
                box-shadow: {SHADOWS['md']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['warning_dark']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
                box-shadow: {SHADOWS['sm']};
            }}
        """,
        
        'outline': f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['normal']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
                border-color: {COLORS['text_secondary']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['background']};
                padding: {SPACING['sm']}px {SPACING['lg']-2}px;
            }}
        """,
        
        'text': f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['primary']};
                border: none;
                border-radius: {RADIUS['sm']}px;
                padding: {SPACING['sm']}px {SPACING['md']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['normal']};
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_light']};
                padding: {SPACING['sm']}px {SPACING['md']-2}px;
            }}
        """,
        
        'icon': f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: {RADIUS['sm']}px;
                padding: {SPACING['sm']}px;
                font-size: {FONTS['size']['body']}px;
                min-width: 40px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['background']};
                padding: {SPACING['sm']-1}px;
            }}
        """,
        
        'toggle': f"""
            QPushButton {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['normal']};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface']};
                border-color: {COLORS['text_secondary']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: white;
                border-color: {COLORS['primary']};
                font-weight: {FONTS['weight']['bold']};
            }}
            QPushButton:checked:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """,
        
        'fab': f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 28px;
                padding: 0;
                font-size: {FONTS['size']['h2']}px;
                min-width: 56px;
                min-height: 56px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
                box-shadow: {SHADOWS['lg']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary_dark']};
                box-shadow: {SHADOWS['md']};
            }}
        """,
    }
    
    # 卡片样式
    CARD_STYLES = {
        'default': f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: {RADIUS['lg']}px;
                border: 1px solid {COLORS['border']};
                padding: {SPACING['lg']}px;
            }}
        """,
        
        'elevated': f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: {RADIUS['lg']}px;
                border: 1px solid {COLORS['border']};
                padding: {SPACING['lg']}px;
            }}
        """,
    }
    
    # 分组框样式
    GROUP_BOX_STYLES = {
        'default': f"""
            QGroupBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                margin-top: {SPACING['md']}px;
                padding-top: {SPACING['md']}px;
                font-size: {FONTS['size']['h3']}px;
                font-weight: {FONTS['weight']['bold']};
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {SPACING['md']}px;
                padding: 0 {SPACING['sm']}px 0 {SPACING['sm']}px;
            }}
        """
    }
    
    # 表格样式
    TABLE_STYLES = {
        'default': f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                gridline-color: {COLORS['divider']};
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['text_primary']};
                alternate-background-color: {COLORS['background']};
                outline: none;
            }}
            QTableWidget::item {{
                padding: {SPACING['sm']}px {SPACING['md']}px;
                border: none;
                border-bottom: 1px solid {COLORS['divider']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['background']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
                padding: {SPACING['md']}px {SPACING['lg']}px;
                border: none;
                border-bottom: 2px solid {COLORS['primary']};
                border-top-left-radius: {RADIUS['sm']}px;
                border-top-right-radius: {RADIUS['sm']}px;
                font-weight: {FONTS['weight']['bold']};
                font-size: {FONTS['size']['body']}px;
            }}
            QHeaderView::section:hover {{
                background-color: {COLORS['primary_light']};
            }}
            QTableWidget QTableCornerButton::section {{
                background-color: {COLORS['background']};
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['background']};
                width: 12px;
                border-radius: {RADIUS['sm']}px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['text_hint']};
                min-height: 20px;
                border-radius: {RADIUS['sm']}px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {COLORS['background']};
                height: 12px;
                border-radius: {RADIUS['sm']}px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['text_hint']};
                min-width: 20px;
                border-radius: {RADIUS['sm']}px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """,
        
        'compact': f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
                gridline-color: {COLORS['divider']};
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['text_primary']};
                alternate-background-color: {COLORS['background']};
                outline: none;
            }}
            QTableWidget::item {{
                padding: {SPACING['xs']}px {SPACING['sm']}px;
                border: none;
                border-bottom: 1px solid {COLORS['divider']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['background']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
                padding: {SPACING['sm']}px {SPACING['md']}px;
                border: none;
                border-bottom: 2px solid {COLORS['primary']};
                border-top-left-radius: {RADIUS['sm']}px;
                border-top-right-radius: {RADIUS['sm']}px;
                font-weight: {FONTS['weight']['bold']};
                font-size: {FONTS['size']['caption']}px;
            }}
            QHeaderView::section:hover {{
                background-color: {COLORS['primary_light']};
            }}
            QTableWidget QTableCornerButton::section {{
                background-color: {COLORS['background']};
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['background']};
                width: 10px;
                border-radius: {RADIUS['sm']}px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['text_hint']};
                min-height: 20px;
                border-radius: {RADIUS['sm']}px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {COLORS['background']};
                height: 10px;
                border-radius: {RADIUS['sm']}px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {COLORS['text_hint']};
                min-width: 20px;
                border-radius: {RADIUS['sm']}px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
    }
    
    # 进度条样式
    PROGRESS_BAR_STYLES = {
        'default': f"""
            QProgressBar {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
                text-align: center;
                height: 24px;
                font-weight: {FONTS['weight']['bold']};
                color: {COLORS['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: {RADIUS['sm']}px;
            }}
        """,
        
        'success': f"""
            QProgressBar {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
                text-align: center;
                height: 24px;
                font-weight: {FONTS['weight']['bold']};
                color: {COLORS['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['success']};
                border-radius: {RADIUS['sm']}px;
            }}
        """
    }
    
    # 标签页样式
    TAB_WIDGET_STYLES = {
        'default': f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: {COLORS['surface']};
                border-radius: {RADIUS['md']}px;
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                border: none;
                border-top-left-radius: {RADIUS['md']}px;
                border-top-right-radius: {RADIUS['md']}px;
                margin-right: {SPACING['xs']}px;
                font-size: {FONTS['size']['body']}px;
                font-weight: {FONTS['weight']['normal']};
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['surface']};
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
                font-weight: {FONTS['weight']['bold']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """
    }
    
    # 输入框样式
    INPUT_STYLES = {
        'default': f"""
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
                padding: {SPACING['sm']}px {SPACING['md']}px;
                font-size: {FONTS['size']['body']}px;
                color: {COLORS['text_primary']};
                min-height: 40px;
            }}
            QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {COLORS['primary']};
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['surface']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLORS['text_secondary']};
                width: 0;
                height: 0;
            }}
        """
    }
    
    # 复选框样式
    CHECKBOX_STYLES = {
        'default': f"""
            QCheckBox {{
                spacing: {SPACING['sm']}px;
                color: {COLORS['text_primary']};
                font-size: {FONTS['size']['body']}px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
                background-color: {COLORS['surface']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['primary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
                image: none;
            }}
        """
    }
    
    @classmethod
    def get_font(cls, size_key: str = 'body', weight: str = 'normal') -> QFont:
        """获取字体对象"""
        from PyQt5.QtGui import QFont
        size = cls.FONTS['size'].get(size_key, cls.FONTS['size']['body'])
        font_weight_str = cls.FONTS['weight'].get(weight, cls.FONTS['weight']['normal'])
        
        weight_map = {
            'light': 25,
            'normal': 50,
            'bold': 75
        }
        font_weight = weight_map.get(font_weight_str, 50)
        
        font = QFont(cls.FONTS['family'], size)
        font.setWeight(font_weight)
        return font
    
    @classmethod
    def apply_stylesheet(cls, widget, style_name: str):
        """应用样式到组件"""
        if style_name == 'button_primary':
            widget.setStyleSheet(cls.BUTTON_STYLES['primary'])
        elif style_name == 'button_secondary':
            widget.setStyleSheet(cls.BUTTON_STYLES['secondary'])
        elif style_name == 'button_success':
            widget.setStyleSheet(cls.BUTTON_STYLES['success'])
        elif style_name == 'button_danger':
            widget.setStyleSheet(cls.BUTTON_STYLES['danger'])
        elif style_name == 'button_warning':
            widget.setStyleSheet(cls.BUTTON_STYLES['warning'])
        elif style_name == 'button_outline':
            widget.setStyleSheet(cls.BUTTON_STYLES['outline'])
        elif style_name == 'button_text':
            widget.setStyleSheet(cls.BUTTON_STYLES['text'])
        elif style_name == 'button_icon':
            widget.setStyleSheet(cls.BUTTON_STYLES['icon'])
        elif style_name == 'button_toggle':
            widget.setStyleSheet(cls.BUTTON_STYLES['toggle'])
        elif style_name == 'button_fab':
            widget.setStyleSheet(cls.BUTTON_STYLES['fab'])
        elif style_name == 'card':
            widget.setStyleSheet(cls.CARD_STYLES['default'])
        elif style_name == 'group_box':
            widget.setStyleSheet(cls.GROUP_BOX_STYLES['default'])
        elif style_name == 'table':
            widget.setStyleSheet(cls.TABLE_STYLES['default'])
        elif style_name == 'table_compact':
            widget.setStyleSheet(cls.TABLE_STYLES['compact'])
        elif style_name == 'progress_bar':
            widget.setStyleSheet(cls.PROGRESS_BAR_STYLES['default'])
        elif style_name == 'tab_widget':
            widget.setStyleSheet(cls.TAB_WIDGET_STYLES['default'])
        elif style_name == 'input':
            widget.setStyleSheet(cls.INPUT_STYLES['default'])
        elif style_name == 'checkbox':
            widget.setStyleSheet(cls.CHECKBOX_STYLES['default'])
