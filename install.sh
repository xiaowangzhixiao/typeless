#!/bin/bash

# Typeless Mac 安装脚本（uv 版本）
# 自动安装所有依赖并配置项目

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Typeless Mac - 安装向导（uv 版本）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 1. 检查 uv
echo "1️⃣  检查 uv..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，正在自动安装..."
    echo ""
    
    # 尝试使用 Homebrew 安装
    if command -v brew &> /dev/null; then
        echo "   使用 Homebrew 安装 uv..."
        brew install uv
    else
        echo "   使用官方脚本安装 uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # 添加到当前 shell 的 PATH
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    echo ""
    
    # 验证安装
    if ! command -v uv &> /dev/null; then
        echo "❌ uv 安装失败"
        echo ""
        echo "请手动安装 uv："
        echo "  方式1: brew install uv"
        echo "  方式2: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        echo "安装后请重启终端或运行："
        echo "  source ~/.zshrc  # 或 source ~/.bashrc"
        exit 1
    fi
fi

UV_VERSION=$(uv --version)
echo "✅ uv 已安装: $UV_VERSION"

# 2. 创建虚拟环境并安装依赖
echo ""
echo "2️⃣  创建虚拟环境并安装依赖..."
echo "   这可能需要几分钟..."

# 使用 uv sync 同步依赖（自动创建虚拟环境）
if uv sync; then
    echo "✅ 依赖安装完成"
else
    echo "❌ 依赖安装失败"
    echo ""
    echo "常见问题："
    echo "  1. 网络连接问题 - 检查网络是否正常"
    echo "  2. Python 版本不兼容 - 需要 Python 3.9+"
    echo ""
    exit 1
fi

# 3. 配置环境变量
echo ""
echo "3️⃣  配置环境变量..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
        echo ""
        echo "⚠️  重要：请编辑 .env 文件，配置以下内容："
        echo ""
        echo "   📝 LLM Provider 选择："
        echo "      LLM_PROVIDER=ollama      # 本地免费（推荐）"
        echo "      或"
        echo "      LLM_PROVIDER=openrouter  # 云端 API"
        echo ""
        echo "   🔑 如使用 OpenRouter："
        echo "      OPENROUTER_API_KEY=sk-or-v1-your-key-here"
        echo ""
        echo "   🤖 如使用 Ollama（需先安装）："
        echo "      OLLAMA_MODEL=qwen2.5:3b  # 或其他模型"
        echo ""
    else
        echo "❌ .env.example 文件不存在"
        exit 1
    fi
else
    echo "✅ .env 文件已存在"
fi

# 4. 下载 Whisper 模型
echo ""
echo "4️⃣  下载 Whisper 模型（tiny, 约 75MB）..."
echo "   这可能需要几分钟，取决于网络速度..."

if uv run python3 -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu')" 2>&1 | grep -v "Warning"; then
    echo "✅ Whisper 模型准备完成"
else
    echo "⚠️  模型下载可能失败，但可以在首次运行时自动下载"
fi

# 5. 检查 Ollama（如果选择使用）
echo ""
echo "5️⃣  检查 Ollama（可选）..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n 1)
    echo "✅ Ollama 已安装: $OLLAMA_VERSION"
    
    # 检查是否有模型
    MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
    if [ "$MODELS" -gt 0 ]; then
        echo "✅ 已安装 $MODELS 个 Ollama 模型"
    else
        echo "⚠️  未安装任何 Ollama 模型"
        echo ""
        echo "   推荐安装："
        echo "   ollama pull qwen2.5:3b   # 中文效果好（1.9GB）"
        echo "   或"
        echo "   ollama pull llama3.2:3b  # 英文效果好（2.0GB）"
    fi
else
    echo "ℹ️  Ollama 未安装（如需本地 LLM 支持）"
    echo ""
    echo "   安装方法："
    echo "   brew install ollama"
    echo "   或访问: https://ollama.ai"
fi

# 6. 设置可执行权限
echo ""
echo "6️⃣  设置可执行权限..."
chmod +x start.sh
chmod +x install.sh
echo "✅ 权限设置完成"

# 完成
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 安装完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 下一步："
echo ""
echo "   1. 编辑配置文件："
echo "      nano .env"
echo ""
echo "   2. 配置 LLM Provider："
echo "      - 使用 Ollama（本地，免费）: LLM_PROVIDER=ollama"
echo "      - 使用 OpenRouter（云端）:    LLM_PROVIDER=openrouter"
echo ""
echo "   3. 启动应用："
echo "      ./start.sh"
echo ""
echo "   4. 使用快捷键："
echo "      Cmd+Shift+Space - 开始/停止录音"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示："
echo ""
echo "   🆓 完全免费方案（推荐）："
echo "      - ASR: 本地 Whisper (tiny 模型)"
echo "      - LLM: 本地 Ollama (qwen2.5:3b)"
echo "      - 优点: 免费、隐私、离线可用"
echo ""
echo "   ☁️  云端方案："
echo "      - ASR: 本地 Whisper"
echo "      - LLM: OpenRouter API (Claude/GPT)"
echo "      - 优点: 质量更高、速度更快"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 更多文档："
echo "   - README.md - 项目介绍"
echo "   - QUICKSTART.md - 快速开始"
echo "   - OLLAMA_README.md - Ollama 使用指南"
echo ""
