import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    return access_token


def get_weather_emoji(weather_text):
    """根据天气情况返回对应的emoji符号"""
    weather_emoji_map = {
        "晴": "☀️",
        "多云": "☁️",
        "阴": "☁️",
        "小雨": "🌧️",
        "中雨": "🌧️",
        "大雨": "⛈️",
        "暴雨": "⛈️",
        "雷阵雨": "⚡",
        "雨夹雪": "🌨️",
        "小雪": "❄️",
        "中雪": "❄️",
        "大雪": "❄️",
        "暴雪": "❄️",
        "雾": "🌫️",
        "霾": "😷",
        "沙尘暴": "💨",
        "浮尘": "💨",
        "扬沙": "💨"
    }

    for key, emoji in weather_emoji_map.items():
        if key in weather_text:
            return emoji
    return "🌤️"  # 默认返回


def get_weather(region):
    """获取天气信息，包括当前天气和最高最低气温"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        location_id = response["location"][0]["id"]

    # 获取当前天气
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    weather = response["now"]["text"]

    # 获取今日天气预报（包含最高最低气温）
    forecast_url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    forecast_response = get(forecast_url, headers=headers).json()
    temp_min = forecast_response["daily"][0]["tempMin"] + "°C"
    temp_max = forecast_response["daily"][0]["tempMax"] + "°C"

    return weather, temp_min, temp_max


def get_lunar_date(today):
    """获取农历日期和生肖年"""
    lunar = ZhDate.from_datetime(datetime(today.year, today.month, today.day))

    # 农历月份
    lunar_months = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
    # 农历日期
    lunar_days = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                  "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                  "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
    # 天干
    tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # 地支
    dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    # 生肖
    shengxiao = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

    # 数字转中文
    num_to_chinese = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

    # 年份转中文
    year_str = str(lunar.lunar_year)
    year_chinese = ""
    for digit in year_str:
        year_chinese += num_to_chinese[int(digit)]

    # 计算天干地支和生肖
    gan_index = (lunar.lunar_year - 4) % 10
    zhi_index = (lunar.lunar_year - 4) % 12
    ganzhi = tiangan[gan_index] + dizhi[zhi_index]
    animal = shengxiao[zhi_index]

    lunar_month = lunar_months[lunar.lunar_month - 1]
    lunar_day = lunar_days[lunar.lunar_day - 1]

    lunar_date_str = "{}年{}月{} {}年（{}年）".format(year_chinese, lunar_month, lunar_day, ganzhi, animal)

    return lunar_date_str


def get_birthday_solar(birthday, year, today):
    """计算阳历生日倒计时"""
    birthday_month = int(birthday.split("-")[1])
    birthday_day = int(birthday.split("-")[2])
    year_date = date(year, birthday_month, birthday_day)

    if today > year_date:
        year_date = date(year + 1, birthday_month, birthday_day)

    if today == year_date:
        return 0
    else:
        return (year_date - today).days


def get_birthday_lunar(birthday, year, today):
    """计算农历生日倒计时"""
    birthday_str = birthday
    if birthday_str[0] == "r":
        birthday_str = birthday_str[1:]

    lunar_month = int(birthday_str.split("-")[1])
    lunar_day = int(birthday_str.split("-")[2])

    try:
        # 今年的农历生日对应的公历日期
        lunar_birthday = ZhDate(year, lunar_month, lunar_day).to_datetime().date()
    except:
        # 如果今年没有这个农历日期，尝试明年
        lunar_birthday = ZhDate(year + 1, lunar_month, lunar_day).to_datetime().date()

    if today > lunar_birthday:
        try:
            lunar_birthday = ZhDate(year + 1, lunar_month, lunar_day).to_datetime().date()
        except:
            lunar_birthday = ZhDate(year + 2, lunar_month, lunar_day).to_datetime().date()

    if today == lunar_birthday:
        return 0
    else:
        return (lunar_birthday - today).days


def get_love_message():
    """从第三方API获取每日情话"""
    url = "https://api.uomg.com/api/rand.qinghua?format=text"
    try:
        r = get(url)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return config.get("love_message", "今天也很爱你哦~")


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en


def send_message(to_user, access_token, region_name, weather, temp_min, temp_max, note_ch):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]

    # 获取农历日期
    lunar_date = get_lunar_date(today)

    # 获取在一起的天数
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    love_days = (today - love_date).days

    # 获取生日信息
    birthday_info = config.get("birthday1", {})
    birthday_str = birthday_info.get("birthday", "2003-04-23")

    # 阳历生日倒计时
    birthday_solar = get_birthday_solar(birthday_str, year, today)

    # 农历生日倒计时（需要在config中添加农历生日）
    lunar_birthday_str = config.get("lunar_birthday", "r2003-03-22")
    birthday_lunar = get_birthday_lunar(lunar_birthday_str, year, today)

    # 问候语
    greeting = config.get("greeting", "(づ￣ 3￣)づ美好的一天开始啦(づ￣ 3￣)づ")

    # 甜蜜问候（从API获取每日情话）
    love_message = get_love_message()

    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": config.get("click_url", "http://weixin.qq.com/download"),
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{}年{}月{}日 {}".format(year, month, day, week),
                "color": "#EED016"
            },
            "lunar_date": {
                "value": lunar_date,
                "color": "#849B97"
            },
            "greeting": {
                "value": greeting,
                "color": "#EED016"
            },
            "region": {
                "value": region_name,
                "color": "#4CBCD0"
            },
            "weather": {
                "value": weather,
                "color": "#4CBCD0"
            },
            "temp_min": {
                "value": temp_min,
                "color": "#0ACE5B"
            },
            "temp_max": {
                "value": temp_max,
                "color": "#FF6B6B"
            },
            "love_message": {
                "value": love_message,
                "color": "#FF6B6B"
            },
            "love_day": {
                "value": str(love_days),
                "color": "#CB6D9D"
            },
            "birthday_solar": {
                "value": str(birthday_solar),
                "color": "#6ECFDC"
            },
            "birthday_lunar": {
                "value": str(birthday_lunar),
                "color": "#CB6D9D"
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    print("发送数据:", data)
    print("返回结果:", response)
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp_min, temp_max = get_weather(region)

    # 获取每日金句
    note_ch = config.get("note_ch", "")
    if note_ch == "":
        note_ch, _ = get_ciba()

    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp_min, temp_max, note_ch)
