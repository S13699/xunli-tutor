# 循理学伴 · Xunli Tutor v0.2.0

跨学科交互教学插件：讲清依据与中间过程，让学习者独立实践，根据作答证据调整节奏。

## 使用

在支持的宿主中安装并选择插件后，发送：

> 用循理学伴教我指定主题。讲清过程，再让我独立尝试；卡住时逐级提示。

也可以明确要求“独立实践，不代写当前练习”，或“这次切换为直接解答”。

本目录是独立插件包。对于 Codex 本地 marketplace 安装，请使用完整源码包，它另外包含 `.agents/plugins/marketplace.json` 和安装说明。本 ZIP 不直接创建 marketplace 或修改配置。

## 内容

- [教学 Skill](skills/learn-with-feedback/SKILL.md)
- [通用教学协议](skills/learn-with-feedback/references/teaching-protocol.md)
- [学科指南](skills/learn-with-feedback/references/subject-guides.md)
- [示例](skills/learn-with-feedback/references/examples.md)
- [学习记录与交接](skills/learn-with-feedback/references/progress.md)

使用宿主模型与已有工具；没有独立聊天界面、账户系统、内置沙箱或自动跨聊天记忆。导出的档案需要带入新聊天，或通过宿主工具明确读取。

源码与插件按 [MIT License](LICENSE) 分发。
