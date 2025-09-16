# 2.6 Texture fix
# Fixes Broken Characters
# Version 1.0.1
# Made by Zesilina

import os
import shutil
import time
from dataclasses import dataclass
from typing import Dict, List

print("2.6 Texture Fix v1.0.1 by Zesilina")
print("Preparing to Fix Mods.. Please Wait")
time.sleep(2)

@dataclass
class HashMap:
    old_vs_new: Dict[str, Dict[str, str]]

# Define hash replacements for Most Characters (23)
old_vs_new = {
    "Phrolova": {
        "hash = e6819fc8":"hash = c9a55c1a",
    },
    "Roccia": {
        "hash = 8c76d557":"hash = 24b44872",
        "hash = 16558db2":"hash = 859f8f55",
        "hash = 1e5ddfd3":"hash = 7515ea2e",
        "hash = 1d5ea77e":"hash = c915f11c",
        "hash = af77fb44":"hash = 84e10138",
        "hash = 6f2fd0ce":"hash = 48bd8b69",
        "hash = 87d73bf2":"hash = 21ff0f89",
        "hash = 86f266a5":"hash = 39db08c0",
        "hash = df813937":"hash = ea12c00e",
        "hash = 843152d9":"hash = 8759aa05",
        "hash = c9c9ae65":"hash = 4c151aa4",
        "hash = f10f32ad":"hash = 778a83a4",
        "hash = 718589a4":"hash = 0807dcc7",
    },
    "ResCrest": {
        "hash = c235c6a7":"hash = 21f813ba",
        "hash = 5019e88f":"hash = f47bc395",
        "hash = 3cd03f60":"hash = 1dcc0f1d",
    },
    "Shorekeeper": {
        "hash = 952d9960":"hash = 8e19fa21",
        "hash = 1fb14596":"hash = c148034c",
        "hash = a2f6b3e4":"hash = 13baf2f6",
        "hash = 2779cda7":"hash = fb389390",
        "hash = 5ae09e60":"hash = a8ef808e",
        "hash = 5e0383e5":"hash = 41b0d744",
        "hash = be955444":"hash = 529645a1",
        "hash = 6a6c419b":"hash = 2293ef8e",
        "hash = 15d38062":"hash = 5aa61d2f",
        "hash = 2cb33efd":"hash = d2f2fe3e",
        "hash = ec2a6255":"hash = b9136153",
        "hash = b7997090":"hash = b9136153",
        "hash = 49f91bc3":"hash = a7c9acc3",
        "hash = 33b7a4d5":"hash = 4b0e4779",
        "hash = 00b2fa86":"hash = 6e3d31e6",
        "hash = f510cf89":"hash = 03284c19",
    },
    "Lupa": {
        "hash = eb4d05bb":"hash = 3ba4af04",
        "hash = c5d64764":"hash = d1c82bf3",
        "hash = c347ca65":"hash = 1443c0c0",
        "hash = 84206d9f":"hash = 3cf552bd",
        "hash = 5d7d3f28":"hash = 41532ac9",
        "hash = 77ba7584":"hash = bbb18270",
        "hash = bd1bcfd8":"hash = 8f9bacd2",
        "hash = e4638507":"hash = 4c57726e",
        "hash = e541ab4b":"hash = 312fc5e4",
        "hash = 62ef42ef":"hash = b7a16140",
        "hash = 79b6c3f4":"hash = 9d5fe765",
    },
    "Cartethiya": {
        "hash = 64cd06f9":"hash = d98578ec",
        "hash = 8d9954bf":"hash = 083564da",
        "hash = fb32025d":"hash = b8b55682",
        "hash = ae8fd5fb":"hash = 6c7cc5cc",
        "hash = 3ff8b56e":"hash = 5ca9b4f0",
        "hash = c17eb9f5":"hash = 5ec1f4de",
        "hash = d10e2ae1":"hash = 6b7fb28f",
        "hash = 923d8c06":"hash = 803452b8",
        "hash = 423ec9ce":"hash = ecc1c90a",
        "hash = 7f08cd4f":"hash = a6ac08f5",
        "hash = 7ef7dba9":"hash = f953f385",
        "hash = fd0268ad":"hash = fec2f60b",
        "hash = f69958a2":"hash = c3235f6a",
        "hash = 052142b5":"hash = a8b86995",
        "hash = b0d30838":"hash = 18228dc3",
        "hash = 241a6fbe":"hash = acfd6fe0",
        "hash = 1f426e73":"hash = b2e6f707",
        "hash = c5b7aee2":"hash = ffbd8eee",
    },
    "Ciaconna": {
        "hash = d79a3f55":"hash = 24af21ae",
        "hash = fe853fcf":"hash = 10d1aeac",
        "hash = 19d3de08":"hash = a20c032a",
        "hash = 852b2b72":"hash = 342dcbc3",
        "hash = 1e072c24":"hash = 1f746639",
        "hash = 09e98e33":"hash = 0448648a",
        "hash = 4c379f61":"hash = 6f620405",
        "hash = 4358f290":"hash = de5a0f92",
        "hash = 748f8d97":"hash = 1cffa7e8",
        "hash = 2f590d3f":"hash = f58c741e",
        "hash = cca1af56":"hash = 5a41b6fa",
        "hash = 3b5e4a9b":"hash = 37400c45",
        "hash = 4e1fdf28":"hash = ed5511fe",
    },
    "Cantarella": {
        "hash = 35c01267":"hash = b6deb6c2",
        "hash = d789c54e":"hash = 3ebe428b",
        "hash = 40e95d0b":"hash = 91bf0adb",
        "hash = dcb62fb6":"hash = 76a3b6f4",
        "hash = 83a99602":"hash = 5fb46aac",
        "hash = c93ea25b":"hash = b8fe5f0a",
        "hash = 2091f4e1":"hash = 87b19749",
        "hash = 87821a93":"hash = f7dadc16",
        "hash = 94a9c5e1":"hash = 3cda6614",
        "hash = dc14e209":"hash = 9986ce50",
        "hash = 73360451":"hash = b00d33d6",
        "hash = 5db1989d":"hash = 5bbb1f80",
        "hash = 812ba53f":"hash = 787c92b8",
        "hash = 734ad993":"hash = b6deb6c2",
        "hash = 0fce3633":"hash = 0480d129",
        "hash = ef3dab0e":"hash = 8f3ebd32",
    },
    "FRover": {
        "hash = 6aac203f":"hash = 04192868",
        "hash = dcae957e":"hash = 68a6b802",
        "hash = a2207e11":"hash = 52c18227",
        "hash = be8666c3":"hash = a01c9b96",
        "hash = a2aed964":"hash = 2ff23d4c",
        "hash = 7bc718ed":"hash = 84025dca",
        "hash = 1fe7c3f1":"hash = 946ec36c",
        "hash = c39ea10a":"hash = 747ada83",
        "hash = 99d33a32":"hash = c79b5772",
        "hash = 12407ce2":"hash = ab6288a3",
        "hash = cccc4663":"hash = f85b1b15",
        "hash = c39ea10a":"hash = 747ada83",
    },
    "MRover": {
        "hash = b4855e43":"hash = 7de9f13a",
        "hash = f16d5dae":"hash = a1c0d97c",
        "hash = 56343b28":"hash = 6913dea1",
        "hash = fedfec0e":"hash = e2c06226",
        "hash = 65af60de":"hash = 6bc458a2",
        "hash = 454843d1":"hash = 7997ade0",
        "hash = 13bc29e0":"hash = 756ab255",
        "hash = db7ba06b":"hash = 5606456f",
    },
    "Carlotta": {
        "hash = 90e7de37":"hash = fc76838a",
        "hash = 6deb3b31":"hash = 6a96ee48",
        "hash = 10d7620f":"hash = ee96e964",
        "hash = abea3993":"hash = fd016c75",
        "hash = 1874bd89":"hash = 27abb610",
        "hash = aff53965":"hash = 463ab246",
        "hash = 129c321d":"hash = c7918746",
        "hash = a522548d":"hash = ea549e9a",
        "hash = 514a16b0":"hash = 30bc60f3",
        "hash = 24d244c6":"hash = 2c08bef8",
        "hash = df2d1f7b":"hash = 9ec0b80f",
    },
    "CarlottaCHair": {
        "hash = 1d394c0e":"hash = c7042488",
        "hash = 9d0b65e1":"hash = 1842bc28",
        "hash = 7f0aa102":"hash = 9ec0b80f",
    },
    "Camellya": {
        "hash = fc743d45":"hash = 422a50e2",
        "hash = 837c1b30":"hash = afadfdbd",
        "hash = 6ce51d7a":"hash = b4355151",
        "hash = 212d1d6a":"hash = 277dcf73",
        "hash = 830aecff":"hash = 9b03ba8c",
        "hash = 5f4e6f09":"hash = 4f357454",
        "hash = 5d4de02b":"hash = d8a26ff8",
        "hash = 0f14fc34":"hash = 26e023bb",
        "hash = edfe74f8":"hash = e299e4ca",
        "hash = 3a299182":"hash = fed8469a",
        "hash = 780dc4ee":"hash = 4df0b327",
    },
    "Zhezhi": {
        "hash = dc383c2f":"hash = 8f1f16f2",
        "hash = 16bf75a8":"hash = 15d8e51d",
        "hash = a39c7832":"hash = 861bd2d1",
        "hash = 2931bfa1":"hash = 42b99a48",
        "hash = 815d50a9":"hash = 9bf218c0",
        "hash = e2ff72ff":"hash = a07dd592",
        "hash = 26045936":"hash = 246557d6",
        "hash = 93904edd":"hash = 6ba42f12",
        "hash = 2c9428d3":"hash = 333217d7",
        "hash = 04f24eb9":"hash = cc072002",
        "hash = 9122d2f2":"hash = db2412ad",
        "hash = 8427b202":"hash = 082752de",
        "hash = a28f18f6":"hash = 1f4bb8ab",
    },
    "Changli": {
        "hash = d6f4003a":"hash = 89da6405",
        "hash = 30017835":"hash = fcec9218",
        "hash = 5fff67ee":"hash = 7eb470fc",
        "hash = 8094e3ca":"hash = 25e6decf",
        "hash = b54a043e":"hash = 9a3f146d",
        "hash = e0b2f0d3":"hash = c0f0b1e1",
        "hash = 1d3ad29f":"hash = fde34d42",
        "hash = 6f7a2dab":"hash = 0484ab73",
        "hash = eb70f116":"hash = 1bc98900",
        "hash = 225aad5a":"hash = a97f587b",
        "hash = a260e7f7":"hash = 8407b021",
        "hash = f23483e3":"hash = 69994531",
        "hash = dfe134cd":"hash = 3ff7cad2",
        "hash = 8a125464":"hash = 5ed7e436",
        "hash = a45bfe26":"hash = 3e6d3c8e",
        "hash = 998bc53c":"hash = 4da65048",
        "hash = 00e5703f":"hash = ee867ac2",
        "hash = 2782d638":"hash = e047ea9c",
        "hash = f98c7e7c":"hash = 59b52b44",
        "hash = c02dbf56":"hash = 258c919f",
    },
    "JinhsiSkin": {
        "hash = ef3cbf99":"hash = 420bc474",
        "hash = f08bbd4e":"hash = 83b787db",
        "hash = 1ccb4d01":"hash = 2eb74e79",
        "hash = a12dd42b":"hash = 44a33623",
        "hash = 9d116cf8":"hash = 0cf861f8",
        "hash = 43d2d155":"hash = 301efc44",
        "hash = c864a274":"hash = 913631e7",
        "hash = ffe3eb56":"hash = 3973960b",
        "hash = 7fd16705":"hash = 67787504",
        "hash = 5523c61b":"hash = 11c042bc",
        "hash = d7753a6c":"hash = 94e015b4",
        "hash = 2fa7e169":"hash = 35fc907b",
        "hash = 5a2462f9":"hash = ec8277c1",
    },
    "Jinhsi": {
        "hash = 4296f0e8":"hash = 9d12b710",
        "hash = 14ecacf3":"hash = 188f9150",
        "hash = 27f4ef91":"hash = 95034a03",
        "hash = e51cf6a4":"hash = 81bc8818",
        "hash = 3943dca3":"hash = 7031d19e",
        "hash = e7191b19":"hash = d00f99ad",
        "hash = 911dca0f":"hash = 88aafbc0",
        "hash = 21828bbd":"hash = 5b14639e",
        "hash = 27036b65":"hash = 5b14639e",
        "hash = 64bbdb18":"hash = e51f0115",
        "hash = 70b95d89":"hash = 829180c8",
        "hash = 354569e8":"hash = 439ed7f4",
    },
    "Yinlin": {
        "hash = 1f0f6dc8":"hash = 58b06268",
        "hash = 71525c2a":"hash = 7d1b007a",
        "hash = 76967821":"hash = 9ea4dc96",
        "hash = 3271530d":"hash = 5f0fbdb9",
        "hash = 30053482":"hash = 87bbb0c1",
        "hash = 711af10e":"hash = 55c63039",
        "hash = 8493df3e":"hash = c425fd58",
        "hash = 86b95122":"hash = 00120eee",
        "hash = 750390fa":"hash = 584b7755",
        "hash = 148a83c6":"hash = 33d00a20",
        "hash = 9ebf7cad":"hash = 5065eae3",
        "hash = e56f82b1":"hash = e50849e0",
    },
    "Verina": {
        "hash = 679ad2f5":"hash = 16b54cef",
        "hash = 309b25ba":"hash = edc699f5",
        "hash = fcc47274":"hash = e2a003ed",
        "hash = 03416881":"hash = cb01a05c",
        "hash = ae7043eb":"hash = e2887be0",
        "hash = 24c1883d":"hash = 5e99cc67",
        "hash = 40f3c4ea":"hash = a2d01f96",
        "hash = c0ca0958":"hash = 08be5cdb",
        "hash = dc7f97f7":"hash = 412de025",
        "hash = 953daba7":"hash = 48c627b9",
    },
    "Encore": {
        "hash = c44c3cb9":"hash = f7063e17",
        "hash = 6ff2b9f1":"hash = b6021f06",
        "hash = cd7ec1f3":"hash = e3e1281a",
        "hash = a347d2bc":"hash = 47c515ac",
        "hash = c26d7da2":"hash = 29c8d938",
        "hash = 5395f197":"hash = f1838b66",
        "hash = 34617fc8":"hash = 8def9d8b",
        "hash = beb2b10e":"hash = 9d0fefda",
        "hash = b5222998":"hash = 996b2e4b",
        "hash = e73ee6fb":"hash = 8183786e",
        "hash = 9b440397":"hash = 3d32cb0e",
    },
    "Danjin": {
        "hash = bcf3db0a":"hash = 45a6240e",
        "hash = 5da1a7ae":"hash = 7536f732",
        "hash = 1dd49aa4":"hash = cea68862",
        "hash = f56dbcb4":"hash = 8ae06cff",
        "hash = f6910c93":"hash = 3802a4e4",
        "hash = da15e0f7":"hash = 18a39719",
        "hash = b7758489":"hash = beefbd72",
        "hash = c1f7edcc":"hash = 689e446c",
        "hash = 500d4413":"hash = 659ab32e",
        "hash = b4618a2b":"hash = 11315dc1",
        "hash = 7c720662":"hash = d35da2f0",
        "hash = e2321307":"hash = 65e1499b",
        "hash = 2e599849":"hash = 6969fb89",
        "hash = 63fbfe72":"hash = 99179105",
    },
    "Sanhua": {
        "hash = 48616ac9":"hash = ae6e9014",
        "hash = 345368c9":"hash = 1c0c8b91",
        "hash = 1bdd0987":"hash = 1035197c",
        "hash = 98b9635b":"hash = 68ca7071",
        "hash = 2584190a":"hash = cef6494f",
        "hash = aa70ef15":"hash = 881c236d",
        "hash = 4b6d52b9":"hash = fde0f298",
        "hash = 03d9850b":"hash = e39835c7",
        "hash = ebeeda8c":"hash = abda232b",
        "hash = 0521977a":"hash = efb25eb3",
        "hash = 2c0c2728":"hash = c689a8ee",
        "hash = 16695017":"hash = f3b217ab",
    },
    "SanhuaSkin":{
        "hash = 31a5f36a":"hash = f8d5c991",
        "hash = d153e37f":"hash = 63c807fe",
        "hash = 9522bbc7":"hash = 11171f1c",
        "hash = a0cf932f":"hash = 9febd992",
        "hash = d78ad0f5":"hash = c74af063",
        "hash = f22348f0":"hash = 4478285f",
        "hash = fd078186":"hash = 8e5306a9",
        "hash = d96aa9b8":"hash = 221b8ad6",
        "hash = 464256d1":"hash = c98e83cd",
        "hash = 168462a9":"hash = 52f35e6d",
        "hash = d5a089c8":"hash = 72739d6e",
        "hash = 43dc9bdf":"hash = 1d50aa4a",
    },
    "Pheobe":{
        "hash = 1641ec82":"hash = eeefa6b0",
        "hash = 04c4949f":"hash = cd290e05",
        "hash = 18b491c2":"hash = 06b39fed",
        "hash = 08ee69e1":"hash = 22a9e382",
        "hash = 3e216e73":"hash = 1bc4da29",
        "hash = 3325c6d2":"hash = 38a8ddae",
        "hash = a04d2480":"hash = 620fd27a",
        "hash = 83bc4e8a":"hash = 0758a784",
        "hash = 0da7ba9d":"hash = 76402ba3",
        "hash = 9772a12f":"hash = 989a9b41",
        "hash = 99f06647":"hash = 5198cff7",
        "hash = cbe73490":"hash = 78fa07fc",
        "hash = 2b6e5340":"hash = 18aae516",
        "hash = bace929a":"hash = cb5eca8c",
    },
    "ZaniMenu_Overworld": {
        "hash = 7f15f013":"hash = 5bcca6de",
        "hash = 71f1a895":"hash = 1133b076",
        "hash = a7869af0":"hash = 6df52af4",
        "hash = a6006726":"hash = 2ba75c9c",
        "hash = 988c2332":"hash = ac687edd",
        "hash = ce1aa29a":"hash = 17d03603",
        "hash = 6b885af9":"hash = 85371f27",
        "hash = 69ce5914":"hash = de4463e0",
		"hash = 66ec53c0":"hash = 612a235b",
		"hash = c91bc37a":"hash = 5fe6e3f5",
		"hash = bfaa82b4":"hash = 67316edd",
		"hash = c676996a":"hash = 18a76e47",
		"hash = 73c4cc50":"hash = 726c6138",
		"hash = c91bc37a":"hash = 5fe6e3f5",
		"hash = a6006726":"hash = 2ba75c9c",
        "hash = eb7b28e3":"hash = 8acf0a92",
        "hash = 12b90236":"hash = 07352718",
        "hash = b9f4b0b4":"hash = c2727ed7",
    },
    "ZaniUlt": {
        "hash = c28372b3":"hash = a4a04996",
		"hash = 4fb245db":"hash = a5da61f8",
		"hash = f005294b":"hash = eba837f6",
		"hash = 6118a560":"hash = 15507304",
		"hash = f005294b":"hash = eba837f6",
		"hash = ac0a77cf":"hash = 34fd8ff4",
		"hash = a6006726":"hash = 2ba75c9c",
		"hash = 34774f22":"hash = 3624cd00",
    },
    "Brant": {
        "hash = 79c389b5": "hash = 10cdc735",
        "hash = 93f37a93": "hash = 0f4e6e0a",
        "hash = 41be688c": "hash = ef87053b",
        "hash = 2cf897c6": "hash = 8b117bac",
        "hash = 567e2ab7": "hash = 92036301",
        "hash = 67175ee6": "hash = f69259fd",
        "hash = 8b25adba": "hash = c1f72669",
        "hash = 47c4cf4b": "hash = 33a5aeec",
        "hash = 1830304b": "hash = 9c7aac2e",
        "hash = fc28e018": "hash = b5976b09",
        "hash = 9e2806f0": "hash = 541ea4fd",
    },
    "Jianxin":{
        "hash = 0862e376":"hash = 83744475",
        "hash = 1d823cfb":"hash = 83744475",
        "hash = 5f672bb2":"hash = 6b0f5c7a",
        "hash = 21bc79a7":"hash = af3ba321",
        "hash = 6700cf35":"hash = 55023199",
        "hash = 6c077c81":"hash = ae193e08",
        "hash = 45f7105b":"hash = f524ad06",
        "hash = 534c2615":"hash = 4c0805e1",
        "hash = 3782ab1b":"hash = 837eb0d7",
        "hash = a7275cef":"hash = 55a56862",
        "hash = dab9d56b":"hash = 134a5c16",
        "hash = 09f954e5":"hash = 4701ab34",
        "hash = f095bfbc":"hash = be729d1a",
        "hash = 68c6a3a6":"hash = a42480d2",
    },
    "Lingyang": {
        "hash = 525e8109":"hash = f1282b25",
        "hash = 158837cc":"hash = 6e30ff58",
        "hash = fefe885a":"hash = 84488d7d",
        "hash = 095549b5":"hash = 91bba480",
        "hash = a4e3009b":"hash = 1d9176cc",
        "hash = d01c79e9":"hash = 291b46d1",
        "hash = 4c77312e":"hash = 795b563b",
        "hash = 3a5f46c6":"hash = 3ebe7858",
        "hash = d1d6464e":"hash = 535cb397",
        "hash = b1438a92":"hash = bdf5e2b4",
        "hash = 08f8fbe7":"hash = da541842",
        "hash = e37ba92d":"hash = 65faf13f",
        "hash = a5263392":"hash = 66e7b828",
        "hash = 921bc51f":"hash = eaa6090e",
    },
    "Jiyan": {
        "hash = 46f910cf":"hash = 40346675",
        "hash = 36807a81":"hash = 16662002",
        "hash = cbe41f58":"hash = 05fa5a06",
        "hash = 70727fb3":"hash = 64d51f09",
        "hash = 781bb5d4":"hash = 18c53df4",
        "hash = 9631335c":"hash = 510ae939",
        "hash = 919672df":"hash = 7367d0af",
        "hash = 7741698a":"hash = d8621e79",
        "hash = aedc62a4":"hash = 92e1b9ce",
        "hash = 8bba6141":"hash = deab020e",
    },
    "Xiangli Yao": {
        "hash = 794bf372":"hash = aa467d8c",
        "hash = 59f0cae9":"hash = 65f5a746",
        "hash = d966cc04":"hash = 19190a12",
        "hash = 1ccddcaf":"hash = 312a23b3",
        "hash = a6ddeb73":"hash = 847d7908",
        "hash = 30766750":"hash = d3334af2",
        "hash = 392cfad5":"hash = c5e3d837",
        "hash = 580004ac":"hash = 77fc9adf",
        "hash = ae7af048":"hash = 707ddd83",
        "hash = ab04dbfe":"hash = df7dcbad",
        "hash = 3865a786":"hash = 0f2ce004",
        "hash = 7f1ed7f3":"hash = ccea891f",
        "hash = 7ce42dd7":"hash = fcc7fe3a",
        "hash = 9af1a3b1":"hash = 12f7f3a3",
        "hash = 7291186a":"hash = f0ba2ca2",
        "hash = 2fed1aa0":"hash = dfbe6069",
        "hash = 7c17bb8d":"hash = 548b37ed",
    },
    "Lumi": {
        "hash = 0390820a":"hash = 8e28c8e7",
        "hash = a2c25060":"hash = 27308969",
        "hash = a9b2a415":"hash = 68916487",
        "hash = 4afb92ae":"hash = 801f9d6e",
        "hash = 73dc0ecf":"hash = 33d29aa1",
        "hash = 2decd61b":"hash = d23090a3",
        "hash = dda29ba9":"hash = ac26dd3b",
        "hash = 35c1c5cf":"hash = 43682482",
        "hash = 97e43063":"hash = a614279c",
        "hash = 4dba3f46":"hash = 1e238f6c",
        "hash = 2212362c":"hash = 80fdc4d8",
        "hash = 0249a0f6":"hash = d2ad31db",
    },
    "Taoqi": {
        "hash = 9557c49e":"hash = b5c93936",
        "hash = 4d0c99e4":"hash = 7c47abf0",
        "hash = 3b69e4b4":"hash = a39f43c8",
        "hash = 982bdcc5":"hash = d5ba0088",
        "hash = dec4f75e":"hash = 4e4bbb32",
        "hash = 4ba577c5":"hash = 2c5e38b6",
        "hash = b1372fdd":"hash = b51d4fd4",
        "hash = 33a41964":"hash = 6c4bd3dc",
        "hash = 9b47f413":"hash = 8a1d8b17",
        "hash = b0e248c5":"hash = 16d55d60",
    },
    "Yuanwu": {
        "hash = a59c17cb":"hash = d6b9870f",
        "hash = ce0a295e":"hash = 7b4fd238",
        "hash = 6aa8b697":"hash = 31d64d0d",
        "hash = 389f5e85":"hash = a6c496bb",
        "hash = 14df60bb":"hash = d9a6d77f",
        "hash = c6025664":"hash = 7feb53b2",
        "hash = 2ba57c1b":"hash = 091b887c",
        "hash = de05e406":"hash = 7681bf3d",
        "hash = 8c299dbf":"hash = 7a0e2aa2",
        "hash = 1319b682":"hash = 53e67a3d",
        "hash = 43799dd2":"hash = bda4f564",
    },
    "Baizhi": {
        "hash = 1a09bbb5":"hash = 43ae1deb",
        "hash = 7404e947":"hash = f0f101b3",
        "hash = d755a4a9":"hash = fe4e4afe",
        "hash = 49a71537":"hash = 39b39c99",
        "hash = 7c460f02":"hash = 4e4d79b9",
        "hash = 804d32e9":"hash = 64b13efd",
        "hash = 718456ac":"hash = 0be38d62",
        "hash = 64cc6fa8":"hash = afe67129",
        "hash = 2b7eb01d":"hash = cac210d5",
        "hash = d7756134":"hash = 060f40ba",
        "hash = 91754701":"hash = a2315519",
        "hash = 6f238044":"hash = ff9b6df0",
    },
    "Chixia": {
        "hash = 8f423e37":"hash = 75333d76",
        "hash = eee73787":"hash = ab72381e",
        "hash = 4a2657d7":"hash = a7141c04",
        "hash = 45e0cedb":"hash = 7988637b",
        "hash = ba246036":"hash = 873ca04e",
        "hash = 9497a1b9":"hash = d51104f6",
        "hash = f6fed778":"hash = d51104f6",
        "hash = 489b5f2a":"hash = 94afca13",
        "hash = e29e63d6":"hash = 8080d570",
        "hash = ab057c17":"hash = cb71b417",
        "hash = 9f2544e0":"hash = ebe1f999",
    },
    "YangYang": {
        "hash = 123bcc8e":"hash = fba3de34",
        "hash = 77fe24ce":"hash = d25b9648",
        "hash = f42c4870":"hash = 8e27c9a2",
        "hash = bd8fff82":"hash = c3b2a42e",
        "hash = 1e9a1fb8":"hash = a871413a",
        "hash = 1607589b":"hash = 02e9009d",
        "hash = fc40048f":"hash = 250c59b6",
        "hash = 16f9802d":"hash = ae886086",
        "hash = 92d4ad47":"hash = 49b790e0",
        "hash = cc7a443c":"hash = 29942440",
        "hash = 69c48be0":"hash = 1a9b9391",
        "hash = edf438d9":"hash = 3bd37212",
    },
    "Youhu": {
        "hash = 1012570b":"hash = 5d5ee265",
        "hash = 9b11d340":"hash = bf48c10e",
        "hash = fdeae97b":"hash = bcbd3086",
        "hash = a2cc097f":"hash = a3b840f8",
        "hash = aa28d63e":"hash = 221d712d",
        "hash = 7e251226":"hash = cf0ae3d8",
        "hash = 39ffdf33":"hash = ae2fe6e9",
        "hash = c1078929":"hash = 5e0d738a",
        "hash = a95def0b":"hash = 39696fc7",
        "hash = eb5b96b2":"hash = a0e3c5cb",
        "hash = 450040b2":"hash = 41ced95a",
        "hash = baee6fc5":"hash = bfd993d3",
        "hash = 0eb7da46":"hash = 2d7bb11f",
        "hash = 8b1913b4":"hash = 1079fd6f",
        "hash = dd54d712":"hash = 37dcbf53",
    },
    "Calcharo": {
        "hash = c235c6a7":"hash = 21f813ba",
        "hash = 5019e88f":"hash = f47bc395",
        "hash = 3cd03f60":"hash = 1dcc0f1d",
        "hash = 8b43ad38":"hash = f3e04a65",
        "hash = 52197a16":"hash = 1ae38ad2",
        "hash = 8a7d6de5":"hash = 3e77c6f1",
        "hash = 7e87c77a":"hash = d4a87b42",
        "hash = de0af803":"hash = 5687b335",
        "hash = 0485b505":"hash = 88fc89dd",
        "hash = 3320efad":"hash = b578f66a",
        "hash = 96cdca80":"hash = 790dc54b",
        "hash = e8d882a0":"hash = 0465ef39",
        "hash = feff1922":"hash = 71756a01",
        "hash = f657b0b8":"hash = d482f64e",
        "hash = 006cda67":"hash = 006cda67",
        "hash = cb23f0b5":"hash = 31f8578b",
        "hash = f657b0b8":"hash = d482f64e",
    },
    "Aalto": {
        "hash = 93bbbdc0":"hash = 93bbbdc0",
        "hash = 4f0a1fba":"hash = 4f0a1fba",
        "hash = 3edd37c6":"hash = 4eba0ca3",
        "hash = 41d712e3":"hash = 3dcf2a5e",
        "hash = 83220aa9":"hash = 9f6b993d",
        "hash = 78616c21":"hash = 7f4b67b2",
        "hash = b94cc7e1":"hash = b06caa8d",
        "hash = 03265d9c":"hash = 184f22fd",
        "hash = e02df19b":"hash = 98a883e4",
    },
    "Mortefi": {
        "hash = 11b18904":"hash = 2a5da812",
        "hash = 92474c68":"hash = 6a56519c",
        "hash = 6d76b1cc":"hash = 0f14dc92",
        "hash = 7eee35f8":"hash = 6e183bd5",
        "hash = 27c4d37a":"hash = 3f6dc5cc",
        "hash = bedffbf4":"hash = 794917a4",
        "hash = 18fb0f57":"hash = 1d2ca7a8",
        "hash = 97ef5c1a":"hash = 800ac367",
        "hash = 413c2f2e":"hash = 39144df1",
        "hash = 62949a6c":"hash = b8690bc1",
        "hash = 5e6a779f":"hash = b775a156",
        "hash = f81811a7":"hash = fbf9f66a",
        "hash = be6d8bde":"hash = 539b81a3",
    },
    "Wings": {
        "hash = 99977887":"hash = 4082c8ea",
        "hash = 7233337e":"hash = ff615a59",
    },
    "Glider": {
        "hash = e0b526b0":"hash = 8c2f4684",
    },
}

