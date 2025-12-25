# holidays.py - 节日配置
# 在这里添加节日，格式: (月, 日): { 配置 }

HOLIDAYS = {
    (12, 25): {
        "name": "圣诞节",
        "greeting": "圣诞节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🎄</div>
            <p style="text-align: center; color: #2e7d32; font-size: 16px; margin: 0 0 30px 0;">✨ Merry Christmas! ✨</p>
        """
    },
    (1, 1): {
        "name": "元旦",
        "greeting": "新年快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🎆</div>
            <p style="text-align: center; color: #ff6f00; font-size: 16px; margin: 0 0 30px 0;">🎊 Happy New Year! 🎊</p>
        """
    },
    (2, 14): {
        "name": "情人节",
        "greeting": "情人节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">💝</div>
            <p style="text-align: center; color: #e91e63; font-size: 16px; margin: 0 0 30px 0;">💕 Happy Valentine's Day! 💕</p>
        """
    },
    (10, 31): {
        "name": "万圣节",
        "greeting": "万圣节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🎃</div>
            <p style="text-align: center; color: #ff9800; font-size: 16px; margin: 0 0 30px 0;">👻 Happy Halloween! 👻</p>
        """
    },
    # 可以继续添加更多节日，例如：
    # (5, 1): {"name": "劳动节", "greeting": "劳动节快乐", "header_html": "..."},
    # 注意：农历节日（春节、中秋等）需要额外计算，这里暂不支持
}


def get_today_holiday():
    """返回今天的节日配置，如果没有则返回 None"""
    from datetime import datetime, timezone, timedelta
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    return HOLIDAYS.get((now.month, now.day))
