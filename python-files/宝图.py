from util.image_clicker import ImageOffsetClicker
from util.random_mouse import RandomMouseMover
import asyncio

# Your 5 region definitions
regions = [
    (8, 49, 1034, 810),
    (1052, 57, 2070, 810),
    (2091, 56, 3105, 808),
    (13, 880, 1027, 1630),
    (1054, 880, 2066, 1636)
]

# Random mouse mover instance
mover = RandomMouseMover(
    speed=0.5,
    base_jitter=200,
    steps=10,
    pause_chance=0.15,
    pause_range=(0.1, 0.3)
)
clicker = ImageOffsetClicker(regions, mover)

async def run_task():
    # Step 1: Find images in regions
    # 活动
    clicker.click_boxes((305, 67, 335, 99))
    found_boxes = await clicker.find_image_in_regions("img/map.png", offset=(262, 19, 331, 58))
    # Step 2: Click on those positions
    for box in found_boxes:
        converted_box = tuple(map(int, box))
        clicker.mover.click(converted_box)
    
    # 点击开始
    clicker.click_boxes((744, 518, 990, 551))

# 点击队伍
mover.click((1980, 972, 2073, 1011))

# 请出队伍 5号位
mover.click((1868, 1267,2063, 1314))
mover.click((1718, 1260,1831, 1311))
mover.click((1596, 1304,1718, 1338))

# 请出队伍 4号位
mover.click((1867, 1210,2068, 1259))
mover.click((1718, 1257,1828, 1315))
mover.click((1596, 1304,1718, 1338))

# 请出队伍 3号位
mover.click((1864, 1147,2073, 1198))
mover.click((1715, 1213,1829, 1269))
mover.click((1596, 1304,1718, 1338))

# 请出队伍 2号位
mover.click((1865, 1086,2075, 1140))
mover.click((1715, 1158,1828, 1213))
mover.click((1596, 1304,1718, 1338))

# 退出队伍
mover.click((1868, 1026,2073, 1076))
mover.click((1716, 1099,1827, 1153))
mover.click((1596, 1304,1718, 1338))

# 开始宝图任务
asyncio.run(run_task())

