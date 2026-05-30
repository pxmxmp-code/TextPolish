# TextPolish GitHub 打包指南

GitHub Actions 在推送形如 `vX.Y.Z` 的 tag 时打包，例如 `v2.1.1`。也可以手动运行 workflow 并输入已有版本标签来补发 Release。

## 打包流程

```bash
# 更新版本号（编辑 pyproject.toml）后提交
git add pyproject.toml
git commit -m "chore: bump version to 2.1.1"

# 创建并推送语义化版本标签
git tag -a v2.1.1 -m "Release v2.1.1"
git push origin main
git push origin v2.1.1
```

匹配标签推送到 GitHub 后，`.github/workflows/package.yml` 会执行：

1. 检出代码
2. 安装 Python 3.13 和 uv
3. 运行 `uv sync`
4. 验证版本标签格式
5. 使用 PyInstaller 构建 `dist/TextPolish.exe`
6. 复制为 `TextPolish-vX.Y.Z-Windows.exe`
7. 上传 `TextPolish-vX.Y.Z-Windows` artifact
8. 创建或更新 GitHub Release，并上传 exe 安装包

## 本地验证

发布前建议先运行本地构建测试：

```powershell
uv run python scripts/test-build.py
```

## 标签规则

- 正确：`v1.0.0`、`v2.1.3`
- 不触发：`v2.1`、`2.1.0`、`v2.1.0-beta`

## 补发 Release

如果 tag 的打包 Action 已经成功，但 GitHub Releases 没有版本，可以手动运行 `Package TextPolish` workflow，输入已有标签（例如 `v2.1.0`）。workflow 会检出该标签、重新打包，并创建或更新对应 Release。
