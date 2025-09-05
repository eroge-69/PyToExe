import requests
import time
import random
import json

# 多账号配置，每个号配一个代理 IP
ACCOUNTS = [
    {
        "sid": "你的SID1",
        "proxy": "http://user:pass@ip1:port"
    },
    {
        "sid": "你的SID2",
        "proxy": "http://user:pass@ip2:port"
    }
]

# 公共请求头
def get_headers(sid):
    return {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"sid={sid}",
        "Content-Type": "application/json"
    }

# 占位：获取直播间列表
def get_live_rooms(account):
    url = "https://edith.xiaohongshu.com/api/xxx/live_list"  # 需要替换
    r = requests.get(url, headers=get_headers(account["sid"]), proxies={"http": account["proxy"], "https": account["proxy"]})
    return r.json()

# 占位：进入直播间（模拟观看）
def enter_live_room(account, room_id):
    url = f"https://edith.xiaohongshu.com/api/xxx/enter_room?room_id={room_id}"  # 需要替换
    requests.post(url, headers=get_headers(account["sid"]), proxies={"http": account["proxy"], "https": account["proxy"]})

# 占位：获取评论区用户
def get_comment_users(account, room_id):
    url = f"https://edith.xiaohongshu.com/api/xxx/comments?room_id={room_id}"  # 需要替换
    r = requests.get(url, headers=get_headers(account["sid"]), proxies={"http": account["proxy"], "https": account["proxy"]})
    return [c["user_id"] for c in r.json().get("comments", [])]

# 占位：关注用户
def follow_user(account, user_id):
    url = "https://edith.xiaohongshu.com/api/xxx/follow"  # 需要替换
    payload = {"target_user_id": user_id}
    r = requests.post(url, headers=get_headers(account["sid"]), data=json.dumps(payload), proxies={"http": account["proxy"], "https": account["proxy"]})
    return r.json()

# 主逻辑
def run(account):
    print(f"开始运行账号：{account['sid'][:6]}...")

    # 1. 获取直播间
    rooms = get_live_rooms(account)
    if not rooms:
        print("没有获取到直播间")
        return

    # 2. 随机挑一个房间
    room_id = random.choice(rooms).get("id")
    enter_live_room(account, room_id)

    # 3. 模拟停留（2-5分钟）
    stay_time = random.randint(120, 300)
    print(f"进入直播间 {room_id}，停留 {stay_time} 秒")
    time.sleep(stay_time)

    # 4. 获取评论区用户
    users = get_comment_users(account, room_id)
    if users:
        user_id = random.choice(users)
        res = follow_user(account, user_id)
        print(f"关注用户 {user_id}，结果：{res}")
    else:
        print("评论区没有用户可关注")

# 多账号循环执行
if __name__ == "__main__":
    while True:
        for acc in ACCOUNTS:
            run(acc)
            time.sleep(random.randint(600, 1800))  # 每个号间隔10-30分钟再操作