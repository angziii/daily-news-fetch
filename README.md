# Daily News Aggregator 📰

一个基于 GitHub Actions 的轻量级每日新闻聚合器。

## 功能介绍
- **每日定时**：每天北京时间 8:00 自动抓取。
- **多源聚合**：包含科技、财经、地缘政治等高质量源。
- **自动推送**：生成 Markdown 报告并支持邮件推送。

## 部署说明
1. **新建仓库**：在 GitHub 上创建一个私有或公开仓库。
2. **推送代码**：将本项目文件推送至该仓库。
3. **配置 Secrets**（可选，用于邮件推送）：
   - `SENDER_EMAIL`: 你的发件邮箱。
   - `RECEIVER_EMAIL`: 你的收件邮箱。
   - `SMTP_PASSWORD`: SMTP 授权码。

## 已集成信源
- FT中文网
- BBC 中文
- 联合早报
- Solidot
- Hacker News
- 少数派 (Minority)
