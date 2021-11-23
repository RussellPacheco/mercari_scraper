#!env/bin/python

from dotenv import load_dotenv
from connection import Mercari, ROOT_PATH
import os
import json
from datetime import datetime
import argparse

from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

load_dotenv()

mercari_api = Mercari()
line_bot_api = LineBotApi(os.getenv("CONNECTION_TOKEN"))
parser = argparse.ArgumentParser(prog="main.py", description="Automatically search Mercari and send all unseen items to your line account")

parser.add_argument("keyword", help="Search keyword")
parser.add_argument("--price-min")
parser.add_argument("--price-max")
parser.add_argument("-e", "--electronics", help="Search all electronics", action="store_true")
parser.add_argument("-c", "--computers", help="Search specifically for computer parts", action="store_true")

args = parser.parse_args()

def previously_viewed_item_check(item_list: list):

    data_file_path = None

    if os.name == "nt":
        data_file_path = f"{ROOT_PATH}\\data.json"
    elif os.name == "posix":
        data_file_path = f"{ROOT_PATH}/data.json"

    if not os.path.exists(data_file_path):
        json_file = open("data.json", "w")
        json.dump({}, json_file)
        json_file.close()

    json_file = open(data_file_path)
    data = json.load(json_file)
    json_file.close()

    previously_viewed_items = [key for key in data.keys()]

    new_items = []
    for item in item_list:
        if item[1] not in previously_viewed_items:
            new_items.append(item)

    if len(new_items) > 0:
        print("There are unseen items.")
        print(f"Sending new items to line_msg {new_items}")

        json_file = open("data.json")
        data = json.load(json_file)
        json_file.close()

        for item in new_items:
            data[item[1]] = {"price": item[0], "viewed": str(datetime.now())}

        with open(data_file_path, "w") as json_file:
            json.dump(data, json_file)
            json_file.close()

        return new_items
    print("There are no new items")
    return False


def line_msg(data_to_send):

    for item in data_to_send:

        message = f"Hey Russell,\n\nThere is a new item.\n\nPrice: {item[0]}円\nLink: {item[1]}"

        try:
            line_bot_api.push_message(os.getenv("USER_ID"), TextSendMessage(text=message))
        except LineBotApiError as e:
            print(f"[ERROR]:{e}")


if __name__ == "__main__":
    print("Checking Mercari for items")
    results = mercari_api.fetch_items_pagination(
        keyword=args.keyword,
        price_min=args.price_min,
        price_max=args.price_max,
        e_flag=args.electronics,
        c_flag=args.computers)
    print(f"There are {len(results[0])} results")

    print("Checking to see if items have been previously seen")
    items_to_message = previously_viewed_item_check(results[0])

    if items_to_message is not False:
        line_msg(items_to_message)