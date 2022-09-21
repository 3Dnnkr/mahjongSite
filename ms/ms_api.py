import asyncio
import hashlib
import hmac
import logging
import random
import uuid
import urllib.request, json, codecs

import aiohttp

from ms.base import MSRPCChannel
from ms.rpc import Lobby
from ms import protocol_pb2 as pb
from google.protobuf.json_format import MessageToJson

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

MS_HOST = "https://game.maj-soul.com"


async def load_paifu():
    username = "3dnnkr@gmail.com"
    password = "ramanujan1729Ac"
    #uuid = "191117-5c090817-4837-4760-8c3e-420af823832a" # ～2019/12/31
    #uuid = "210716-8c69db69-0ce0-4a93-b263-441335581091" # 2020/01/01～2021/07/28
    uuid = "220714-faa69c2d-8321-4748-b027-0b13edfeb704"  # 2021/07/28～
    lobby, channel, version_to_force = await connect()
    await login(lobby, username, password, version_to_force)
    paifu = await load_and_process_game_log(lobby, uuid)
    await channel.close()
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
    req.client_version_string = 'web-0.10.154' # update from 'web-0.9.333'
    res = await lobby.fetch_game_record(req)
    paifu = json.loads(MessageToJson(res, preserving_proto_field_name=True, including_default_value_fields=False)) # ResGameRecord => JSON => Dict

    # get res.data from data_url
    if not res.data and res.data_url:
        logging.info("Loading data url")
        response = urllib.request.urlopen(res.data_url)
        raw_data = response.read()
        res.data = raw_data

    # decode res.data(Byte => Wrapper)
    wrapper = pb.Wrapper()
    wrapper.ParseFromString(res.data)
    paifu["data"] = json.loads(MessageToJson(wrapper, preserving_proto_field_name=True))

    # decode wrapper.data(Byte => GameDetailRecords)
    details = pb.GameDetailRecords()
    details.ParseFromString(wrapper.data)
    paifu["data"]["data"] = json.loads(MessageToJson(details, preserving_proto_field_name=True))

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
    }

    if details.version == 0:
        # decode details.records
        for i, rec in enumerate(details.records):
            # decode record(Byte => Wrapper)
            record = pb.Wrapper()
            record.ParseFromString(rec)
            paifu["data"]["data"]["records"][i] = json.loads(MessageToJson(record, preserving_proto_field_name=True))

            # decode record.data(Byte => SomeRecord)
            if record.name in record_dic:
                record_data = record_dic[record.name]()
                record_data.ParseFromString(record.data)
                paifu["data"]["data"]["records"][i]["data"] = json.loads(MessageToJson(record_data, preserving_proto_field_name=True))

    elif details.version == 210715:
        # decode details.actions
        for i, action in enumerate(details.actions):
            if action.type == 1:
                # decode action.result(Byte => Wrapper)
                result = pb.Wrapper()
                result.ParseFromString(action.result)
                paifu["data"]["data"]["actions"][i]["result"] = json.loads(MessageToJson(result, preserving_proto_field_name=True))

                # decode action.result.data(Byte => SomeRecord)
                if result.name in record_dic:
                    result_data = record_dic[result.name]()
                    result_data.ParseFromString(result.data)
                    paifu["data"]["data"]["actions"][i]["result"]["data"] = json.loads(MessageToJson(result_data, preserving_proto_field_name=True))

    else:
        print("Unknown version: {}".format(details.version))

    # save as json
    fw = codecs.open('paifu.json', 'w', 'utf-8')
    json.dump(paifu, fw, indent=2, ensure_ascii=False)
    fw.close()
    return paifu
