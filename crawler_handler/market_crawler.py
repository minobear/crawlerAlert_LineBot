import json
import re
import time

import requests

from bot_utils import send_broadcast_message, send_broadcast_image
from database.get_db import db

login_url = "https://api.msgforex.com/v2/user/login?lang=cn"

login_data = {
    "username": "917083875",
    "password": "soupmill"
}

session = requests.Session()
access_token = session.post(login_url, data=login_data).json()["access_token"]


def update_access_token():
    global access_token

    login_res = session.post(login_url, data=login_data)
    access_token = login_res.json()["access_token"]
    print(f"[{time.strftime('%H:%M:%S')}] update_access_token: {access_token}")

ignored_info_id = []

def get_new_market_info(type_product, type_name):
    list_url = "https://api.msgforex.com/v2/trading_strategy/lists"

    list_params = {
        "type_product":type_product,
        "page": "1",
        "limit": "9",
        "lang": "tw"
    }

    list_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "authorization": f"Bearer {access_token}"
    }

    is_first_message = True
    try:
        res = session.get(list_url, params=list_params, headers=list_headers)
    except Exception as ex:
        print(ex)
        return
    res_data = res.json()["data"]

    current_milli_time = (lambda: int(round(time.time() * 1000)))
    posted_ids = db.fetchAll("SELECT id FROM market_list WHERE post_time >= %s", (current_milli_time() - 86400000,))

    if type(res_data) is not list:  # 如果res_data並非屬於list類型, 代表得到的數據錯誤必須return
        print(type(res_data), res_data)
        return

    for i in range(len(res_data)):
        post_id = res_data[i]["id"]
        info_data = res_data[i]
        type_product = info_data["type_product"]

        pivot = int(info_data["chartlevels"]["pivot"].replace(".", ""))
        support2 = int(info_data["chartlevels"]["support2"].replace(".", ""))
        difference = abs(pivot - support2)

        if type_product == "cryptocurrency" or type_product == "stock" or type_product == "index":  # 如果商品類型為加密貨幣、股票、指數則continue
            continue
        elif type_product == "forex":
            if difference < 100:  # 如果損利價差小於100
                if post_id not in ignored_info_id:
                    print(f"[{time.strftime('%H:%M:%S')}] 已排除: {info_data['title']} 因為價差過小: {pivot} -> {support2}")
                    ignored_info_id.append(post_id)
                continue

        for posted_id in map(lambda ele: ele[0], posted_ids):
            if posted_id == post_id:
                break
        else:
            db.execute("INSERT INTO market_list (id, post_time, info_data) VALUES (%s, %s, %s)",
                       (post_id, current_milli_time(), json.dumps(info_data, ensure_ascii=False)))
            print(f"[{time.strftime('%H:%M:%S')}] 新的交易資訊已通知並加進資料庫中: ", "[" + str(post_id) + "]", info_data["title"])

            title = info_data["title"]  # 美元/加元 當日交易: 反轉向下。
            if info_data['type_product'] == "forex":
                product_name = re.search(r"(\w+/\w+) .+", title).group(1)
                title = title.replace(product_name, info_data['product_name'])  # 將可能為英文的商品名稱都改為中文: USD/CAD -> 美元/加幣
            title = "📢 " + title
            media = info_data["media"]  # 走勢分析圖
            writing_time = info_data["writing_time"]
            paragraph = info_data['paragraph']
            content = ""

            for par in range(1, len(paragraph)):
                content += "💥 " + paragraph[par]['title'] + ":\n"
                par_content = paragraph[par]['content']
                if type(par_content) is str:
                    content += par_content.strip()
                elif type(par_content) is list:  # [122.84 **, 122.64 *, 122.31 **, 122.18]
                    content += (" | ".join(par_content))  # # 122.84 ** | 122.64 * | 122.31 ** | 122.18
                if par != len(paragraph) - 1:
                    content += "\n\n"

            interval_line = '=' * 25 + "\n"
            message = f"{title}\n\n{interval_line}{content}\n{interval_line}{writing_time}"

            if is_first_message:
                send_broadcast_message("[" + time.strftime('%H:%M:%S') + "] "+ type_name +" 最新交易資訊為下 👇")
                is_first_message = False
            send_broadcast_message(message)
            send_broadcast_image(media)
