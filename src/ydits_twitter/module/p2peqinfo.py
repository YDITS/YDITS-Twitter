#
# p2peqinfo.py | ydits_twitter/module | YDITS for Twitter
#
# Copyright (c) 2022-2023 よね/Yone
# licensed under the Apache License 2.0
#

import json

import requests


async def get_eqinfo():
    url = "https://api.p2pquake.net/v2/history/"

    params = {"zipcode": "", "codes": "551", "limit": "1"}

    try:
        res = requests.get(url, params=params)
    except Exception as e:
        return {"status": 0x0211, "data": e}

    if res.status_code == requests.codes.ok:
        try:
            data = json.loads(res.text)
        except Exception:
            return {"status": 0x0212, "data": e}
    else:
        return {"status": 0x0213, "data": res.status_code}

    eqinfo_id = data[0]["id"]
    eqinfo_time = data[0]["earthquake"]["time"]
    eqinfo_type = data[0]["issue"]["type"]

    eqinfo_types = {
        "ScalePrompt": "震度速報",
        "Destination": "震源情報",
        "ScaleAndDestination": "震源・震度情報",
        "DetailScale": "各地の震度情報",
        "Foreign": "遠地地震情報",
        "Other": "地震情報",
    }

    if eqinfo_type in eqinfo_types:
        eqinfo_type = eqinfo_types[eqinfo_type]

    eqinfo_hypo = data[0]["earthquake"]["hypocenter"]["name"]

    if eqinfo_hypo == "":
        eqinfo_hypo = "調査中"

    eqinfo_maxScale = data[0]["earthquake"]["maxScale"]

    eqinfo_Scales = {
        -1: "調査中",
        10: "1",
        20: "2",
        30: "3",
        40: "4",
        45: "5弱",
        50: "5強",
        55: "6弱",
        60: "6強",
        70: "7",
    }

    if eqinfo_maxScale in eqinfo_Scales:
        eqinfo_maxScale_put = eqinfo_Scales[eqinfo_maxScale]

    eqinfo_magnitude = data[0]["earthquake"]["hypocenter"]["magnitude"]

    if eqinfo_magnitude == -1:
        eqinfo_magnitude = "調査中"
    else:
        eqinfo_magnitude = f"M{str(eqinfo_magnitude)}"

    eqinfo_depth = data[0]["earthquake"]["hypocenter"]["depth"]

    if eqinfo_depth == -1:
        eqinfo_depth = "調査中"
    elif eqinfo_depth == 0:
        eqinfo_depth = "ごく浅い"
    else:
        eqinfo_depth = f"約{str(eqinfo_depth)}km"

    eqinfo_tsunami = data[0]["earthquake"]["domesticTsunami"]

    eqinfo_tsunamiLevels = {
        "None": "この地震による津波の心配はありません。",
        "Unknown": "津波の影響は不明です。",
        "Checking": "津波の影響を現在調査中です。",
        "NonEffective": "若干の海面変動が予想されますが、被害の心配はありません。",
        "Watch": "この地震で津波注意報が発表されています。",
        "Warning": "この地震で津波警報等（大津波警報・津波警報あるいは津波注意報）が発表されています。",
    }

    if eqinfo_tsunami in eqinfo_tsunamiLevels:
        eqinfo_tsunami = eqinfo_tsunamiLevels[eqinfo_tsunami]

    eqinfo_timeYear = eqinfo_time[0:4]
    eqinfo_timeMonth = eqinfo_time[5:7]
    eqinfo_timeDay = eqinfo_time[8:10]
    eqinfo_timeHour = eqinfo_time[11:13]
    eqinfo_timeMinute = eqinfo_time[14:16]
    eqinfo_timeSecond = eqinfo_time[17:19]

    # if eqinfo_maxScale < 30:
    # eqinfo_report = ''
    # if eqinfo_maxScale == 30:
    # eqinfo_report = '地震による揺れを感じました。\n\n'
    # if eqinfo_maxScale == 40:
    # eqinfo_report = '地震によるやや強い揺れを感じました。\n\n'
    # if eqinfo_maxScale >= 50:
    # eqinfo_report = '地震による非常に強い揺れを感じました。\n\n'

    return {
        "status": 0x0101,
        "data": {
            "raw": data,
            "text": f"【#地震情報】\n"
            + f"{eqinfo_timeDay}日{eqinfo_timeHour}時{eqinfo_timeMinute}分頃\n"
            + f"{eqinfo_hypo}を震源とする地震がありました。\n"
            + f"最大震度は{eqinfo_maxScale_put}、地震の規模は{eqinfo_magnitude}、\n"
            + f"震源の深さは{eqinfo_depth}と推定されます。\n"
            + f"{eqinfo_tsunami}\n"
            + "#地震 #地震速報",
        },
    }
