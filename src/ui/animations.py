"""
UI动画效果模块
提供统一的动画效果和过渡动画
"""

from PyQt5.QtCore import (QPropertyAnimation, QEasingCurve, QTimer, 
                         QParallelAnimationGroup, QSequentialAnimationGroup,
                         QObject, pyqtSignal, pyqtProperty)
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QColor


class AnimationHelper(QObject):
    """动画辅助类"""
    
    animation_completed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animations = []
    
    def fade_in(self, widget: QWidget, duration: int = 300):
        """淡入动画"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self._animations.append(animation)
        return animation
    
    def fade_out(self, widget: QWidget, duration: int = 300):
        """淡出动画"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(1)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self._animations.append(animation)
        return animation
    
    def slide_in_left(self, widget: QWidget, duration: int = 400):
        """从左侧滑入"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(widget.geometry().translated(-widget.width(), 0))
        animation.setEndValue(widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._animations.append(animation)
        return animation
    
    def slide_in_right(self, widget: QWidget, duration: int = 400):
        """从右侧滑入"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(widget.geometry().translated(widget.width(), 0))
        animation.setEndValue(widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._animations.append(animation)
        return animation
    
    def slide_in_top(self, widget: QWidget, duration: int = 400):
        """从顶部滑入"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(widget.geometry().translated(0, -widget.height()))
        animation.setEndValue(widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._animations.append(animation)
        return animation
    
    def slide_in_bottom(self, widget: QWidget, duration: int = 400):
        """从底部滑入"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(widget.geometry().translated(0, widget.height()))
        animation.setEndValue(widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._animations.append(animation)
        return animation
    
    def scale_in(self, widget: QWidget, duration: int = 300):
        """缩放进入动画"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        center = widget.geometry().center()
        start_geometry = widget.geometry()
        start_geometry.setWidth(0)
        start_geometry.setHeight(0)
        start_geometry.moveCenter(center)
        
        animation.setStartValue(start_geometry)
        animation.setEndValue(widget.geometry())
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        self._animations.append(animation)
        return animation
    
    def bounce(self, widget: QWidget, duration: int = 500):
        """弹跳动画"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        original_geometry = widget.geometry()
        center = original_geometry.center()
        
        animation.setStartValue(original_geometry)
        animation.setKeyValueAt(0.5, original_geometry.translated(0, -20))
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(QEasingCurve.OutBounce)
        
        self._animations.append(animation)
        return animation
    
    def pulse(self, widget: QWidget, duration: int = 1000, repeat: int = 1):
        """脉冲动画"""
        group = QParallelAnimationGroup()
        
        scale_animation = QPropertyAnimation(widget, b"geometry")
        scale_animation.setDuration(duration // 2)
        scale_animation.setLoopCount(repeat)
        
        original_geometry = widget.geometry()
        center = original_geometry.center()
        
        scaled_geometry = original_geometry
        scaled_geometry.setWidth(int(original_geometry.width() * 1.05))
        scaled_geometry.setHeight(int(original_geometry.height() * 1.05))
        scaled_geometry.moveCenter(center)
        
        scale_animation.setStartValue(original_geometry)
        scale_animation.setKeyValueAt(0.5, scaled_geometry)
        scale_animation.setEndValue(original_geometry)
        scale_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        group.addAnimation(scale_animation)
        self._animations.append(group)
        return group
    
    def shake(self, widget: QWidget, duration: int = 500):
        """抖动动画"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        
        original_geometry = widget.geometry()
        
        animation.setStartValue(original_geometry)
        animation.setKeyValueAt(0.125, original_geometry.translated(-10, 0))
        animation.setKeyValueAt(0.375, original_geometry.translated(10, 0))
        animation.setKeyValueAt(0.625, original_geometry.translated(-10, 0))
        animation.setKeyValueAt(0.875, original_geometry.translated(10, 0))
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(QEasingCurve.InOutSine)
        
        self._animations.append(animation)
        return animation
    
    def sequential_fade(self, widgets: list, duration: int = 300, delay: int = 100):
        """顺序淡入动画"""
        group = QSequentialAnimationGroup()
        
        for i, widget in enumerate(widgets):
            fade_animation = self.fade_in(widget, duration)
            if i > 0:
                delay_timer = QTimer()
                delay_timer.setSingleShot(True)
                delay_timer.timeout.connect(fade_animation.start)
                delay_timer.start(i * delay)
            else:
                group.addAnimation(fade_animation)
        
        self._animations.append(group)
        return group
    
    def clear_animations(self):
        """清除所有动画"""
        for animation in self._animations:
            if animation.state() == animation.Running:
                animation.stop()
        self._animations.clear()


class AnimatedWidget(QWidget):
    """带动画效果的组件基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation_helper = AnimationHelper(self)
    
    def show_animated(self, animation_type: str = "fade_in", duration: int = 300):
        """带动画显示"""
        self.show()
        
        if animation_type == "fade_in":
            animation = self._animation_helper.fade_in(self, duration)
        elif animation_type == "slide_in_left":
            animation = self._animation_helper.slide_in_left(self, duration)
        elif animation_type == "slide_in_right":
            animation = self._animation_helper.slide_in_right(self, duration)
        elif animation_type == "slide_in_top":
            animation = self._animation_helper.slide_in_top(self, duration)
        elif animation_type == "slide_in_bottom":
            animation = self._animation_helper.slide_in_bottom(self, duration)
        elif animation_type == "scale_in":
            animation = self._animation_helper.scale_in(self, duration)
        else:
            animation = self._animation_helper.fade_in(self, duration)
        
        animation.start()
        return animation
    
    def hide_animated(self, animation_type: str = "fade_out", duration: int = 300):
        """带动画隐藏"""
        if animation_type == "fade_out":
            animation = self._animation_helper.fade_out(self, duration)
        else:
            animation = self._animation_helper.fade_out(self, duration)
        
        animation.finished.connect(self.hide)
        animation.start()
        return animation
    
    def bounce_animation(self, duration: int = 500):
        """执行弹跳动画"""
        animation = self._animation_helper.bounce(self, duration)
        animation.start()
        return animation
    
    def shake_animation(self, duration: int = 500):
        """执行抖动动画"""
        animation = self._animation_helper.shake(self, duration)
        animation.start()
        return animation
    
    def pulse_animation(self, duration: int = 1000, repeat: int = 1):
        """执行脉冲动画"""
        animation = self._animation_helper.pulse(self, duration, repeat)
        animation.start()
        return animation