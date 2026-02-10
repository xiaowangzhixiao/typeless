#!/bin/bash

# 停止 Typeless Mac 应用
echo "🛑 正在停止 Typeless Mac..."

# 查找并停止所有相关进程
pkill -9 -f "typeless-mac/main.py"
pkill -9 -f "typeless-mac/.venv"
pkill -9 -f "uv run python3 main.py"

# 等待进程完全停止
sleep 1

# 检查是否还有进程在运行
if pgrep -f "typeless-mac/main.py" > /dev/null; then
    echo "⚠️  警告：部分进程可能仍在运行"
    echo "请手动执行：pkill -9 -f typeless-mac"
else
    echo "✅ Typeless Mac 已成功停止"
fi
