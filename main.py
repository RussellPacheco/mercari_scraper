#!env/bin/python

from dotenv import load_dotenv
import os
import json
from datetime import datetime
import argparse
from connection import Mercari, ROOT_PATH
import grpc
import transmitter.transmitter_pb2 as transmitter_pb2
import transmitter.transmitter_pb2_grpc as transmitter_pb2_grpc
from google.protobuf.wrappers_pb2 import StringValue

# from linebot import LineBotApi
# from linebot.models import TextSendMessage
# from linebot.exceptions import LineBotApiError


load_dotenv()

parser = argparse.ArgumentParser(prog="main.py", description="Automatically search Mercari and send all unseen items to your line account")
parser.add_argument("keyword", help="Search keyword")
parser.add_argument("--price-min")
parser.add_argument("--price-max")
parser.add_argument("-e", "--electronics", help="Search all electronics", action="store_true")
parser.add_argument("-c", "--computers", help="Search specifically for computer related items", action="store_true")
parser.add_argument("-p", "--pc-parts", help="Search even more specifically for pc parts", action="store_true")

args = parser.parse_args()

mercari_api = Mercari()

#line_bot_api = LineBotApi(os.getenv("CONNECTION_TOKEN"))
channel = grpc.insecure_channel("localhost:50051")

def previously_viewed_item_check(item_list: list):
    data_file_path = None

    if os.name == "nt":
        data_file_path = f"{ROOT_PATH}\\data.json"
    elif os.name == "posix":
        data_file_path = f"{ROOT_PATH}/data.json"

    if not os.path.exists(data_file_path):
        json_file = open(data_file_path, "w")
        json.dump({}, json_file)
        json_file.close()

    json_file = open(data_file_path)
    data = json.load(json_file)
    json_file.close()

    previously_viewed_items = [key for key in data.keys()]
    new_items = []
    items_to_update = []

    labled_new_items = {}
    labled_items_to_update = {}

    for item in item_list:
        if item["item"] not in previously_viewed_items:
            new_items.append(item)
        else: # Check if the price has changed
            if data[item["item"]]["last_price"] != item["price"]:
                items_to_update.append(item)

    if len(new_items) > 0:
        print("There are unseen items.")

        json_file = open(data_file_path)
        data = json.load(json_file)
        json_file.close()

        for item in new_items:
            data[item["item"]] = {
                "price": item["price"], 
                "last_price": item["price"],
                "original_price": item["price"], 
                "viewed": str(datetime.now()), 
                "updated": str(datetime.now())
            }
            labled_new_items[item["item"]] = data[item["item"]]

        with open(data_file_path, "w") as json_file:
            json.dump(data, json_file)
            json_file.close()
   
    if len(items_to_update) > 0:
        print("There are items with updated prices")

        json_file = open(data_file_path)
        data = json.load(json_file)
        json_file.close()

        for item in items_to_update:
            data[item["item"]] = {
                "price": item["price"], 
                "last_price": data[item["item"]]["price"],
                "original_price": data[item["item"]]["original_price"],
                "viewed": data[item["item"]]["viewed"], 
                "updated": str(datetime.now())
            }
            labled_items_to_update[item["item"]] = data[item["item"]]

        with open(data_file_path, "w") as json_file:
            json.dump(data, json_file)
            json_file.close()

    if len(labled_new_items) > 0 or len(labled_items_to_update) > 0:
        print(f"Sending new items to line_msg {labled_new_items}")
        print(f"Sending updated items to line_msg {labled_items_to_update}")
        return labled_new_items, labled_items_to_update

    if len(labled_new_items) == 0 and len(labled_items_to_update) == 0:
        print("There are no new items")
        return False
    

def transmit_msg(data_to_send):
    grpc_url = f"{os.getenv('GRPC_HOST')}:{os.getenv('GRPC_PORT')}"
    new_items, updated_items = data_to_send

    for item in new_items.keys():

        message = f"""Hey Russell,
        
There is a new item.

Price: {new_items[item]['price']}円

Link: {item}"""

        try:
            # line_bot_api.push_message(os.getenv("USER_ID"), TextSendMessage(text=message))
            with grpc.insecure_channel(grpc_url) as channel:
                stub = transmitter_pb2_grpc.TransmitterStub(channel)
                stub.SendMessage(
                    transmitter_pb2.Message(
                        source=transmitter_pb2.Source(name="Mercari Scraper"), 
                        type=transmitter_pb2.MessageType.TEXT, 
                        text=StringValue(value=message)
                    )
                )
        except Exception as e:
            print(f"[ERROR]:{e}")

    for item in updated_items.keys():
        message = f"""Hey Russell,
            
There is an updated item.

New Price: {updated_items[item]['price']}円
Last Price: {updated_items[item]['last_price']}円
Original Price: {updated_items[item]['original_price']}円

Link: {item}"""

        try:
            with grpc.insecure_channel(grpc_url) as channel:
                stub = transmitter_pb2_grpc.TransmitterStub(channel)
                stub.SendMessage(
                    transmitter_pb2.Message(
                        source=transmitter_pb2.Source(name="Mercari Scraper"), 
                        type=transmitter_pb2.MessageType.TEXT, 
                        text=StringValue(value=message)
                    )
                )
        except Exception as e:
            print(f"[ERROR]:{e}")

if __name__ == "__main__":
    print("Checking Mercari for items")
    results = mercari_api.fetch_items_pagination(
        keyword=args.keyword,
        price_min=args.price_min,
        price_max=args.price_max,
        e_flag=args.electronics,
        c_flag=args.computers,
        p_flag=args.pc_parts)
    print(f"There are {len(results)} results")

    print("Checking to see if items have been previously seen")
    items_to_message = previously_viewed_item_check(results)

    if items_to_message is not False:
        transmit_msg(items_to_message)