# 🚀 Ollama 支持说明

Typeless Mac 现已支持本地 Ollama API！

## ✨ 优势

- 💰 **完全免费** - 无 API 成本
- 🔒 **完全隐私** - 数据不离开设备
- 🌐 **离线可用** - 无需网络连接
- ⚡ **速度快** - 2-3秒响应（3B模型）

## 🎯 快速开始

### 1. 安装 Ollama

```bash
brew install ollama
```

### 2. 启动服务

```bash
ollama serve
```

### 3. 下载模型（推荐中文）

```bash
ollama pull qwen2.5:3b
```

### 4. 配置 Typeless

编辑 `config.yaml`:

```yaml
llm:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "qwen2.5:3b"
```

### 5. 启动使用

```bash
python3 main.py
```

## 📊 推荐模型

| 模型 | 大小 | 速度 | 中文 | 场景 |
|------|------|------|------|------|
| **qwen2.5:3b** | 1.9GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 日常中文 |
| **llama3.2:3b** | 2.0GB | ⚡⚡⚡ | ⭐⭐⭐ | 英文为主 |
| **qwen2.5:7b** | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 高质量 |

## 🔄 切换 Provider

只需修改 `config.yaml` 一行：

```yaml
# 使用 Ollama
llm:
  provider: "ollama"

# 使用 OpenRouter
llm:
  provider: "openrouter"
```

## 📚 更多信息

- Ollama 官网: https://ollama.ai
- 模型列表: https://ollama.ai/library
