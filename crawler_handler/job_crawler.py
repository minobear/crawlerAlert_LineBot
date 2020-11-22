import json
import re
import time

import requests

from bot_utils import send_broadcast_message
from database.get_db import db

url = "https://top.104.com.tw/api/demandList/search?cats=4006000%2C4001000%2C4002000%2C4003000%2C4004000%2C4005000%2C4007000%2C4009000%2C4010000"

headers = {
    "cookie":"_gid=GA1.3.1140161573.1604031883; __auc=3a23b8f717577c02832e65b49e6; luauid=538928883; __gads=ID=2beca360f2cf092d-22129c9e6ec4009a:T=1604031948:RT=1604031948:S=ALNI_Ma-5-5BRBNA3Pk_iec6geYkMdLUkw; _hp2_id.3192618648=%7B%22userId%22%3A%228293769712694783%22%2C%22pageviewId%22%3A%228732080109789794%22%2C%22sessionId%22%3A%223609058703816748%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; EPK=10562497896987cd324ae1e0c14db22d4; R_PF=%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C%2C2020103052124030000003%2C%2C%2C; _hjid=b8c9c556-02de-43ee-a278-2c5d75a27001; _top=s%3AJjS0sYOWcLHf5oWYaF_1oibIjpWsWSC1.xqdJC3dOOp0HGXCTOftG%2BuDuJin%2FzEr9UjGfMswobmg; _hjClosedSurveyInvites=596661; _hjTLDTest=1; AC=1604067584; TS01f8a99d=01180e452d0f6ca40e40f18a187335efd149c46ccd4cefad6d5451fa76b0da76f27a8ace9a0194f73b249df3dfc88376d85c3b1fed1eee34c5191539df5e15f6257adabbff7cc86e681d70f47bc4160dca9773da7b897d8219feb4b77137941c6fc25b09dcb7e0892715f2a7ef34fcde4ce71e0f70419162965934db1718d1b9324ea13711; lup=538928883.4911295100689.4707284154224.1.4640712161167; lunp=4707284154224; __asc=43d0bd7f1757cd2970087703280; _gat_UA-140919465-1=1; _gat_UA-15276226-1=1; _ga_FJWMQR9J2K=GS1.1.1604116976.9.1.1604118376.0; _ga=GA1.1.917347697.1604031883; mp_f44b9e4d96b69ff2c0adb2879c26f7ba_mixpanel=%7B%22distinct_id%22%3A%20%2217577c6e09a12c-0418d61ca2c21e-303464-1fa400-17577c6e09b660%22%2C%22%24device_id%22%3A%20%2217577c6e09a12c-0418d61ca2c21e-303464-1fa400-17577c6e09b660%22%2C%22utm_source%22%3A%20%22case%22%2C%22utm_medium%22%3A%20%22Func%22%2C%22utm_campaign%22%3A%20%22join104top%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fcase.104.com.tw%2F%22%2C%22%24initial_referring_domain%22%3A%20%22case.104.com.tw%22%2C%22%24search_engine%22%3A%20%22google%22%7D",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}


def get_new_jobs_info():
    try:
        res = requests.get(url, headers=headers)
        jobs_info = res.json()
    except Exception as ex:
        print(ex)
        return

    result = db.fetchAll("SELECT demandId FROM job_list")

    for job_data in jobs_info["data"]:
        if job_data["assignPlace"] is not None:
            continue

        for db_data in result:
            if db_data[0] == job_data["demandId"]:
                break
        else:
            demandId = job_data["demandId"]
            title = job_data["title"]
            min_price = job_data["minPrice"]
            max_price = job_data["maxPrice"]
            online_date = " ".join(re.search(r"(\d+-\d+-\d+)T(\d+:\d+:\d+).+", job_data["onlineDate"]).groups())
            desc = job_data["desc"].strip()
            unit = job_data["unit"]  # 0代表論件, 1代表時薪
            price_range = f"論件 NT$ {format(min_price, ',')} ~ {format(max_price, ',')} 元" if unit == 0 else f"時薪 NT$ {min_price} ~ {max_price} 元"
            basicId = job_data["basicId"]

            db.execute("INSERT INTO job_list (demandId, title, min_price, max_price, online_date, info_data) VALUES (%s, %s, %s, %s, %s, %s)", (demandId, title, min_price, max_price, online_date, json.dumps(job_data)))
            interval_line = '=' * 25 + "\n"
            send_broadcast_message(f"💼 有新的案件機會囉！\n\n【{title}】\n{price_range}\n連結: https://top.104.com.tw/caseInfo?basicId={basicId}&demandId={demandId}\n{interval_line}{desc}\n{interval_line}{online_date}")
            print(f"[{time.strftime('%H:%M:%S')}] 新的案件機會已通知並加進資料庫中: ", "[" + demandId + "]", title)