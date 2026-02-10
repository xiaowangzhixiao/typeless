# 📦 Typeless Mac v0.2 更新日志

## 🎉 新功能：Ollama 本地 LLM 支持

### ✨ 主要更新

现在支持使用本地 Ollama API 进行文本润色，实现完全本地化、免费且隐私优先的体验！

### 🔧 技术更新

#### 1. LLM 模块重构 (`src/llm.py`)

- ✅ 新增 `provider` 参数支持多后端
- ✅ 新增 `_polish_openrouter()` 方法
- ✅ 新增 `_polish_ollama()` 方法  
- ✅ 自动路由到对应的 API

#### 2. 配置文件更新

**config.yaml**:
```yaml
llm:
  provider: "ollama"  # 新增：支持 openrouter 或 ollama
  ollama:              # 新增：Ollama 配置块
    base_url: "http://localhost:11434"
    model: "qwen2.5:3b"
```

**.env.example**:
```bash
LLM_PROVIDER=ollama           # 新增
OLLAMA_BASE_URL=...           # 新增
OLLAMA_MODEL=qwen2.5:3b       # 新增
```

#### 3. 主程序更新 (`main.py`)

- ✅ LLM 初始化逻辑支持多 provider
- ✅ 根据配置自动选择 OpenRouter 或 Ollama
- ✅ 向后兼容旧配置

### 📊 性能对比

| 方案 | 延迟 | 成本 | 隐私 | 质量 |
|------|------|------|------|------|
| **Ollama (qwen2.5:3b)** | ~2-3s | 免费 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **OpenRouter (Claude)** | ~2-4s | $0.003/次 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 🚀 使用方法

#### 快速切换

编辑 `config.yaml`，修改一行即可：

```yaml
# 使用 Ollama
llm:
  provider: "ollama"

# 使用 OpenRouter  
llm:
  provider: "openrouter"
```

### 🎯 推荐配置

**日常使用**（免费 + 隐私）:
```yaml
llm:
  provider: "ollama"
  ollama:
    model: "qwen2.5:3b"
```

**追求质量**（付费 + 云端）:
```yaml
llm:
  provider: "openrouter"
  model: "anthropic/claude-3.5-sonnet"
```

### 📚 文档

- **完整指南**: `OLLAMA_README.md`
- **原有文档**: 保持不变

### ⚠️ 注意事项

1. **Ollama 需要预先安装和启动**:
   ```bash
   brew install ollama
   ollama serve
   ollama pull qwen2.5:3b
   ```

2. **向后兼容**: 不修改配置时默认使用 OpenRouter

3. **硬件需求**: 3B 模型建议至少 8GB 内存

### 🐛 Bug 修复

- 无

### 📈 性能优化

- 优化了 LLM 处理器的错误处理
- 添加了更详细的日志输出

---

**升级建议**: 如果追求隐私和免费，强烈建议切换到 Ollama！
