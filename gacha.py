import os
import random
import json
from PIL import Image
from math import ceil

from nonebot.exceptions import CQHttpError

from hoshino.typing import *
from hoshino import R, Service, priv
from hoshino.util import pic2b64

sv = Service('arknights', enable_on_default=True, visible=False)
fd = os.path.dirname(__file__)


# 加载配置：
# 加载干员表、up表
with open("./hoshino/modules/arknights/characters.json", "r", encoding='utf-8') as json_file:
    d = json.loads(json_file.read())
# 从干员表中移除up角色和6★限定角色
for i in d["6_up"]:
    d["6"].remove(i)
for i in d["6_disable"]:
    try:
        d["6"].remove(i)
    except(ValueError):
        pass
for i in d["5_up"]:
    d["5"].remove(i)
for i in d["4_up"]:
    d["4"].remove(i)
# print(d)
rate = [0, 0, 0, 40, 50, 8, 2]
rate_last = [0, 0, 0, 0, 0, 98, 2]


def gacha_arknights(rate):
    # 抽星数
    start = 0
    index = 0
    randnum = random.random() * 100
    for index, scope in enumerate(rate):
        start += scope
        if randnum <= start:
            break
    return index


def arknights_gacha_info_text():
    # 文字：
    up_4 = d["4_up"]
    up_5 = d["5_up"]
    up_6 = d["6_up"]
    msg = "本期up：\n"
    for i in up_6:
        msg += i + " " + "★" * 6 + "\n"
    for i in up_5:
        msg += i + " " + "★" * 5 + "\n"
    for i in up_4:
        msg += i + " " + "★" * 4 + "\n"
    # msg += "5★、6★up角色出率占所属星级的50%\n4★up角色出率占4★的20%"
    msg += f"6★up角色出率占6★的{d['6_up_rate']*100}%\n5★up角色出率占5★的{d['5_up_rate']*100}%\n"
    if len(d['4_up'])>0:
        msg += f"4★up角色出率占4★的{d['4_up_rate']*100}%\n"
    return msg


def arknights_gacha_info_pic():
    # 图片：
    info_pic_file = Image.open(f'./res/img/arknights/gacha_info.png')
    pic = pic2b64(info_pic_file)
    pic = MessageSegment.image(pic)
    return pic


@sv.on_fullmatch('重载方舟配置',only_to_me = True)
async def arknights_reload_condig(bot,ev):
    global d
    with open("./hoshino/modules/arknights/characters.json", "r", encoding='utf-8') as json_file:
        d = json.loads(json_file.read())
    # 从干员表中移除up角色和6★限定角色
    for i in d["6_up"]:
        d["6"].remove(i)
    for i in d["6_disable"]:
        try:
            d["6"].remove(i)
        except(ValueError):
            pass
    for i in d["5_up"]:
        d["5"].remove(i)
    for i in d["4_up"]:
        d["4"].remove(i)
    await bot.send(ev,"重载成功")


@sv.on_fullmatch(('查看方舟卡池','方舟卡池','看看方舟卡池'),only_to_me = True)
async def arknights_gacha_info(bot,ev):
    # 查看卡池
    await bot.send(ev, arknights_gacha_info_text())
    # await bot.send(ev, arknights_gacha_info_pic())
    # await bot.send(ev, "★★★★★★：年[限定] \ 阿（占6★出率的70%）\n★★★★★：吽（占5★出率的50%）")
    

@sv.on_fullmatch(('方舟十连','明日方舟十连','十次寻访'),only_to_me = True)
async def arknights_gacha_10(bot,ev):
    # 先抽星数
    gacha_result = []  
    
    for i in range(10):  # 无保底策略
        gacha_result.append(gacha_arknights(rate))  # 无保底
    width = 640  # 最终长度
    height = 192  # 最终高度
    imagefile = []
    for i in gacha_result:  # i是星数
        if i == 4 and random.random() < d["4_up_rate"] and len(d[str(i) + "_up"]) > 0:  # 直读up_date
            name = random.choice(d[str(i) + "_up"])
        elif i == 5 and random.random() < d["5_up_rate"] and len(d[str(i) + "_up"]) > 0:  # 直读up_date
            name = random.choice(d[str(i) + "_up"])
        elif i == 6 and random.random() < d["6_up_rate"] and len(d[str(i) + "_up"]) > 0:  # 直读up_date
            name = random.choice(d[str(i) + "_up"])
        else:  # 否则抽不up的
            name = random.choice(d[str(i)])  # 根据星数，随机选取
        imagefile.append(Image.open(f'./res/img/arknights/{i}/{name}.jpg'))
    target = Image.new('RGB', (width, height))
    left = 0
    right = 64
    for image in imagefile:
        target.paste(image, (left, 0, right, 192))
        left += 64  # 左上角
        right += 64  # 右下角
    # target.save(os.path.join(fd , 'cache/gacha_10_result.jpg'), quality=10)
    # 编辑消息
    msg = ""
    if 6 in gacha_result:
        msg = "恭喜出货"
        #await bot.send(ev, "恭喜出货")
    elif 5 in gacha_result:
        pass
        # await bot.send(ev, "")
    elif (5 not in gacha_result) and (6 not in gacha_result) and (4 in gacha_result):
        msg = "紫气东来"
        # await bot.send(ev, "紫气东来")
    elif 4 not in gacha_result:
        msg = "这……这种事情发生的概率只有0.6%吧……"
    
    pic = pic2b64(target)
    pic = MessageSegment.image(pic)
    res = f"{msg}{pic}"
    await bot.send(ev, res, at_sender = True)


