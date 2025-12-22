import feedparser
import datetime
import os
import smtplib
import re
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
    # 从环境变量获取配置
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
    # 尝试切换到 587 端口以提高兼容性
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    sender_email = os.environ.get("SENDER_EMAIL")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("SMTP_PASSWORD") # 授权码

    if not all([sender_email, receiver_email, password]):
        print("Email configuration missing. Skipping email sending.")
        return

    receivers = [r.strip() for r in receiver_email.split(',')]

    try:
        print(f"Debug: Connecting to {smtp_server}:{smtp_port} via STARTTLS...")
        # 使用 standard SMTP + STARTTLS，这在云环境下通常更稳定
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls() 
        server.login(sender_email, password)
        print("Debug: Login successful.")
        
        for receiver in receivers:
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = sender_email
            message['To'] = receiver
            message['Subject'] = Header(f"每日新闻汇总 - {datetime.datetime.now().strftime('%Y-%m-%d')}", 'utf-8')
            
            server.sendmail(sender_email, [receiver], message.as_string())
            print(f"Email sent successfully to {receiver}!")
            
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        print("Tip: If using QQ Mail, ensure SMTP is enabled and use the 16-digit authorization code.")

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
