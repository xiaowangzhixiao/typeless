#!/bin/bash

# Typeless Mac 启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 Typeless Mac..."
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "   请复制 .env.example 到 .env 并填入 API Key"
    echo ""
    read -p "是否现在创建 .env 文件？ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo "   请编辑 .env 文件，填入你的 OPENROUTER_API_KEY"
        echo "   然后重新运行: ./run.sh"
        exit 0
    else
        exit 1
    fi
fi

# 检查依赖
if ! python3 -c "import faster_whisper" 2>/dev/null; then
    echo "⚠️  依赖未安装"
    echo ""
    read -p "是否现在安装依赖？ (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 安装依赖..."
        pip3 install -r requirements.txt
        echo ""
    else
        echo "请手动运行: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# 启动应用
python3 main.py
