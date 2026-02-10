#!/bin/bash

# Typeless Mac - uv 迁移设置脚本
# 完成最后的设置步骤

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Typeless Mac - uv 迁移最终设置"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")"

# 1. 设置可执行权限
echo "1️⃣  设置可执行权限..."
chmod +x install.sh start.sh setup_uv.sh 2>/dev/null || true
echo "✅ 权限设置完成"

# 2. 检查 uv
echo ""
echo "2️⃣  检查 uv 安装状态..."
if command -v uv &> /dev/null; then
    echo "✅ uv 已安装: $(uv --version)"
else
    echo "❌ uv 未安装"
    echo ""
    echo "请运行以下命令安装："
    echo "  brew install uv"
    echo "  或"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 3. 验证文件
echo ""
echo "3️⃣  验证迁移文件..."
files=(
    "pyproject.toml"
    "start.sh"
    "install.sh"
    "UV_MIGRATION_GUIDE.md"
)

all_ok=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - 缺失"
        all_ok=false
    fi
done

echo ""
if [ "$all_ok" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✨ 迁移设置完成！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 下一步："
    echo ""
    echo "   方式1: 运行完整安装（推荐）"
    echo "   $ ./install.sh"
    echo ""
    echo "   方式2: 手动安装"
    echo "   $ uv sync"
    echo "   $ ./start.sh"
    echo ""
    echo "📚 查看迁移指南："
    echo "   $ cat UV_MIGRATION_GUIDE.md"
    echo ""
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  部分文件缺失，请检查"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
