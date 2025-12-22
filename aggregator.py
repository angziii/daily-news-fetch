import feedparser
import datetime
import os
import re
import markdown
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 配置新闻源
NEWS_SOURCES = [
    {"name": "FT中文网", "url": "http://www.ftchinese.com/rss/feed", "category": "财经/国际"},
    {"name": "BBC 中文", "url": "https://www.bbc.com/zhongwen/simp/index.xml", "category": "财经/国际"},
    {"name": "联合早报", "url": "https://feedx.net/rss/zaobao.xml", "category": "财经/国际"},
    {"name": "Solidot", "url": "https://www.solidot.org/index.rss", "category": "技术/情报"},
    {"name": "阮一峰的网络日志", "url": "http://www.ruanyifeng.com/blog/atom.xml", "category": "技术/极客"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "category": "技术/极客"},
    {"name": "少数派 (Minority)", "url": "https://sspai.com/feed", "category": "科技/生活"},
]

LIMIT_PER_SOURCE = 5

def clean_summary(html_text):
    if not html_text:
        return ""
    # 将常见的块级标签替换为分号或句号，防止断句失败
    text = re.sub(r'</p>|<br\s*/?>|</li>', '。', html_text)
    # 去除剩余的所有 HTML 标签
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # 压缩多余的空白和重复的句号
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'。+', '。', text)
    return text.strip()

def fetch_news():
    today_news = {}
    # 设置 User-Agent 模拟浏览器，防止部分源屏蔽爬虫
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    for source in NEWS_SOURCES:
        print(f"Fetching {source['name']}...")
        feed = feedparser.parse(source['url'], agent=user_agent)
        
        entries = []
        if not feed.entries:
            print(f"Warning: No entries found for {source['name']}.")
        for entry in feed.entries[:LIMIT_PER_SOURCE]:
            summary = clean_summary(entry.get("summary", ""))
            if not summary and "description" in entry:
                summary = clean_summary(entry.description)
            
            entries.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary[:120] + "..." if len(summary) > 120 else summary
            })
            
        category = source['category']
        if category not in today_news:
            today_news[category] = []
        
        today_news[category].append({
            "source_name": source['name'],
            "items": entries
        })
        
    return today_news

def generate_markdown(news_data):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    md_content = f"# 每日新闻汇总 - {date_str}\n\n"
    
    for category, sources in news_data.items():
        md_content += f"## {category}\n\n"
        for source in sources:
            md_content += f"### {source['source_name']}\n\n"
            for item in source['items']:
                md_content += f"- [{item['title']}]({item['link']})\n"
                if item['summary']:
                    md_content += f"  > {item['summary']}\n"
            md_content += "\n"
            
    return md_content

def send_email(content):
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("SMTP_PASSWORD")

    if not all([sender_email, receiver_email, password]):
        print("Email configuration missing. Skipping email sending.")
        return

    # 尝试自动识别服务器（如果是 Gmail 或 QQ）
    default_server = "smtp.qq.com"
    default_port = 465
    
    if sender_email.endswith("@gmail.com"):
        default_server = "smtp.gmail.com"
        default_port = 587
    elif sender_email.endswith("@qq.com"):
        default_server = "smtp.qq.com"
        default_port = 465

    smtp_server = os.environ.get("SMTP_SERVER") or default_server
    smtp_port = int(os.environ.get("SMTP_PORT") or default_port)

    receivers = [r.strip() for r in receiver_email.split(',')]

    # 将 Markdown 转换为带有样式的 HTML
    html_body = markdown.markdown(content)
    
    # 极简美观的 CSS 样式
    html_template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #1a1a1a; border-bottom: 2px solid #EEE; padding-bottom: 10px; }}
            h2 {{ color: #2c3e50; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
            h3 {{ color: #e67e22; margin-top: 20px; }}
            a {{ color: #3498db; text-decoration: none; font-weight: bold; }}
            blockquote {{ border-left: 4px solid #DDD; padding-left: 15px; color: #666; font-style: italic; margin: 10px 0; }}
            li {{ margin-bottom: 10px; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #999; text-align: center; border-top: 1px solid #EEE; padding-top: 20px; }}
        </style>
    </head>
    <body>
        {html_body}
        <div class="footer">
            <p>本邮件由 GitHub Actions 自动发送</p>
            <p><a href="https://github.com/angziii/daily-news-fetch">查看 GitHub 仓库</a></p>
        </div>
    </body>
    </html>
    """

    try:
        print(f"Debug: Connecting to {smtp_server}:{smtp_port}...")
        
        # 根据端口选择连接方式
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.starttls()
            
        server.login(sender_email, password)
        print("Debug: Login successful.")
        
        for receiver in receivers:
            message = MIMEText(html_template, 'html', 'utf-8')
            message['From'] = f"Daily News <{sender_email}>"
            message['To'] = receiver
            message['Subject'] = Header(f"每日新闻汇总 - {datetime.datetime.now().strftime('%Y-%m-%d')}", 'utf-8')
            
            server.sendmail(sender_email, [receiver], message.as_string())
            print(f"Email sent successfully to {receiver}!")
            
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        print("Tip: If using Gmail, use an 'App Password'. If using QQ, use 'Authorization Code'.")

def main():
    news_data = fetch_news()
    md_report = generate_markdown(news_data)
    
    # 动态生成文件名，如 NEWS_251222.md
    date_filename = f"NEWS_{datetime.datetime.now().strftime('%y%m%d')}.md"
    
    # 保存为 Markdown 文件
    with open(date_filename, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"{date_filename} has been generated.")

    # 发送邮件
    send_email(md_report)

if __name__ == "__main__":
    main()
