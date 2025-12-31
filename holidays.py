# holidays.py - 节日配置
# 在这里添加节日

# 阳历固定节日 (月, 日)
FIXED_HOLIDAYS = {
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
    (3, 8): {
        "name": "妇女节",
        "greeting": "妇女节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🌷</div>
            <p style="text-align: center; color: #e91e63; font-size: 16px; margin: 0 0 30px 0;">✨ Happy Women's Day! ✨</p>
        """
    },
    (4, 1): {
        "name": "愚人节",
        "greeting": "愚人节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🃏</div>
            <p style="text-align: center; color: #9c27b0; font-size: 16px; margin: 0 0 30px 0;">👻 Happy April Fools' Day! 👻</p>
        """
    },
    (5, 1): {
        "name": "劳动节",
        "greeting": "劳动节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🛠️</div>
            <p style="text-align: center; color: #5d4037; font-size: 16px; margin: 0 0 30px 0;">💪 Happy Labor Day! 💪</p>
        """
    },
    (6, 1): {
        "name": "儿童节",
        "greeting": "儿童节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🎈</div>
            <p style="text-align: center; color: #03a9f4; font-size: 16px; margin: 0 0 30px 0;">🎡 Happy Children's Day! 🎡</p>
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
    (12, 25): {
        "name": "圣诞节",
        "greeting": "圣诞节快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🎄</div>
            <p style="text-align: center; color: #2e7d32; font-size: 16px; margin: 0 0 30px 0;">✨ Merry Christmas! ✨</p>
        """
    },
    (12, 31): {
        "name": "跨年夜",
        "greeting": "跨年夜快乐",
        "header_html": """
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">🥂</div>
            <p style="text-align: center; color: #673ab7; font-size: 16px; margin: 0 0 30px 0;">✨ Happy New Year's Eve! ✨</p>
        """
    },
}

# 农历节日配置模板
def lunar_config(name, greeting, emoji, color):
    return {
        "name": name,
        "greeting": greeting,
        "header_html": f"""
            <div style="text-align: center; font-size: 100px; margin: 20px 0; line-height: 1;">{emoji}</div>
            <p style="text-align: center; color: {color}; font-size: 16px; margin: 0 0 30px 0;">✨ {greeting} ✨</p>
        """
    }

CNY_EVE = lunar_config("除夕", "除夕快乐", "🧨", "#d32f2f")
CNY_DAY = lunar_config("春节", "春节快乐", "🧧", "#c62828")
LANTERN = lunar_config("元宵节", "元宵节快乐", "🏮", "#f57c00")
DRAGON = lunar_config("端午节", "端午安康", "🐉", "#2e7d32")
QIXI = lunar_config("七夕", "七夕快乐", "🎋", "#e91e63")
MID_AUTUMN = lunar_config("中秋节", "中秋节快乐", "🥮", "#f9a825")
DOUBLE_NINTH = lunar_config("重阳节", "重阳安康", "🏔️", "#ff6f00")

# 农历节日查找表 (Year, Month, Day) -> Config
# 覆盖范围: 2025 - 2027
LUNAR_HOLIDAYS = {
    # 2025 (Snake)
    (2025, 1, 28): CNY_EVE,
    (2025, 1, 29): CNY_DAY,
    (2025, 2, 12): LANTERN,
    (2025, 5, 31): DRAGON,
    (2025, 8, 29): QIXI,
    (2025, 10, 6): MID_AUTUMN,
    (2025, 10, 29): DOUBLE_NINTH,
    
    # 2026 (Horse)
    (2026, 2, 16): CNY_EVE,
    (2026, 2, 17): CNY_DAY,
    (2026, 3, 3): LANTERN,
    (2026, 6, 19): DRAGON,
    (2026, 8, 19): QIXI,
    (2026, 9, 25): MID_AUTUMN,
    (2026, 10, 18): DOUBLE_NINTH,
    
    # 2027 (Goat)
    (2027, 2, 5): CNY_EVE,
    (2027, 2, 6): CNY_DAY,
    (2027, 2, 20): LANTERN,
    (2027, 6, 9): DRAGON,
    (2027, 8, 8): QIXI,
    (2027, 9, 15): MID_AUTUMN,
    (2027, 10, 8): DOUBLE_NINTH,
}

def get_today_holiday():
    """返回今天的节日配置，如果没有则返回 None"""
    from datetime import datetime, timezone, timedelta
    
    # 使用北京时间
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)
    
    # 1. 优先检查农历/特定日期节日
    lunar_cfg = LUNAR_HOLIDAYS.get((now.year, now.month, now.day))
    if lunar_cfg:
        return lunar_cfg
        
    # 2. 检查此日期是否是农历除夕（如果 Lookup Table 没覆盖到，这里可以兜底，但 Lookup 已经覆盖了）
    pass

    # 3. 检查固定节日
    return FIXED_HOLIDAYS.get((now.month, now.day))
