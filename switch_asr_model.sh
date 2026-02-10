#!/bin/bash

# 一键切换 ASR 模型（medium / large-v3-turbo）
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$PROJECT_DIR/config.yaml"

usage() {
    echo "用法: ./switch_asr_model.sh [medium|large-v3-turbo]"
    echo "示例:"
    echo "  ./switch_asr_model.sh medium"
    echo "  ./switch_asr_model.sh large-v3-turbo"
}

TARGET_MODEL="${1:-}"

if [ -z "$TARGET_MODEL" ]; then
    usage
    exit 1
fi

case "$TARGET_MODEL" in
    medium|large-v3-turbo)
        ;;
    *)
        echo "❌ 不支持的模型: $TARGET_MODEL"
        usage
        exit 1
        ;;
esac

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 未找到配置文件: $CONFIG_FILE"
    exit 1
fi

CURRENT_MODEL=$(awk '
    /^asr:[[:space:]]*$/ {in_asr=1; next}
    in_asr && /^[^[:space:]]/ {in_asr=0}
    in_asr && /^[[:space:]]*model_size:/ {
        model=$2
        gsub(/"/, "", model)
        print model
        exit
    }
' "$CONFIG_FILE")

if [ "$CURRENT_MODEL" = "$TARGET_MODEL" ]; then
    echo "✅ 当前已是 $TARGET_MODEL，无需切换"
    exit 0
fi

TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

awk -v target="$TARGET_MODEL" '
    /^asr:[[:space:]]*$/ {in_asr=1; print; next}
    in_asr && /^[^[:space:]]/ {in_asr=0}
    in_asr && /^[[:space:]]*model_size:/ {
        print "  model_size: \"" target "\"  # tiny, base, small, medium, large-v3-turbo"
        replaced=1
        next
    }
    {print}
    END {
        if (!replaced) {
            print "未找到 asr.model_size 配置项" > "/dev/stderr"
            exit 2
        }
    }
' "$CONFIG_FILE" > "$TMP_FILE"

mv "$TMP_FILE" "$CONFIG_FILE"
trap - EXIT

echo "✅ 已切换 ASR 模型: $CURRENT_MODEL -> $TARGET_MODEL"
echo "📌 配置文件: $CONFIG_FILE"
