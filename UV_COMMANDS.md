# uv 快速命令参考

## 🚀 常用命令

### 项目管理

```bash
# 初始化新项目
uv init

# 同步依赖（安装/更新虚拟环境）
uv sync

# 仅安装主依赖（不包括开发依赖）
uv sync --no-dev

# 强制重新安装所有依赖
uv sync --reinstall
```

### 运行脚本

```bash
# 在虚拟环境中运行 Python
uv run python main.py

# 运行脚本（自动使用虚拟环境）
uv run python3 script.py

# 运行已安装的命令
uv run pytest
uv run black .
uv run mypy src/
```

### 依赖管理

```bash
# 添加依赖
uv add requests
uv add numpy pandas

# 添加开发依赖
uv add --dev pytest black mypy

# 添加可选依赖组
uv add --optional docs sphinx

# 移除依赖
uv remove requests

# 更新所有依赖到最新版本
uv sync --upgrade

# 更新特定依赖
uv add requests --upgrade
```

### 查询信息

```bash
# 查看已安装的包
uv pip list

# 查看依赖树
uv tree

# 查看包信息
uv pip show requests

# 搜索包
uv pip search numpy
```

### pip 兼容命令

```bash
# 使用 pip 语法安装
uv pip install requests

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 导出依赖到 requirements.txt
uv pip freeze > requirements.txt

# 或使用 compile
uv pip compile pyproject.toml -o requirements.txt

# 卸载包
uv pip uninstall requests
```

### 虚拟环境

```bash
# 创建虚拟环境（通常不需要手动创建）
uv venv

# 指定 Python 版本创建
uv venv --python 3.11

# 激活虚拟环境（传统方式）
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf .venv
```

### 缓存管理

```bash
# 查看缓存大小
uv cache dir

# 清理缓存
uv cache clean

# 清理特定包的缓存
uv cache clean requests
```

### 锁定文件

```bash
# 生成 uv.lock（自动）
uv sync

# 从锁定文件安装（精确版本）
uv sync --frozen

# 更新锁定文件但不安装
uv lock
```

---

## 📊 Typeless Mac 项目专用命令

### 日常开发

```bash
# 启动应用
./start.sh
# 或
uv run python3 main.py

# 运行测试
uv run python3 test.py

# 格式化代码
uv run black src/ main.py

# 类型检查
uv run mypy src/
```

### 安装和设置

```bash
# 完整安装
./install.sh

# 手动安装
uv sync

# 仅安装运行时依赖
uv sync --no-dev

# 设置权限
chmod +x install.sh start.sh setup_uv.sh
```

### 依赖更新

```bash
# 更新所有依赖
uv sync --upgrade

# 添加新依赖
uv add package-name

# 查看项目依赖树
uv tree
```

### 环境检查

```bash
# 查看 uv 版本
uv --version

# 查看 Python 版本
uv run python3 --version

# 查看已安装的包
uv pip list

# 验证环境
uv run python3 -c "import faster_whisper; print('OK')"
```

---

## 🎯 最佳实践

### 1. 总是使用 `uv run`

```bash
# ✅ 推荐
uv run python3 main.py

# ❌ 不推荐（需要手动激活虚拟环境）
source .venv/bin/activate
python3 main.py
```

### 2. 定期更新依赖

```bash
# 每周或每月运行
uv sync --upgrade
```

### 3. 提交 uv.lock

```bash
# 确保团队环境一致
git add uv.lock
git commit -m "Update dependencies"
```

### 4. 使用 pyproject.toml 管理依赖

```toml
# 不要手动编辑 requirements.txt
# 使用 uv add/remove 管理依赖
```

---

## 🔧 故障排除

### uv 命令找不到

```bash
# 添加到 PATH
export PATH="$HOME/.cargo/bin:$PATH"

# 永久生效
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 依赖解析失败

```bash
# 清理缓存重试
uv cache clean
uv sync
```

### 虚拟环境损坏

```bash
# 删除并重建
rm -rf .venv
uv sync
```

### 权限问题

```bash
# macOS/Linux
chmod +x script.sh

# 或直接运行
bash script.sh
```

---

## 📚 更多资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [项目迁移指南](UV_MIGRATION_GUIDE.md)
- [更新日志](CHANGELOG_v0.2.0.md)

---

## ⚡ 速查表

| 任务 | 命令 |
|------|------|
| 安装项目 | `uv sync` |
| 运行脚本 | `uv run python3 script.py` |
| 添加依赖 | `uv add package` |
| 移除依赖 | `uv remove package` |
| 更新依赖 | `uv sync --upgrade` |
| 查看依赖 | `uv tree` |
| 清理缓存 | `uv cache clean` |
| 导出依赖 | `uv pip freeze > requirements.txt` |

---

**提示**: 将此文件保存为书签，方便随时查阅！
