import json
import time

import requests

from bot_utils import send_broadcast_message
from database.get_db import db


def get_new_pro360_info():
    headers = {
        "x-pro360-rest-api-key":"5F7C3FF875C97E5B719D059444C1570F",
        "x-pro360-user-session-token":"6evbbg8v8sfpv980loa6fpqmo2"
    }

    session = requests.session()
    res = session.get("https://api.pro360.com.tw/quote_bids/index/type:myworks/page:1/page_size:12/filter_id:8.json", headers=headers)
    quote_bids = res.json()["quote_bids"]

    current_milli_time = (lambda: int(round(time.time() * 1000)))
    posted_ids = db.fetchAll("SELECT id FROM pro360_list")

    for i in range(len(quote_bids)):
        quote_bid = quote_bids[i]
        id = quote_bid["QuoteBid"]["id"]
        if id not in map(lambda ele: str(ele[0]), posted_ids):
            QuoteRequest = quote_bid["QuoteRequest"]
            title = QuoteRequest["title"]
            manual_fee = QuoteRequest["manual_fee"]  # 聯繫費用
            bid_count_limit = QuoteRequest["bid_count_limit"]  # 最大連繫名額
            quote_bid_count = QuoteRequest["quote_bid_count"]  # 已連繫次數
            bid_count_remaining = int(bid_count_limit) - int(quote_bid_count)  # 剩餘聯繫名額
            form_summary = json.loads(QuoteRequest["form_summary"])
            content = ""
            count = 0
            for k in form_summary:
                count+=1
                content += "📌" + k + "\n"
                if type(form_summary[k]) == list:
                    content += "、".join(form_summary[k])
                else:
                    content += form_summary[k]
                if count != len(form_summary): content += "\n\n"

            online_date = QuoteRequest["created"]
            interval_line = '=' * 25 + "\n"
            send_broadcast_message(f"💼 Pro360有新的案件機會囉！\n\n類型: {title}\n聯繫費用: ${manual_fee}\n剩餘名額: {bid_count_remaining} / {bid_count_limit}\n連結: https://www.pro360.com.tw/dashboard/requests/{id}\n{interval_line}{content}\n{interval_line}{online_date}")
            db.execute("INSERT INTO pro360_list VALUES (?, ?, ?)", (id, current_milli_time(), form_summary))
            print(f"[{time.strftime('%H:%M:%S')}] 新的案件機會已通知並加進資料庫中: ", "[" + id + "]", title)
