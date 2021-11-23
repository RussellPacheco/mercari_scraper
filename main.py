from dotenv import load_dotenv
from connection import Mercari
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

load_dotenv()

# if __name__ == '__main__':
#     main()

mercari_api = Mercari()

results = mercari_api.fetch_items_pagination(keyword="2070 -ジャンク", price_min=40000, price_max=60000)
print(f"There are {len(results[0])} results")
print(results[0])


line_bot_api = LineBotApi(os.getenv("CONNECTION_TOKEN"))


# Write code for checking if found results are new against a saved json file.

for item in results[0]:

    message = f"Hey Russell,\n\nThere is a new item.\n\nPrice: {item[0]}円\nLink: {item[1]}"
    print(message)

    # try:
    #     line_bot_api.push_message(os.getenv("USER_ID"), TextSendMessage(text=message))
    # except LineBotApiError as e:
    #     pass
