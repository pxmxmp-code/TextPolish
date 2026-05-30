# TextPolish 构建脚本

这个目录包含用于本地验证构建流程的脚本。GitHub 端打包由标签触发：推送形如 `vX.Y.Z` 的 tag 后，工作流会自动构建 Windows exe 并上传 artifact。

## 📁 脚本说明

### `test-build.py`
本地构建测试脚本，用于：
- 模拟GitHub Actions构建环境
- 本地验证构建流程
- 确保发布前构建正常

**使用方法**:
```powershell
uv run python scripts/test-build.py
```

## 🚀 GitHub 打包流程

1. 开发完成后，先运行 `test-build.py` 验证本地构建。
2. 更新并提交版本号。
3. 创建并推送 `vX.Y.Z` 格式的 tag，例如 `v2.1.1`。
4. GitHub Actions 检测到匹配 tag 后自动打包。

## ⚠️ 注意事项

- 发布前确保工作区干净（无未提交更改）
- 建议先运行本地测试确保构建正常
- 只有 `vX.Y.Z` 格式的标签会触发 GitHub 打包
