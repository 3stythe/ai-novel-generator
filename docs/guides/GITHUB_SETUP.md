# GitHub 仓库创建和推送指南

本指南将帮助你将 AI 小说生成器项目推送到 GitHub。

---

## 📋 前置准备

### 本地仓库状态

✅ **已完成**:
- Git 仓库已初始化
- 所有文件已提交 (4 个 commits)
- 版本标签已创建 (v0.1.0)

```bash
# 当前提交历史
781a76a docs: 更新 README 为 GitHub 展示版本
431ae87 chore: 更新 Claude Code 自动化权限
1401eef test: 添加 10 章压力测试
78a9f04 feat: 完成 AI 小說生成器 MVP (V0.1.0)

# 版本标签
v0.1.0 - Release: AI 小說生成器 MVP v0.1.0
```

---

## 🚀 步骤 1: 在 GitHub 创建新仓库

### 1.1 登录 GitHub
访问: https://github.com

### 1.2 创建新仓库
1. 点击右上角 `+` → `New repository`
2. 填写仓库信息：

```
Repository name: ai-novel-generator
Description: 🤖 基于矽基流动 API 和 Qwen2.5 模型的智能长篇小说生成系统
```

### 1.3 仓库设置

**⚠️ 重要设置**:
- ❌ **不要勾选** "Add a README file"（本地已有）
- ❌ **不要勾选** "Add .gitignore"（本地已有）
- ❌ **不要勾选** "Choose a license"（可选）

**可见性**:
- 🔓 Public（推荐，开源项目）
- 🔒 Private（私有项目）

### 1.4 创建仓库
点击 `Create repository` 按钮

---

## 🔗 步骤 2: 配置远程仓库

### 2.1 复制仓库 URL

GitHub 会显示类似以下的 URL：
```
https://github.com/your-username/ai-novel-generator.git
```

**⚠️ 注意**:
- 替换 `your-username` 为你的 GitHub 用户名
- 如果使用 SSH: `git@github.com:your-username/ai-novel-generator.git`

### 2.2 添加远程仓库

**命令**:
```bash
cd "E:\神奇的東東\AI 小說生成器"
git remote add origin https://github.com/your-username/ai-novel-generator.git
```

**验证**:
```bash
git remote -v
```

**预期输出**:
```
origin  https://github.com/your-username/ai-novel-generator.git (fetch)
origin  https://github.com/your-username/ai-novel-generator.git (push)
```

---

## 📤 步骤 3: 推送代码到 GitHub

### 3.1 推送主分支

**命令**:
```bash
git push -u origin master
```

**参数说明**:
- `-u`: 设置上游分支（以后只需 `git push`）
- `origin`: 远程仓库名称
- `master`: 分支名称

**预期输出**:
```
Enumerating objects: ..., done.
Counting objects: 100% (...), done.
...
To https://github.com/your-username/ai-novel-generator.git
 * [new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

### 3.2 推送版本标签

**命令**:
```bash
git push origin v0.1.0
```

**预期输出**:
```
...
To https://github.com/your-username/ai-novel-generator.git
 * [new tag]         v0.1.0 -> v0.1.0
```

**可选：推送所有标签**
```bash
git push origin --tags
```

---

## ✅ 步骤 4: 验证推送结果

### 4.1 检查 GitHub 网页

访问: `https://github.com/your-username/ai-novel-generator`

**应该看到**:
- ✅ README.md 渲染为首页
- ✅ 所有文件和目录
- ✅ 4 个 commits
- ✅ 1 个 release (v0.1.0)

### 4.2 检查 Release

访问: `https://github.com/your-username/ai-novel-generator/releases`

**应该看到**:
- ✅ v0.1.0 标签
- ✅ Release 说明

**可选：编辑 Release**
1. 点击 v0.1.0 标签
2. 点击 "Edit tag"
3. 添加详细的 Release Notes（可以从 CHANGELOG.md 复制）
4. 点击 "Publish release"

---

## 🎨 步骤 5: 优化 GitHub 仓库（可选）

### 5.1 添加主题标签 (Topics)

在仓库首页点击 `Add topics`，添加：
```
ai, novel-generator, qwen, siliconflow, python,
natural-language-processing, text-generation,
creative-writing, automated-writing
```

### 5.2 设置仓库描述

