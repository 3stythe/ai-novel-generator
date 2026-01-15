# AI 小说生成器

> 🤖 基于矽基流动 API 和多模型的智能长篇小说生成系统

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/Cody8722/ai-novel-generator/releases)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Test](https://img.shields.io/badge/test-passing-success.svg)](docs/reports/STRESS_TEST_REPORT.md)

## ✨ 特性

- 🚀 **快速生成**: 平均 34 秒/章，10 章小说仅需 6 分钟
- 💰 **成本极低**: 100 章长篇小说仅需 ¥0.24
- 📖 **剧情连贯**: AI 智能维护角色一致性和情节逻辑（92/100 分）
- 🔧 **错误自愈**: 自动重试机制，100% 成功率
- 📊 **实时监控**: Token 使用和成本实时追踪
- 🎯 **高度可控**: 支持自定义类型、主题、章节数

## 🎯 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**:
- `requests>=2.31.0` - HTTP 请求
- `python-dotenv>=1.0.0` - 环境变量管理

### 2. 配置 API Key

创建 `.env` 文件：

```bash
SILICONFLOW_API_KEY=your_api_key_here
```

获取 API Key: [矽基流动官网](https://siliconflow.cn/)

### 3. 测试连接

```bash
python novel_generator.py --test-api
```

### 4. 生成小说

**交互式生成**:
```bash
python novel_generator.py
```

然后按提示输入：
- 小说标题
- 类型（科幻/武侠/都市等）
- 核心主题
- 章节数

**自动化测试** (3 章):
```bash
python tests/test_generate.py
```

**压力测试** (10 章):
```bash
python tests/test_stress.py
```

**参数优化测试**:
```bash
# GLM-4 参数测试（快速模式）
python tests/test_glm4_params.py --quick --no-ai

# DeepSeek R1 参数测试（快速模式）
python tests/test_r1_params_enhanced.py --quick
```

## 📊 性能指标

### 实测数据（10 章压力测试）

| 指标 | 数值 | 评级 |
|------|------|------|
| **生成速度** | 33.7 秒/章 | ⭐⭐⭐⭐⭐ |
| **成功率** | 100% (10/10) | ⭐⭐⭐⭐⭐ |
| **成本** | ¥0.0024/章 | ⭐⭐⭐⭐⭐ |
| **剧情连贯性** | 92/100 | ⭐⭐⭐⭐⭐ |
| **平均字数** | 3,166 字/章 | ⭐⭐⭐⭐ |

**详细测试报告**: [STRESS_TEST_REPORT.md](docs/reports/STRESS_TEST_REPORT.md)

### 规模化能力预测

| 规模 | 耗时 | 成本 | 总字数 |
|------|------|------|--------|
| 10 章 | 6 分钟 | ¥0.024 | 31,658 |
| 20 章 | 11 分钟 | ¥0.048 | 63,316 |
| 50 章 | 28 分钟 | ¥0.119 | 158,290 |
| 100 章 | 56 分钟 | ¥0.238 | 316,580 |

## 🏗️ 系统架构

```
AI 小说生成器/
├── core/                      # 核心模块
│   ├── api_client.py         # API 客户端（重试、成本追踪）
│   ├── generator.py          # 小说生成器（大纲、章节）
│   ├── character_arc_enforcer.py  # 角色弧线强制器
│   ├── conflict_escalator.py      # 冲突升级器
│   └── event_dependency_graph.py  # 事件依赖图
├── utils/                     # 工具模块
│   ├── json_parser.py        # JSON 容错解析
│   ├── outline_validator.py  # 大纲验证器
│   ├── plot_manager.py       # 剧情管理器
│   └── volume_manager.py     # 分卷管理器
├── templates/                 # 提示词管理
│   └── prompts.py            # 提示词模板
├── tests/                     # 测试脚本目录
│   ├── test_glm4_params.py   # GLM-4 参数测试
│   ├── test_r1_params_enhanced.py  # R1 参数测试
│   └── ...                    # 其他测试脚本
├── docs/                      # 文档目录
│   ├── reports/              # 测试报告
│   └── guides/               # 使用指南
├── novels/                    # 生成的小说
├── test_results/              # 测试结果
├── config/                    # 配置目录
├── novel_generator.py        # CLI 主程序
└── config.py                 # 配置文件
```

## 💡 核心技术

### 1. 智能提示词管理
- **每次重建提示词**: 防止 AI 遗忘规则
- **上下文自动注入**: 传递上一章结尾（1000 字）
- **差异化策略**: 首章/中间章/末章使用不同提示词

### 2. 强大的 JSON 容错
5 策略级联解析，应对 AI 不规范输出：
1. 标准 JSON 解析
2. 提取 `` ```json `` `` 代码块
3. 提取任意 `` ``` `` 代码块
4. 暴力提取 `{...}`
5. 暴力提取 `[...]`

### 3. 自动重试机制
- 最多重试 3 次
- 指数退避策略（2^attempt 秒）
- 超时自动恢复

### 4. 精确成本追踪
- Token 级别计数（输入/输出分别统计）
- 实时成本计算
- 累积统计报告

## 🎨 示例输出

### 生成的小说目录结构
```
novels/novel_时空裂痕_20260104_143140/
├── metadata.json              # 项目元数据
├── outline.txt                # 故事大纲 (916 字)
└── chapters/                  # 章节目录
    ├── chapter_1.txt          # 第 1 章 (3,704 字)
    ├── chapter_2.txt          # 第 2 章 (3,514 字)
    ├── ...
    └── chapter_10.txt         # 第 10 章 (2,163 字)
```

> 💡 **提示**: 所有生成的小说都保存在 `novels/` 目录中

### 统计报告示例
```
📊 生成统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
专案目录............ novels/novel_时空裂痕_20260104_143140
已生成章节.......... 10/10
总字数.............. 31,658 字
总 Token 使用........ 34,821
  ├─ 输入........... 16,029
  └─ 输出........... 18,792
总成本.............. ¥0.0238
平均每章成本........ ¥0.0024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📖 文档

### 主要文档
- [开发者指南](docs/guides/README_DEV.md) - 详细的开发和使用文档
- [完整技术文档](docs/guides/AI小說生成器完整技術文檔.md) - 原始设计文档
- [变更日志](docs/guides/CHANGELOG.md) - 版本历史

### 测试报告
- [GLM-4 参数测试指南](docs/reports/GLM4_PARAMS_TEST_README.md) - GLM-4 模型参数优化
- [GLM-4 诊断增强报告](docs/reports/GLM4_DEBUG_ENHANCEMENT_REPORT.md) - Debug 模式实现
- [R1 参数测试指南](docs/guides/R1_PARAMS_TESTER_GUIDE.md) - DeepSeek R1 参数优化
- [压力测试报告](docs/reports/STRESS_TEST_REPORT.md) - 10 章长篇测试分析
- [实作完成报告](docs/reports/IMPLEMENTATION_REPORT.md) - MVP 完整实现记录

### 重构文档
- [大纲生成器重构](docs/guides/REFACTOR_OUTLINE_GENERATOR.md) - 延遲載入優化
- [延遲載入優化](docs/guides/REFACTOR_LAZY_LOADING.md) - 性能優化報告

### 查看更多
- [所有文档](docs/) - 完整文档列表
- [所有测试脚本](tests/) - 测试脚本说明
- [生成的小说](novels/) - 小说存储说明

## 🚀 支持的模型

### 当前版本 (v0.2.1)

系统支持三模型协作：
- **Architect (GLM-4)** ✅ - 大纲架构设计
- **Writer (Qwen2.5-7B)** ✅ - 章节内容生成
- **Editor (GLM-4)** ✅ - 内容编辑优化

### 可用模型列表

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|---------|---------|---------|
| **GLM-4** ✅ | ¥0.0010/1K | ¥0.0010/1K | 架构设计、编辑优化 |
| **Qwen2.5-7B-Instruct** ✅ | ¥0.0007/1K | ¥0.0007/1K | 内容生成 |
| **DeepSeek R1** | ¥0.0014/1K | ¥0.0056/1K | 深度推理（已测试但未采用）|
| Qwen2.5-14B-Instruct | ¥0.0014/1K | ¥0.0014/1K | 正式出版 |
| Qwen2.5-32B-Instruct | ¥0.0035/1K | ¥0.0035/1K | 专业级创作 |

> 💡 **提示**: 使用参数测试工具可以为每个模型找到最佳参数配置

## 🧪 测试验证

### ✅ 3 章基础测试
- **标题**: 星际边缘
- **成功率**: 100% (3/3)
- **总字数**: 9,719 字
- **总成本**: ¥0.0078
- **剧情连贯性**: 95/100

### ✅ 10 章压力测试
- **标题**: 时空裂痕
- **成功率**: 100% (10/10)
- **总字数**: 31,658 字
- **总成本**: ¥0.0238
- **剧情连贯性**: 92/100
- **性能**: 比预期快 68%

## 🛠️ 技术栈

- **语言**: Python 3.11+
- **API**: 矽基流动 (SiliconFlow)
- **模型**: Qwen2.5-7B-Instruct
- **依赖**: requests, python-dotenv

## 📝 待开发功能（Phase 2-3）

### Phase 2 - 上下文管理
- [ ] 分卷管理系统
- [ ] RAG 检索增强
- [ ] 向量数据库集成
- [ ] 智能上下文压缩

### Phase 3 - 质量提升
- [ ] 剧情一致性自动检查
- [ ] 角色档案自动维护
- [ ] 缓存系统优化
- [ ] 可视化统计面板

### Phase 4 - 用户体验
- [ ] Web UI 界面
- [ ] 实时生成预览
- [ ] 多模型并行生成
- [ ] 云端部署支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [矽基流动](https://siliconflow.cn/) - 提供高性价比 AI API 服务
- [阿里云通义千问团队](https://tongyi.aliyun.com/) - Qwen2.5 模型开发
- [Claude Code](https://claude.com/claude-code) - 开发辅助工具

## 📞 联系方式

- **Issues**: [GitHub Issues](https://github.com/Cody8722/ai-novel-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cody8722/ai-novel-generator/discussions)

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐

---

**🎉 开始你的 AI 小说创作之旅！**

*最后更新: 2026-01-15 | 版本: v0.2.1*

### 📂 项目组织
```
📁 tests/       - 所有测试脚本
📁 docs/        - 技术文档和报告
📁 novels/      - 生成的小说
📁 core/        - 核心功能模块
📁 utils/       - 工具函数
📁 templates/   - 提示词模板
```
