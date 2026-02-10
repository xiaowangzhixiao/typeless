# Typeless Mac - AI 语音输入法

基于本地 ASR + OpenRouter LLM 的智能语音输入工具

## 功能特性

- ✅ 实时语音转文字（本地 Whisper 模型）
- ✅ 智能文本润色（去语气词、改口修正、格式化）
- ✅ 全局快捷键触发（Cmd+Shift+Space）
- ✅ 自动输入到当前应用
- ✅ 支持 OpenRouter 多模型切换

## 系统要求

- macOS 10.15+
- Python 3.9+
- 麦克风权限

## 快速开始

### 方式一：一键安装（推荐）⚡

```bash
# 克隆项目
git clone https://github.com/your-repo/typeless-mac.git
cd typeless-mac

# 运行安装脚本（自动安装 uv 和所有依赖）
chmod +x install.sh
./install.sh

# 启动应用
./start.sh
```

### 方式二：手动安装

#### 1. 安装 uv（极速 Python 包管理器）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 Homebrew
brew install uv

# 验证安装
uv --version
```

#### 2. 安装项目依赖

```bash
cd typeless-mac

# uv 会自动创建虚拟环境并安装所有依赖
uv sync
```

#### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
nano .env
```

配置示例：

```bash
# 选择 LLM Provider
LLM_PROVIDER=ollama  # 或 openrouter

# OpenRouter 配置（如使用云端 API）
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Ollama 配置（如使用本地 LLM）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
```

#### 4. （可选）安装 Ollama 本地 LLM

```bash
# 安装 Ollama
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载推荐模型（1.9GB）
ollama pull qwen2.5:3b
```

## 使用方法

### 启动应用

```bash
# 使用启动脚本（推荐）
./start.sh

# 或直接运行
uv run python3 main.py
```

### 使用快捷键

1. 按 `Cmd+Shift+Space` 开始录音
2. 说话（状态窗口会显示"🎤 录音中..."）
3. 再次按 `Cmd+Shift+Space` 或停顿 2 秒自动结束
4. AI 处理后自动输入到光标位置

### 配置 LLM

编辑 `config.yaml` 选择不同的 LLM provider 和模型：

**使用 Ollama（本地，免费）：**

```yaml
llm:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "qwen2.5:3b"  # 中文效果好
```

**使用 OpenRouter（云端，付费）：**

```yaml
llm:
  provider: "openrouter"
  model: "anthropic/claude-3.5-sonnet"
  max_tokens: 1000
  temperature: 0.3
```

## 项目结构

```
typeless-mac/
├── main.py                 # 主程序入口
├── src/
│   ├── asr.py             # 语音识别模块
│   ├── llm.py             # LLM 润色模块
│   ├── input_handler.py   # 系统输入处理
│   ├── hotkey.py          # 快捷键监听
│   └── ui.py              # 状态显示界面
├── pyproject.toml         # 项目配置和依赖
├── config.yaml            # 运行时配置
├── .env                   # 环境变量（需自行创建）
├── install.sh             # 一键安装脚本
├── start.sh               # 启动脚本
└── README.md
```

## 依赖管理（uv）

```bash
# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev pytest

# 更新所有依赖
uv sync --upgrade

# 查看依赖树
uv tree

# 导出为 requirements.txt（兼容性）
uv pip compile pyproject.toml -o requirements.txt

# 运行脚本
uv run python3 script.py

# 进入虚拟环境
source .venv/bin/activate
```

## 为什么使用 uv？

- ⚡ **极速安装**：比 pip 快 10-100 倍
- 🔒 **依赖锁定**：自动生成 `uv.lock` 确保可重现构建
- 🎯 **自动管理**：虚拟环境自动创建和管理
- 💾 **全局缓存**：节省磁盘空间
- 🦀 **Rust 实现**：高性能、低资源占用

## 隐私说明

- 语音在本地设备识别（Whisper 模型）
- 仅文本通过 OpenRouter 发送到 LLM
- 不存储任何录音或文本历史
- 可选离线模式（仅 ASR，不润色）

## 故障排除

### 麦克风权限

如果无法录音，需要授予终端/Python 麦克风权限：
`系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风`

### 无法自动输入

需要授予辅助功能权限：
`系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能`

## License

MIT
