@echo off
cd /d "%~dp0"
echo 正在启动...
python -m streamlit run app.py
if %errorlevel% neq 0 (
    echo 启动失败，尝试安装依赖...
    pip install streamlit pillow
    echo 依赖安装完成，重新启动...
    python -m streamlit run app.py
)
pause
