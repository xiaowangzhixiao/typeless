#!/bin/bash

# Typeless Mac 启动脚本（uv 版本）
# 使用 uv 管理虚拟环境和依赖

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Typeless Mac - 启动中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: uv 未安装"
    echo ""
    echo "请安装 uv："
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  或"
    echo "  brew install uv"
    echo ""
    echo "安装后请重启终端或运行："
    echo "  source ~/.zshrc  # 或 source ~/.bashrc"
    exit 1
fi

echo "✅ uv 版本: $(uv --version)"

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  警告: .env 文件不存在"
    echo "📝 正在从 .env.example 创建..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo ""
        echo "⚠️  重要：请编辑 .env 文件配置："
        echo "   - LLM_PROVIDER: 选择 openrouter 或 ollama"
        echo "   - OPENROUTER_API_KEY: 如使用 OpenRouter"
        echo "   - OLLAMA_MODEL: 如使用 Ollama（需先安装）"
        echo ""
        read -p "按回车键继续..." 
    else
        echo "❌ 错误: .env.example 文件也不存在"
        exit 1
    fi
fi

# 使用 uv 同步依赖（自动创建/更新虚拟环境）
echo ""
echo "📦 同步依赖..."
uv sync --quiet

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 虚拟环境创建失败"
    exit 1
fi

echo "✅ 依赖同步完成"

# Whisper 预热配置（默认由应用按 preload_strategy 加载）
echo ""
echo "🔍 检查 Whisper 配置..."
ASR_CONFIG=$(uv run python3 - <<'PY'
import os
import yaml

config = yaml.safe_load(open("config.yaml", "r", encoding="utf-8")) or {}
asr = config.get("asr", {})
model = asr.get("model_size", "tiny")
cache_dir = os.path.expanduser(asr.get("cache_dir", "~/.cache/whisper"))
print(f"{model}|{cache_dir}")
PY
)
ASR_MODEL="${ASR_CONFIG%%|*}"
ASR_CACHE_DIR="${ASR_CONFIG#*|}"
export ASR_MODEL
export ASR_CACHE_DIR

echo "📌 Whisper 模型: $ASR_MODEL"
echo "📌 Whisper 缓存: $ASR_CACHE_DIR"

if [ "${PREWARM_ASR:-0}" = "1" ]; then
    echo "🔥 PREWARM_ASR=1，启动前预热 Whisper 模型..."
    uv run python3 - <<'PY'
import os
from faster_whisper import WhisperModel

model = os.environ.get("ASR_MODEL", "tiny")
cache_dir = os.environ.get("ASR_CACHE_DIR", os.path.expanduser("~/.cache/whisper"))
WhisperModel(model, device="cpu", download_root=cache_dir)
print("Whisper 预热完成")
PY
else
    if [ -d "$ASR_CACHE_DIR" ] && [ -n "$(ls -A "$ASR_CACHE_DIR" 2>/dev/null)" ]; then
        echo "✅ 已检测到 Whisper 缓存（将按 preload_strategy 加载）"
    else
        echo "ℹ️  未执行启动前预热（将按 preload_strategy 加载）"
        echo "   如需预热请运行: PREWARM_ASR=1 ./start.sh"
    fi
fi

# 检查 LLM 配置
echo ""
echo "🔍 检查 LLM 配置..."
source .env
if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo "📌 使用 Ollama 本地模型"
    if ! command -v ollama &> /dev/null; then
        echo "⚠️  警告: Ollama 未安装"
        echo "   请安装: brew install ollama"
        echo "   或访问: https://ollama.ai"
    elif ! pgrep -x "ollama" > /dev/null; then
        echo "⚠️  警告: Ollama 服务未运行"
        echo "   请运行: ollama serve"
    else
        echo "✅ Ollama 服务运行中"
    fi
elif [ "$LLM_PROVIDER" = "openrouter" ]; then
    echo "📌 使用 OpenRouter API"
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "⚠️  警告: OPENROUTER_API_KEY 未设置"
        echo "   请在 .env 文件中配置"
    else
        echo "✅ API Key 已配置"
    fi
else
    echo "⚠️  警告: 未识别的 LLM_PROVIDER: $LLM_PROVIDER"
fi

# 启动应用
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎤 启动 Typeless Mac..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 使用提示："
echo "   - 快捷键: Cmd+Shift+Space 开始录音"
echo "   - 再次按下或自动检测停顿后停止录音"
echo "   - Ctrl+C 退出程序"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 使用 uv run 运行应用
uv run python3 main.py

# 捕获退出信号
trap "echo ''; echo '👋 Typeless Mac 已退出'; exit 0" INT TERM
