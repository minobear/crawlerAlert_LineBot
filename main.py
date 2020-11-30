import random
import time

from crawler_handler.job104_crawler import get_new_104jobs_info
from crawler_handler.market_crawler import update_access_token, get_new_market_info
from crawler_handler.pro360_crawler import get_new_pro360_info

if __name__ == '__main__':
    run_times = 0
    while True:
        print(f"[{time.strftime('%H:%M:%S')}] 正在獲取最新案件機會...")
        # get_new_market_info("forex", "外匯")
        # get_new_market_info("commodities", "商品")
        get_new_104jobs_info()
        get_new_pro360_info()

        time.sleep(random.randint(60, 120))

        run_times += 1
        if run_times >= 20:
            update_access_token()
            run_times = 0
