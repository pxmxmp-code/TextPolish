# TextPolish GitHub 打包指南

GitHub Actions 只在推送形如 `vX.Y.Z` 的 tag 时打包，例如 `v2.1.1`。其他标签和手动触发不会执行打包流程。

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
4. 使用 PyInstaller 构建 `dist/TextPolish.exe`
5. 验证 exe 文件存在
6. 上传 `TextPolish-vX.Y.Z-Windows` artifact

## 本地验证

发布前建议先运行本地构建测试：

```powershell
uv run python scripts/test-build.py
```

## 标签规则

- 正确：`v1.0.0`、`v2.1.3`
- 不触发：`v2.1`、`2.1.0`、`v2.1.0-beta`