@sv.on_fullmatch(('方舟单抽','明日方舟单抽','单次寻访'),only_to_me = True)
async def arknights_gacha_1(bot,ev):
    gacha_result = gacha_arknights(rate)  # 星数
    # name = random.choice(d[str(gacha_result)])  # 干员名字
    if gacha_result != 3 and random.random() < d[f"{gacha_result}_up_rate"] and len(d[str(gacha_result) + "_up"]) > 0:  # 直读up_rate
        name = random.choice(d[str(gacha_result) + "_up"])
    else:  # 否则抽不up的
        name = random.choice(d[str(gacha_result)])  # 根据星数，随机选取
    msg = "\n" + name + "★" * gacha_result
    imagefile = (Image.open(f'./res/img/arknights/{gacha_result}/{name}.jpg'))
    pic = pic2b64(imagefile)
    pic = MessageSegment.image(pic)
    res = f"{msg}{pic}"
    await bot.send(ev, res, at_sender = True)

@sv.on_fullmatch(('方舟来一井','明日方舟来一井','三百次寻访'),only_to_me = True)
async def arknights_gacha_tennjyou(bot,ev):
    # 先抽星数
    global rate
    msg = ""  # 发送的句子
    gacha_result = []  # 抽星结果
    total_result = [0, 0, 0, 0]  # 抽星结果统计
    msg_tennjyou = ""  # 保底获取结果
    no_UR = -50
    for i in range(300):
        if no_UR > 0:
            # 触发保底
            rate = [0, 0, 0, 40 - no_UR * 2 * 40 / 98, 50 - no_UR * 2 * 50 / 98, 8 - no_UR * 8 / 98 * 2, 2 + no_UR * 2]
        reality = gacha_arknights(rate)
        if reality < 6:
            # 没有6星
            no_UR += 1
        else:
            # 抽到6，给出保底提示，重置概率
            if rate[6] > 2:
                msg_tennjyou += f"第{i + 1}抽触发保底，6★概率：{rate[6]}%\n"
            no_UR = -50
            rate = [0, 0, 0, 40, 50, 8, 2]
        total_result[reality - 3] += 1
        gacha_result.append(reality)
    # 最后一定要重置概率
    rate = [0, 0, 0, 40, 50, 8, 2]
    # 抽6★干员
    imagefile = []  # 6★干员名字
    for i in range(total_result[3]):  # 只抽取6星干员并合成图片
        if random.random() < d["6_up_rate"] and len(d["6_up"]) > 0:  # 春节up池，6★up 70%
            name = random.choice(d["6_up"])
        else:  # 否则抽不up的
            name = random.choice(d["6"])  # 根据星数，随机选取
        imagefile.append(Image.open(f'./res/img/arknights/6/{name}.jpg'))
    # 根据干员名字合成图片
    max_col = 8
    col = total_result[3] if total_result[3] < max_col else max_col  # 合成图的列数
    row = ceil(total_result[3] / col)  # 合成图的行数
    target = Image.new('RGB', (col * 64, row * 192))
    left = 0
    right = 64
    top = 0
    bottom = 192
    for image in imagefile:
        target.paste(image, (left, top, right, bottom))
        if left == (col-1) * 64:
            # 到达换行边界
            left = 0
            right = 64
            top += 192
            bottom += 192
        else:
            left = left + 64
            right = right + 64
    msg += f"\n本次抽取结果统计：\n6★：{total_result[3]}名，5★：{total_result[2]}名\n4★：{total_result[1]}名，3★：{total_result[0]}名\n"
    msg += msg_tennjyou
    pic = MessageSegment.image(pic2b64(target))
    res = f"{msg}{pic}"
    await bot.send(ev, res, at_sender = True)