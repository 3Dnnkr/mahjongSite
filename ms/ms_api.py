import asyncio
import hashlib
import hmac
import logging
import random
import uuid
import urllib.request, json, re

import aiohttp

from ms.convert import convert
from ms.base import MSRPCChannel
from ms.rpc import Lobby
from ms import protocol_pb2 as pb
from google.protobuf.json_format import MessageToJson

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

MS_HOST = "https://game.maj-soul.com"


async def load_paifu(username, password, url):
    
    # login to Mahjong Soul
    lobby, channel, version_to_force = await connect()
    await login(lobby, username, password, version_to_force)
    
    # get ms paifu (Dict)
    uuid = url_to_uuid(url)
    paifu = await load_and_process_game_log(lobby, uuid)
    await channel.close()
    
    # # save as json
    # fw = codecs.open('paifu.json', 'w', 'utf-8')
    # json.dump(paifu, fw, indent=2, ensure_ascii=False)
    # fw.close()
    
    # return paifu if error
    if paifu.get("error"):
        print("Error Code: " + str(paifu.get("error").get("code")))
        return paifu
    
    # convert ms to tenhou (Dict)
    paifu = convert(paifu)
    return paifu

async def connect():
    async with aiohttp.ClientSession() as session:
        async with session.get("{}/1/version.json".format(MS_HOST)) as res:
            version = await res.json()
            logging.info(f"Version: {version}")
            version = version["version"]
            version_to_force = version.replace(".w", "")

        async with session.get("{}/1/v{}/config.json".format(MS_HOST, version)) as res:
            config = await res.json()
            logging.info(f"Config: {config}")

            url = config["ip"][0]["region_urls"][1]["url"]

        async with session.get(url + "?service=ws-gateway&protocol=ws&ssl=true") as res:
            servers = await res.json()
            logging.info(f"Available servers: {servers}")

            servers = servers["servers"]
            server = random.choice(servers)
            endpoint = "wss://{}/gateway".format(server)

    logging.info(f"Chosen endpoint: {endpoint}")
    channel = MSRPCChannel(endpoint)

    lobby = Lobby(channel)

    await channel.connect(MS_HOST)
    logging.info("Connection was established")

    return lobby, channel, version_to_force

async def login(lobby, username, password, version_to_force):
    logging.info("Login with username and password")

    uuid_key = str(uuid.uuid1())

    req = pb.ReqLogin()
    req.account = username
    req.password = hmac.new(b"lailai", password.encode(), hashlib.sha256).hexdigest()
    req.device.is_browser = True
    req.random_key = uuid_key
    req.gen_access_token = True
    req.client_version_string = f"web-{version_to_force}"
    req.currency_platforms.append(2)

    res = await lobby.login(req)
    token = res.access_token
    if not token:
        logging.error("Login Error:")
        logging.error(res)
        return False

    return True

async def load_and_process_game_log(lobby, uuid):
    logging.info("Loading game log")

    # get res(ResGameRecord)
    req = pb.ReqGameRecord()
    req.game_uuid = uuid
    req.client_version_string = 'web-0.10.157' # update from 'web-0.9.333'
    res = await lobby.fetch_game_record(req)
    paifu = json.loads(MessageToJson(res, preserving_proto_field_name=True, including_default_value_fields=True)) # ResGameRecord => JSON => Dict

    # get res.data from data_url
    if not res.data and res.data_url:
        logging.info("Loading data url")
        response = urllib.request.urlopen(res.data_url)
        raw_data = response.read()
        res.data = raw_data

    # decode res.data(Byte => Wrapper)
    wrapper = pb.Wrapper()
    wrapper.ParseFromString(res.data)
    paifu["data"] = json.loads(MessageToJson(wrapper, preserving_proto_field_name=True, including_default_value_fields=True))

    # decode wrapper.data(Byte => GameDetailRecords)
    details = pb.GameDetailRecords()
    details.ParseFromString(wrapper.data)
    paifu["data"]["data"] = json.loads(MessageToJson(details, preserving_proto_field_name=True, including_default_value_fields=True))

    # prepare record_dic
    record_dic = {
        ".lq.RecordNewRound":pb.RecordNewRound,
        ".lq.RecordDealTile":pb.RecordDealTile,
        ".lq.RecordDiscardTile":pb.RecordDiscardTile,
        ".lq.RecordChiPengGang":pb.RecordChiPengGang,
        ".lq.RecordAnGangAddGang":pb.RecordAnGangAddGang,
        ".lq.RecordHule":pb.RecordHule,
        ".lq.RecordNoTile":pb.RecordNoTile,
        ".lq.RecordLiuJu":pb.RecordLiuJu,
        ".lq.RecordBaBei":pb.RecordBaBei,
    }

    if details.version == 0:
        # decode details.records
        for i, rec in enumerate(details.records):
            # decode record(Byte => Wrapper)
            record = pb.Wrapper()
            record.ParseFromString(rec)
            paifu["data"]["data"]["records"][i] = json.loads(MessageToJson(record, preserving_proto_field_name=True, including_default_value_fields=True))

            # decode record.data(Byte => SomeRecord)
            if record.name in record_dic:
                record_data = record_dic[record.name]()
                record_data.ParseFromString(record.data)
                paifu["data"]["data"]["records"][i]["data"] = json.loads(MessageToJson(record_data, preserving_proto_field_name=True, including_default_value_fields=True))

    elif details.version == 210715:
        # decode details.actions
        for i, action in enumerate(details.actions):
            if action.type == 1:
                # decode action.result(Byte => Wrapper)
                result = pb.Wrapper()
                result.ParseFromString(action.result)
                paifu["data"]["data"]["actions"][i]["result"] = json.loads(MessageToJson(result, preserving_proto_field_name=True, including_default_value_fields=True))

                # decode action.result.data(Byte => SomeRecord)
                if result.name in record_dic:
                    result_data = record_dic[result.name]()
                    result_data.ParseFromString(result.data)
                    paifu["data"]["data"]["actions"][i]["result"]["data"] = json.loads(MessageToJson(result_data, preserving_proto_field_name=True, including_default_value_fields=True))

    else:
        print("Unknown version: {}".format(details.version))

    logging.info("Loaded game log")
    return paifu

def url_to_uuid(url):
    # url has 4 patterns
    # url = "220714-faa69c2d-8321-4748-b027-0b13edfeb704"
    # url = "220714-faa69c2d-8321-4748-b027-0b13edfeb704_a422132067"
    # url = "https://game.mahjongsoul.com/?paipu=220714-faa69c2d-8321-4748-b027-0b13edfeb704"
    # url = "https://game.mahjongsoul.com/?paipu=220714-faa69c2d-8321-4748-b027-0b13edfeb704_a422132067"
    # url = "https://game.mahjongsoul.com/?paipu=jkjtmv-uzzvx8xv-5y97-6b9i-gcob-rssmplsvyz1q_a422132067_2"
    
    # uuid = re.search('=(.*)_a', url)
    # if uuid:
    #     return uuid
    # else:
    #     return url
    
    sp1 = url.split('=')
    sp2 = url.split('_a')

    if len(sp1)==2 and len(sp2)==2:
        print(sp1[1].split('_a')[0])
        return sp1[1].split('_a')[0]
    elif len(sp1)==2 and len(sp2)==1:
        return sp1[1]
    elif len(sp1)==1 and len(sp2)==2:
        return sp2[0]
    else:
        return url
