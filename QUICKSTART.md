# Typeless Mac 快速开始

## 快速安装（5 分钟）

### 1. 安装依赖

```bash
cd /Users/mattzwang/typeless-mac
pip3 install -r requirements.txt
```

如果遇到权限问题，使用：
```bash
pip3 install --user -r requirements.txt
```

### 2. 配置 API Key

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 OpenRouter API Key：
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**获取 API Key**: https://openrouter.ai/keys

### 3. 运行应用

```bash
python3 main.py
```

### 4. 使用

1. 按 **Cmd+Shift+Space** 开始录音
2. 说话（右上角会显示 "🎤 录音中..."）
3. 再次按 **Cmd+Shift+Space** 或停顿 2 秒自动结束
4. 等待处理（显示 "🎯 识别中..." → "🤖 润色中..."）
5. 文本自动输入到光标位置

## 系统权限设置

首次运行时需要授予权限：

### 麦克风权限
`系统偏好设置` → `安全性与隐私` → `隐私` → `麦克风`
- 勾选 `终端` 或 `Python`

### 辅助功能权限（用于自动输入）
`系统偏好设置` → `安全性与隐私` → `隐私` → `辅助功能`
- 勾选 `终端` 或 `Python`

## 配置说明

### 切换 ASR 模型大小

编辑 `config.yaml`：

```yaml
asr:
  model_size: "tiny"  # 可选: tiny(75MB), base(142MB), small(466MB)
```

推荐：
- **tiny**: 最快，适合实时使用（准确率 ~85%）
- **base**: 平衡选择（准确率 ~90%）
- **small**: 最准确但较慢（准确率 ~95%）

### 切换 LLM 模型

编辑 `config.yaml` 或 `.env`：

```yaml
llm:
  model: "anthropic/claude-3.5-sonnet"  # 推荐，质量最高
  # model: "openai/gpt-4o-mini"        # 便宜快速
  # model: "google/gemini-2.0-flash-exp"  # 免费（有限额）
```

### 修改快捷键

编辑 `config.yaml`：

```yaml
app:
  hotkey: "cmd+shift+space"  # 改成你喜欢的组合
```

可用的修饰键：`cmd`, `ctrl`, `alt`, `shift`

### 离线模式（仅 ASR，不润色）

编辑 `config.yaml`：

```yaml
features:
  offline_mode: true  # 不调用 LLM
```

## 常见问题

### Q: 无法录音？
A: 检查麦克风权限，确保终端/Python 有权限访问麦克风

### Q: 文本无法自动输入？
A: 检查辅助功能权限，确保终端/Python 在列表中

### Q: 识别准确率低？
A: 
1. 尝试更大的模型（base 或 small）
2. 确保麦克风质量良好
3. 在安静环境中录音

### Q: OpenRouter API 报错？
A: 
1. 检查 API Key 是否正确
2. 确认账户有余额或额度
3. 检查网络连接

### Q: 处理太慢？
A: 
1. 使用更小的 ASR 模型（tiny）
2. 切换到更快的 LLM（如 gpt-4o-mini）
3. 降低 LLM 的 max_tokens

## 进阶使用

### 自定义润色提示词

编辑 `config.yaml` 中的 `system_prompt`，可以调整润色风格：

```yaml
llm:
  system_prompt: |
    你是一个专业的文本润色助手。
    - 去除语气词
    - 改正语法错误
    - 使文本更加正式/口语化（根据需求调整）
    直接输出结果。
```

### 按应用适配（TODO）

未来可以根据当前应用自动调整润色风格：
- 短信/微信：口语化
- 邮件/文档：正式
- 代码编辑器：技术术语

## 卸载

```bash
# 删除项目目录
rm -rf /Users/mattzwang/typeless-mac

# 删除模型缓存（可选）
rm -rf ~/.cache/whisper
```

## 反馈与贡献

遇到问题或有建议？欢迎反馈！
