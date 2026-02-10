# 🎙️ 欢迎使用 Typeless Mac！

感谢选择 Typeless Mac —— 你的智能 AI 语音输入助手！

## 🚀 立即开始（3 步）

### 1️⃣ 安装依赖
```bash
cd /Users/mattzwang/typeless-mac
pip3 install -r requirements.txt
```

### 2️⃣ 配置 API Key
1. 访问 https://openrouter.ai/keys 获取 API Key（新用户有免费额度）
2. 复制 `.env.example` 到 `.env`
3. 编辑 `.env`，填入你的 API Key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-你的密钥
   ```

### 3️⃣ 启动应用
```bash
python3 main.py
# 或使用一键启动脚本
./start.sh
```

就这么简单！🎉

## 💡 快速使用

1. **开始录音**: 按 `Cmd+Shift+Space`
2. **说话**: 自然说话，不用担心语气词和改口
3. **结束**: 停顿 2 秒自动结束，或再按一次快捷键
4. **自动输入**: 润色后的文本会自动出现在光标位置

**示例**:
- 你说: "嗯，我今天要去，不对，我明天要去公司开会"
- 输出: "我明天要去公司开会。"

## 📖 文档快速导航

| 文档 | 内容 | 推荐 |
|------|------|------|
| **QUICKSTART.md** | 详细安装和配置指南 | ⭐⭐⭐ 新手必读 |
| **EXAMPLES.md** | 各种使用场景示例 | ⭐⭐⭐ 了解能力 |
| **README.md** | 项目说明和特性介绍 | ⭐⭐ 快速了解 |
| **ARCHITECTURE.md** | 系统架构和技术文档 | ⭐ 开发者参考 |
| **PROJECT_SUMMARY.md** | 项目完整摘要 | ⭐ 全面了解 |

## ⚡ 常见场景

### 📝 写邮件
打开邮件应用 → 按快捷键 → 说话 → 自动输入

### 📋 记笔记
打开笔记应用 → 按快捷键 → 说话 → 自动输入

### 💬 聊天回复
打开聊天应用 → 按快捷键 → 说话 → 自动输入

### 🔍 搜索
聚焦搜索框 → 按快捷键 → 说话 → Enter 搜索

## ⚙️ 快速配置

### 切换到更快的模型（降低成本）
编辑 `config.yaml`:
```yaml
llm:
  model: "openai/gpt-4o-mini"  # 便宜 80%
```

### 离线模式（完全免费）
编辑 `config.yaml`:
```yaml
features:
  offline_mode: true  # 只识别，不润色
```

### 提高识别准确率
编辑 `config.yaml`:
```yaml
asr:
  model_size: "base"  # 或 "small"，更准确但更慢
```

## 🔐 隐私说明

- ✅ 语音在本地识别（Whisper 模型）
- ✅ 仅文本发送到 OpenRouter（可选）
- ✅ 不保存任何录音
- ✅ 不保存文本历史
- ✅ 支持完全离线模式

## 💰 成本估算

使用 **Claude 3.5 Sonnet** (推荐):
- 每次使用: $0.001-0.005
- 每天 50 次: $0.05-0.25
- 每月: $1.5-7.5

使用 **GPT-4o-mini** (经济):
- 成本降低 70-80%
- 每月约 $0.3-2

使用 **离线模式**:
- 完全免费！

**新用户福利**: OpenRouter 新用户通常有 $1-5 免费额度

## 🆘 遇到问题？

### 无法录音
→ 检查麦克风权限: `系统偏好设置 > 安全性与隐私 > 隐私 > 麦克风`

### 无法自动输入
→ 检查辅助功能权限: `系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能`

### API 报错
→ 检查 `.env` 中的 API Key 是否正确

### 识别不准确
→ 尝试更大的模型 (base 或 small)
→ 确保在安静环境中使用

### 其他问题
→ 运行测试: `python3 test.py`
→ 查看日志: `cat typeless.log`

## 🎯 下一步

1. ✅ 完成安装（上面 3 步）
2. 📖 阅读 `EXAMPLES.md` 了解更多用法
3. ⚙️ 根据需要调整配置
4. 🎙️ 开始享受语音输入！

## 💬 反馈与贡献

- 遇到 Bug？查看日志文件 `typeless.log`
- 有建议？修改配置或提示词
- 想贡献？代码模块化，易于扩展

## 📈 学习资源

- **OpenRouter 文档**: https://openrouter.ai/docs
- **Whisper 模型**: https://github.com/openai/whisper
- **faster-whisper**: https://github.com/guillaumekln/faster-whisper

---

## 🎉 开始使用

现在就试试吧！

```bash
python3 main.py
```

按 `Cmd+Shift+Space`，说 "你好世界"，看看魔法发生！✨

---

**享受智能语音输入的乐趣！** 🚀

有任何问题，查看文档或日志文件。祝使用愉快！
