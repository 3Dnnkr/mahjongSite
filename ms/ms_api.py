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
    
    # return paifu if error
    if paifu.get("error"):
        print("Error Code: " + str(paifu.get("error").get("code")))
        return paifu
    
    # convert ms paifu to tenhou paifu (Dict to Dict)
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


def get_paifuinfos_from(paifudata):
    # url encoding
    paifus = []
    names = []
    ju_dict = { 
         0:"東一局",  1:"東二局",  2:"東三局",  3:"東四局",
         4:"南一局",  5:"南二局",  6:"南三局",  7:"南四局",
         8:"西一局",  9:"西二局", 10:"西三局", 11:"西四局",
        12:"北一局", 13:"北二局", 14:"北三局", 15:"北四局",
    }
    for log in paifudata["log"]:
        paifu = {}
        paifu["title"] = paifudata["title"]
        paifu["name"]  = paifudata["name"]
        paifu["rule"]  = paifudata["rule"]
        paifu["log"]   = [log]
        paifu = json.dumps(paifu)
        paifu = urllib.parse.quote(paifu)
        paifus.append(paifu)

        ju    = log[0][0]
        chang = log[0][1]
        names.append(ju_dict.get(ju)+" "+str(chang)+"本場")
    
    paifu_infos = zip(paifus, names)
    return paifu_infos

def get_scoreinfos_from(paifudata):
    # create score_data
    score_data = [{},{},{},{}]
    for name, dic in zip(paifudata["name"], score_data):
        dic["name"] = name
        dic["scores"] = []

    for log in paifudata["log"]:
        for i,dic in enumerate(score_data):
            dic["scores"].append(log[1][i])

    for i, dic in enumerate(score_data):
        dic["scores"].append(paifudata["sc"][i*2])

    if score_data[3]["scores"][0] == 0:
        score_data.pop() # remove last data if sanma

    # create labels
    labels = []
    ju_dict = { 
         0:"E1-",  1:"E2-",  2:"E3-",  3:"E4-",
         4:"S1-",  5:"S2-",  6:"S3-",  7:"S4-",
         8:"W1-",  9:"W2-", 10:"W3-", 11:"W4-",
        12:"N1-", 13:"N2-", 14:"N3-", 15:"N4-",
    }
    for log in paifudata["log"]:
        ju    = log[0][0]
        chang = log[0][1]
        labels.append(ju_dict.get(ju)+str(chang))
    labels.append("END")

    score_infos = {}
    score_infos["score_data"] = score_data
    score_infos["labels"]     = labels
    return score_infos