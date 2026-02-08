@echo off
chcp 65001 >nul
echo ========================================
echo    WiFi Speed Test 启动程序
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python环境检查通过
echo.

REM 检查是否为管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [警告] 当前不是管理员权限
    echo [提示] WiFi扫描功能需要管理员权限
    echo [提示] 建议右键点击此文件，选择"以管理员身份运行"
    echo.
    set /p continue="是否继续运行？(Y/N): "
    if /i not "%continue%"=="Y" (
        echo [信息] 程序已取消
        pause
        exit /b 0
    )
)

echo [信息] 正在启动程序...
echo.

REM 启动程序
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
    exit /b 1
)

echo.
echo [信息] 程序已正常退出
pause
