# 循理学伴 · Xunli Tutor

一个用于 ChatGPT / Codex 支持的插件环境的跨学科教学插件。讲清依据与中间过程，让学习者独立实践，根据作答证据调整节奏。

**v0.1.1** · 中文优先 · MIT · 无服务端依赖

## 能做什么

- 教学前检查：先核对本次内容与示例的必要前提，遇到未讲过或可能不懂的知识先提问，等回答后再继续。
- 概念讲解：从具体问题出发，说明条件、调用关系、推导和边界。
- 独立实践：给需求与验收标准，逐级提示，由学习者完成练习。
- 针对性纠错：区分概念、流程、计算、类型、拼写与省略。
- 学科切换：编程、数学、语言、记忆、操作与分析任务采用不同讲练方式。
- 学习交接：导出主题、作答证据、提示程度、未验证内容和下一步。

这是包含教学 Skill、协议与模板的插件。教学仍由宿主模型完成。首版没有独立聊天窗口、内置运行沙箱、云端档案或自动跨聊天记忆；有宿主文件工具时，可按要求保存本地学习记录。

## 安装到 Codex

使用**源码包**解压后的目录；该目录必须同时包含 `.agents/plugins/marketplace.json` 和 `plugins/xunli-tutor/`。插件 ZIP 适合支持导入 ZIP 的平台，不能代替本地 marketplace 的源码目录。

本机 Codex CLI 0.149.1 提供以下命令。打开 PowerShell，进入解压后的项目根目录执行：

```powershell
codex plugin marketplace add .
codex plugin list --marketplace xunli-tutor-local --available
codex plugin add xunli-tutor@xunli-tutor-local
```

这些命令会登记本地来源并安装插件到当前用户的 Codex 配置与缓存；它们不会发布插件。若客户端不支持 CLI 安装，在添加 marketplace 后，到桌面应用插件目录选择“循理学伴 · 本地插件”来源，安装“循理学伴”。安装后刷新插件列表或重启客户端，在新聊天中测试。具体入口依客户端版本而异。

更新文件后重新安装或使用客户端提供的刷新功能，以便缓存副本生效。本地来源不自动更新到公开版本。

卸载插件：

```powershell
codex plugin remove xunli-tutor@xunli-tutor-local
codex plugin marketplace remove xunli-tutor-local
```

## 开始使用

在插件选择器中选择“循理学伴”，或在支持显式 Skill 调用的客户端输入 `$learn-with-feedback`。宿主若显示带插件命名空间的名称，以选择器插入的名称为准。

可以这样说：

> 用循理学伴教我 Java 线程，从线程和任务的区别开始。讲清执行过程，再让我自己练习。

> 进入独立实践模式。我想练基础工程能力，只给需求、验收标准和必要提示，不替我写练习代码。

> 用同样的方法解释极限，重点讲清每一步为什么成立。

> 导出这次学习记录，保留提示程度和没有验证的内容，方便换聊天继续。

若想直接看答案，可以明确说“这次切换为直接解答”；记录会区分参考答案与独立完成。只问事实或普通代办时，不强制出题。

## 进度与个人偏好

公共插件不携带任何人的真实档案。

- [偏好模板](plugins/xunli-tutor/skills/learn-with-feedback/assets/learner-profile.md)：按需填写，不要求身份、学校或成绩。
- [学习记录模板](plugins/xunli-tutor/skills/learn-with-feedback/assets/learning-record.md)：保留证据、断点和下一步。
- [保存与恢复规则](plugins/xunli-tutor/skills/learn-with-feedback/references/progress.md)：有文件工具时按要求写入学习者目录；无工具时输出可复制文本。

新聊天需带入记录或明确授权宿主读取相应文件。仅安装插件不会让 AI 自动获得其他聊天内容。

## 教学方法与源码

- [通用教学协议](plugins/xunli-tutor/skills/learn-with-feedback/references/teaching-protocol.md)：也可单独交给不支持插件的 AI 阅读。
- [核心 Skill](plugins/xunli-tutor/skills/learn-with-feedback/SKILL.md)：触发条件、两种模式与提示边界。
- [学科指南](plugins/xunli-tutor/skills/learn-with-feedback/references/subject-guides.md)。
- [虚构教学示例](plugins/xunli-tutor/skills/learn-with-feedback/references/examples.md)。
- [行为评估方法](evals/README.md)与[当前验证记录](evals/results.md)。

```text
.agents/plugins/marketplace.json    本地来源
plugins/xunli-tutor/
  plugin.json                      标准插件清单
  .codex-plugin/plugin.json         Codex兼容清单
  skills/learn-with-feedback/       教学规则、引用和记录模板
evals/                             行为场景与评估证据
tools/validate.py                  仅标准库的离线结构检查
```

## 验证与打包

Python 3.10 或以上，在项目根目录运行：

```powershell
python tools/validate.py
```

结构验证不调用模型、不联网、不保存学习数据，不等于教学效果评估。行为评估需在目标模型与客户端中独立执行，方法见 `evals/README.md`。发布包在项目外构建，避免将真实学习档案、缓存和凭证放进去。

本地来源与 manifest 依据 [OpenAI 官方插件打包文档](https://developers.openai.com/plugins/build/plugins)。Skill 结构依据 [官方 Skill 指南](https://developers.openai.com/plugins/build/skills)。适配情况和未验证的平台见验证记录，不承诺不同模型输出完全一致。

## 开源与发布

源码按 [MIT License](LICENSE) 提供，包含本地可分发插件与安装说明，尚未提交公共插件目录。分发到其他平台前，按目标平台要求补充元数据并重新验证。贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。