hash_maps = HashMap(old_vs_new)

def log_message(log, message):
    log.append(message)
    print(message)

def create_backup(file_path):
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)
    return backup_path

def collect_ini_files(folder_path: str) -> List[str]:
    """ Collect .ini files only from the script's location and subfolders (ignore upper folders) """
    ini_files = []
    script_folder = os.path.abspath(folder_path)  # Get script's absolute path

    for root, _, files in os.walk(script_folder):  # Scan current folder and subfolders
        for file in files:
            if file.lower().endswith('.ini'):
                ini_files.append(os.path.join(root, file))

    return ini_files

def apply_hash_fix(folder_path):
    log = []
    ini_files = collect_ini_files(folder_path)

    if not ini_files:
        log_message(log, "No .ini files found.")
        return log, 0, 0

    modified_files = 0

    for file_path in ini_files:
        try:
            log_message(log, f"Processing: {file_path}")

            # Force UTF-8 with error handling
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            modified = False

            for character, mappings in hash_maps.old_vs_new.items():
                for old_hash, new_hash in mappings.items():
                    if old_hash in content:
                        content = content.replace(old_hash, new_hash)
                        modified = True
                        log_message(log, f"[{character}] Replaced Text - {old_hash} → {new_hash}")

            if modified:
                create_backup(file_path)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                modified_files += 1
                log_message(log, f"Updated: {file_path}")
            else:
                log_message(log, "No changes needed.")

        except Exception as e:
            log_message(log, f"Error processing {file_path}: {str(e)}")

    return log, modified_files, len(ini_files)

if __name__ == '__main__':
    folder_path = os.path.abspath(os.getcwd())  # Get current folder (script location)
    start_time = time.time()

    log, modified_files, total_files = apply_hash_fix(folder_path)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nProcessing took {elapsed_time:.2f} seconds")
    print(f"Total files found: {total_files}")
    print(f"Processed {modified_files} files")

    print("Mods have been fixed")
    input("Press F10 to reload")