在仓库首页点击 `Edit` 按钮（齿轮图标），设置：
```
Description: 🤖 基于矽基流动 API 和 Qwen2.5 模型的智能长篇小说生成系统
Website: (留空或填项目主页)
```

### 5.3 启用 Discussions（可选）

Settings → General → Features → ✅ Discussions

### 5.4 创建 LICENSE 文件（推荐）

**MIT License 模板**:
```bash
# 在仓库网页上
Add file → Create new file
Name: LICENSE
# 从模板选择 MIT License
# Commit
```

**或本地创建后推送**:
```bash
# 创建 LICENSE 文件（MIT 模板）
# 然后
git add LICENSE
git commit -m "docs: 添加 MIT 开源许可证"
git push
```

---

## 🔧 常见问题

### Q1: 推送时要求输入用户名和密码

**原因**: GitHub 已废弃密码认证

**解决方案 1 - Personal Access Token (推荐)**:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → 勾选 `repo` 权限
3. 复制 token（只显示一次）
4. 推送时用 token 代替密码

**解决方案 2 - SSH (更安全)**:
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加到 GitHub
# GitHub → Settings → SSH and GPG keys → New SSH key

# 更改远程 URL
git remote set-url origin git@github.com:your-username/ai-novel-generator.git
```

### Q2: 推送被拒绝 (rejected)

**错误信息**: `Updates were rejected because the remote contains work...`

**原因**: 远程仓库有本地没有的提交（比如创建时勾选了 README）

**解决方案**:
```bash
# 拉取并合并远程更改
git pull origin master --allow-unrelated-histories

# 解决冲突（如果有）
# 然后推送
git push -u origin master
```

### Q3: 分支名称冲突 (master vs main)

**现象**: GitHub 默认分支是 `main`，本地是 `master`

**解决方案 1 - 重命名本地分支**:
```bash
git branch -m master main
git push -u origin main
```

**解决方案 2 - 在 GitHub 设置默认分支**:
```
GitHub → Settings → Branches → Default branch → 改为 master
```

### Q4: .env 文件被推送了

**⚠️ 严重问题**: API Key 泄露！

**立即操作**:
1. **撤销 API Key**（矽基流动后台）
2. **删除泄露的 commit**:
```bash
# 从 Git 历史中删除 .env
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送
git push origin --force --all
```

3. **检查 .gitignore**:
```bash
# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: 确保 .env 在 .gitignore 中"
git push
```

---

## 📝 后续操作建议

### 1. 保护主分支
```
Settings → Branches → Add rule
Branch name pattern: master (或 main)
✅ Require pull request reviews before merging
✅ Require status checks to pass before merging
```

### 2. 设置 GitHub Actions（可选）
创建 `.github/workflows/test.yml` 自动运行测试

### 3. 添加贡献指南
创建 `CONTRIBUTING.md` 说明如何贡献代码

### 4. 添加 Issue 模板
`.github/ISSUE_TEMPLATE/` 创建 bug 和 feature 模板

### 5. 添加徽章到 README
```markdown
![GitHub](https://img.shields.io/github/license/your-username/ai-novel-generator)
![GitHub stars](https://img.shields.io/github/stars/your-username/ai-novel-generator)
![GitHub forks](https://img.shields.io/github/forks/your-username/ai-novel-generator)
```

---

## ✅ 验证清单

推送完成后，确认以下项目：

- [ ] README.md 在首页正常显示
- [ ] 所有源代码文件都在
- [ ] .env 文件**未被推送**（敏感信息）
- [ ] test_generate.py 和 test_stress.py 可见
- [ ] CHANGELOG.md、IMPLEMENTATION_REPORT.md 等文档可见
- [ ] v0.1.0 标签存在于 releases 页面
- [ ] 可以 clone 仓库并正常运行
- [ ] 文档中的链接都正常工作

---

## 🎉 完成！

你的 AI 小说生成器项目现已成功部署到 GitHub！

**下一步**:
1. 🌟 分享你的项目给朋友
2. 📢 在社交媒体宣传
3. 🔗 添加到个人简历/作品集
4. 🤝 欢迎贡献者提交 PR
5. 📈 持续开发 Phase 2 功能

**仓库 URL**:
```
https://github.com/your-username/ai-novel-generator
```

---

**最后更新**: 2026-01-04
**文档版本**: v1.0
