import feedparser
import datetime
import os
import re
import markdown
import smtplib
import json
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
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    return {}

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def clean_text(html_text):
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

def fetch_news(history):
    today_news = {}
    new_history = history.copy()
    has_update = False
    
    # 设置 User-Agent 模拟浏览器，防止部分源屏蔽爬虫
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    for source in NEWS_SOURCES:
        print(f"Fetching {source['name']}...")
        feed = feedparser.parse(source['url'], agent=user_agent)
        
        source_history = history.get(source['name'], [])
        entries = []
        
        if not feed.entries:
            print(f"Warning: No entries found for {source['name']}.")
            continue

        for entry in feed.entries[:LIMIT_PER_SOURCE]:
            # 使用 link 作为唯一标识
            item_id = entry.link
            
            if item_id in source_history:
                continue
            
            # 清理标题和摘要
            title = clean_text(entry.title)
            summary = clean_text(entry.get("summary", ""))
            if not summary and "description" in entry:
                summary = clean_text(entry.description)
            
            entries.append({
                "title": title,
                "link": entry.link,
                "summary": summary[:150] + "..." if len(summary) > 150 else summary
            })
            
            # 更新历史记录（仅记录本批次抓取到的）
            if source['name'] not in new_history:
                new_history[source['name']] = []
            new_history[source['name']].insert(0, item_id)
        
        # 限制每个源的历史记录大小，防止文件过大
        if source['name'] in new_history:
            new_history[source['name']] = new_history[source['name']][:20]

        if entries:
            has_update = True
            category = source['category']
            if category not in today_news:
                today_news[category] = []
            
            today_news[category].append({
                "source_name": source['name'],
                "items": entries
            })
        
    return today_news, new_history, has_update

def generate_markdown(news_data):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    md_content = f"# 每日新闻汇总 (增量更新) - {date_str}\n\n"
    
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
    test_email = os.environ.get("TEST_EMAIL")
    password = os.environ.get("SMTP_PASSWORD")

    # 调试模式：如果设置了 TEST_EMAIL，则只发给它
    is_debug = False
    if test_email and test_email.strip():
        print(f"Debug Mode: Overriding receiver with TEST_EMAIL: {test_email}")
        receivers = [test_email.strip()]
        is_debug = True
    else:
        receivers = [r.strip() for r in receiver_email.split(',')] if receiver_email else []

    if not all([sender_email, receivers, password]):
        print("Required email configuration (sender, receiver, or password) is missing. Skipping email sending.")
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
    
    # 匹配博客风格的极简美观模板
    html_template = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* 引用字体 */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                line-height: 1.7; 
                color: #333333; 
                background-color: #FEFEFE; 
                margin: 0; 
                padding: 0;
            }}
            .wrapper {{
                width: 100%;
                background-image: radial-gradient(circle at 35% 50%, #A2C2FF22, #FEFEFE 60%);
                padding: 40px 0;
            }}
            .container {{ 
                max-width: 680px; 
                margin: 0 auto; 
                padding: 40px; 
                background: #FFFFFF;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            }}
            .header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            h1 {{ 
                color: #111111; 
                font-size: 28px; 
                font-weight: 700;
                margin-top: 0;
                letter-spacing: -0.5px;
            }}
            h2 {{ 
                color: #111111; 
                font-size: 20px;
                margin-top: 40px; 
                border-left: 4px solid #A2C2FF; 
                padding-left: 15px;
                background-color: #f9fbff;
                padding-top: 8px;
                padding-bottom: 8px;
            }}
            h3 {{ 
                color: #222222; 
                font-size: 18px;
                margin-top: 30px;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 8px;
            }}
            ul {{ padding-left: 0; list-style: none; }}
            li {{ margin-bottom: 24px; }}
            a {{ 
                color: #222222; 
                text-decoration: none; 
                font-weight: 700;
                border-bottom: 1px solid rgba(162, 194, 255, 0.4);
                transition: border-bottom 0.2s ease;
            }}
            a:hover {{
                border-bottom: 2px solid #A2C2FF;
            }}
            blockquote {{ 
                margin: 12px 0 0 0;
                padding: 0 0 0 16px; 
                border-left: 2px solid #A2C2FF; 
                color: #555555; 
                font-size: 14px;
                font-style: normal;
                line-height: 1.6;
            }}
            .footer {{ 
                margin-top: 60px; 
                padding-top: 30px;
                text-align: center; 
                font-size: 13px; 
                color: #888888; 
                border-top: 1px solid #eeeeee; 
            }}
            .footer a {{
                color: #888888;
                font-weight: 400;
                border-bottom: 1px solid #eeeeee;
            }}
            @media (max-width: 600px) {{
                .container {{ padding: 20px; margin: 10px; }}
                h1 {{ font-size: 24px; }}
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <p style="font-size: 14px; color: #888; margin-bottom: 8px;">{datetime.datetime.now().strftime('%Y年%m月%d日')}</p>
                    <h1>Daily News Roundup</h1>
                </div>
                <div class="content">
                    {html_body}
                </div>
                <div class="footer">
                    <p>Generated by GitHub Actions • <a href="https://github.com/angziii/daily-news-fetch">View Repository</a></p>
                    <p>© {datetime.datetime.now().year} @angziii</p>
                </div>
            </div>
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
            
            subject = f"新闻更新汇总 - {datetime.datetime.now().strftime('%Y-%m-%d')}"
            if is_debug:
                subject = f"[DEBUG] {subject}"
            message['Subject'] = Header(subject, 'utf-8')
            
            server.sendmail(sender_email, [receiver], message.as_string())
            print(f"Email sent successfully to {receiver}!")
            
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    history = load_history()
    news_data, new_history, has_update = fetch_news(history)
    
    if not has_update:
        print("No new content found across all sources. Skipping report generation and email.")
        return

    md_report = generate_markdown(news_data)
    
    # 动态生成文件名，如 NEWS_251222.md
    date_filename = f"NEWS_{datetime.datetime.now().strftime('%y%m%d')}.md"
    
    # 保存为 Markdown 文件
    with open(date_filename, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"{date_filename} has been generated.")

    # 更新历史记录文件
    save_history(new_history)
    print("History updated.")

    # 发送邮件
    send_email(md_report)

if __name__ == "__main__":
    main()
