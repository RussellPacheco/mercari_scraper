from dotenv import load_dotenv
import os
from mercari import Mercari
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

load_dotenv()

# if __name__ == '__main__':
#     main()

mercari_api = Mercari()

print('_' * 80)
print(mercari_api.name)
results = mercari_api.fetch_items_pagination(keyword="2070 -ジャンク",price_min=40000, price_max=60000)
print(f"There are {len(results[0])} results")
print(results[0])


line_bot_api = LineBotApi(os.getenv("CONNECTION_TOKEN"))

try:
    line_bot_api.push_message("<USERID>", )