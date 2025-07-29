#!/usr/bin/env python3
import ssl, urllib.request, urllib.parse, json, time, sys, os, glob, select, re
import http.cookiejar, urllib.error
import datetime

from typing import List, Optional

ssl._create_default_https_context = ssl._create_unverified_context

CANCEL_CMD = "0"
MILITARY_CODES = {"1":"국방부","2":"국직","5":"육군","6":"해군","7":"공군","D":"해병대"}
URLS = {
    "login":      "https://www.dtis.mil.kr/m/login.ajax",
    "main_page":  "https://www.dtis.mil.kr/m/mcp/rmndrSeatAplMain.page",
    "user_info":  "https://www.dtis.mil.kr/m/mcp/selectUserInfo.ajax",
    "train_info": "https://www.dtis.mil.kr/m/mcp/selectMilChrtrPsgcarBdngAplCtlg.ajax",
    "route":      "https://www.dtis.mil.kr/m/mcp/selectMilChrtrPsgcarRuteCtlg.ajax",
    "check":      "https://www.dtis.mil.kr/m/mcp/selectMilChrtrPsgcarRmndrSeatRsvtnCtlg.ajax",
    "book":       "https://www.dtis.mil.kr/m/mcp/saveMilChrtrPsgcarRmndrSeatRsvtnApl.ajax",
    "reservations": "https://www.dtis.mil.kr/m/mcp/selectMilChrtrPsgcarPrstsCtlg.ajax",
    "cancel": "https://www.dtis.mil.kr/m/mcp/saveMilChrtrPsgcarAlctCncl.ajax",
}
POLL_INTERVAL = 0.5

COOKIE_FILE_TEMPLATE = os.path.expanduser("~/.ticket_bot_cookies_{login}.txt")

# — 데이터 구조 —
class Session:
    def __init__(self, login_id:str=""):
        self.login_id = login_id
        self.opener = None
        self.user_id = ""
        self.srvno = ""
        self.mdcd = ""
        self.mgtno = 0

def make_opener(cookie_path:Optional[str]) -> urllib.request.OpenerDirector:
    jar = http.cookiejar.LWPCookieJar(cookie_path) if cookie_path else http.cookiejar.CookieJar()
    if cookie_path and os.path.exists(cookie_path):
        jar.load(cookie_path, ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPHandler()
    )
    opener.cookiejar = jar
    return opener

def http_post_form(opener, url:str, data:dict) -> dict:
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Content-Type":"application/x-www-form-urlencoded"}
    )
    resp = opener.open(req)
    return json.loads(resp.read().decode())

def http_post_json(opener, url:str, data:dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type":"application/json","X-Requested-With":"XMLHttpRequest"}
    )
    resp = opener.open(req)
    return json.loads(resp.read().decode())

def perform_login(session:Session, pwd:str, cookie_file:str):
    payload = {"LOGIN_ID":session.login_id,"PASSWORD":pwd,"MODE":4,"TYPE":0,"DataSetRowType":0,"MENU":"RAIL"}
    j = http_post_json(session.opener, URLS["login"], payload)
    if j.get("errCode",0) < 0:
        print("⚠️ 로그인 실패:", j.get("errMsg"))
        sys.exit(1)
    # 세션쿠키 저장
    session.opener.cookiejar.save(cookie_file, ignore_discard=True, ignore_expires=True)

def extract_main_vars(session:Session):
    html = session.opener.open(URLS["main_page"]).read().decode('euc-kr','ignore')
    user_id_match = re.search(r"var\s+USER_ID\s*=\s*'([^']+)'", html)
    srvno_match = re.search(r"var\s+srvno\s*=\s*'([^']+)'", html)
    mdcd_match = re.search(r"var\s+mdcd\s*=\s*'([^']+)'", html)
    if not user_id_match or not srvno_match or not mdcd_match:
        print("⚠️ 세션 만료 또는 메인 페이지 로딩 실패, 다시 로그인해주세요.")
        return False
    session.user_id = user_id_match.group(1)
    session.srvno   = srvno_match.group(1)
    session.mdcd    = mdcd_match.group(1)
    return True

def fetch_user_info(session:Session):
    data = {"USER_ID":session.user_id,"DataSetRowType":0,"ECHDAY_MVMT_MGTNO":session.mgtno}
    j = http_post_form(session.opener, URLS["user_info"], data)
    res = j.get("result",[])
    if res:
        return
    print("⚠️ 사용자 정보 조회 실패")

def fetch_trains(session:Session, date:str) -> List[dict]:
    data = {"BDNG_FROM_DATE":date,"BDNG_TO_DATE":date,"USER_ID":session.user_id,
            "SRVNO":session.srvno,"MDCD":session.mdcd,"TRN_NM_CD":"","DataSetRowType":0}
    return http_post_form(session.opener, URLS["train_info"], data).get("result",[])

def fetch_route_stations(session:Session, date:str, mgtno:int) -> List[str]:
    data = {"BDNG_FROM_DATE":date,"BDNG_TO_DATE":date,"ECHDAY_MVMT_MGTNO":mgtno,"DataSetRowType":0}
    items = http_post_form(session.opener, URLS["route"], data).get("result",[])
    return sorted({i["DETLS_CD_NM"].strip() for i in items})

def check_seats(session:Session) -> List[dict]:
    data = {"DataSetRowType":0,"ECHDAY_MVMT_MGTNO":session.mgtno}
    return http_post_form(session.opener, URLS["check"], data).get("result",[])

def book_seat(session:Session, seat:dict):
    payload = {"dsListSaveRow":[{
        "DataSetRowType":0,
        "SEATNO_NMBR":seat["SEATNO_NMBR"],
        "SRVNO":session.srvno,
        "RMNDR_SEAT_ALCT_NUMTM":1,
        "SEAT_NM":seat["SEAT_NM"],
        "SSITECD":seat["SSITECD"],"SSITENAM":seat["SSITENAM"],
        "ESITECD":seat["ESITECD"],"ESITENAM":seat["ESITENAM"],
        "ECHDAY_MVMT_MGTNO":seat["ECHDAY_MVMT_MGTNO"],
        "TRNCNO_CD":seat["TRNCNO_CD"],"RUTE_NM_CD":seat["RUTE_NM_CD"],
        "PSGR_SRVNO":session.srvno,"TRN_NM":seat["TRN_NM"],
        "TRN_NM_CD":seat["TRN_NM_CD"],"MVMT_DATE":seat["MVMT_DATE"],
        "TRNCNO_NMBR":seat["TRNCNO_NMBR"],"TRN_KND_CD":seat["TRN_KND_CD"],
        "MDCD":session.mdcd,"USER_ID":session.user_id
    }],"dsSTATNLIST":[]}
    try:
        res = http_post_json(session.opener, URLS["book"], payload)
        return res
    except urllib.error.HTTPError as e:
        print("\n⚠️ 예약 신청 서버 오류:", e)
        sys.exit(1)

# 예약 내역 조회
def fetch_reservations(session:Session) -> List[dict]:
    # retrieve current reservations within the next 7 days
    today = datetime.date.today()
    from_date = today.strftime("%Y%m%d")
    to_date = (today + datetime.timedelta(days=7)).strftime("%Y%m%d")
    data = {
        "USER_ID": session.user_id,
        "SRVNO": session.srvno,
        "MDCD": session.mdcd,
        "BDNG_FROM_DATE": from_date,
        "BDNG_TO_DATE": to_date,
        "DataSetRowType": 0
    }
    return http_post_form(session.opener, URLS["reservations"], data).get("result", [])

# 예약 취소
def cancel_reservation(session: Session, res: dict):
    try:
        result = http_post_form(session.opener, URLS["cancel"], res)
        if isinstance(result, dict):
            return {"success": True, **result}
        else:
            return {"success": True, "result": result}
    except urllib.error.HTTPError as e:
        print("\n⚠️ 예약 취소 서버 오류:", e)
        return {"success": False, "error": str(e)}

# — UI 헬퍼들 —
def choose(prompt:str, opts:List[str], allow_cancel=True) -> Optional[int]:
    print(f"\n{prompt}")
    if allow_cancel: print("0: 취소")
    for i,o in enumerate(opts,1):
        print(f"{i}: {o}")
    while True:
        s = input("선택 ▶ ").strip()
        if allow_cancel and s==CANCEL_CMD: return None
        if s.isdigit() and 1<=int(s)<=len(opts):
            return int(s)-1

def input_date() -> Optional[str]:
    s = input("조회할 날짜를 입력해주세요 (YYYYMMDD) / 취소(0) ▶ ").strip()
    return None if s==CANCEL_CMD else s

# — 분리된 로직 —
def reservation_flow(session:Session):
    date = input_date()
    if not date: return
    trains = fetch_trains(session, date)
    if not trains:
        print("열차 없음")
        return
    idx = choose(
        "조회된 열차 목록입니다. 원하는 열차 번호를 입력해주세요.",
        [
            f"{t['TRN_NM']} | {t.get('SSITENM','')}({t.get('STIME','')}) → {t.get('ESITENM','')}({t.get('ETIME','')})"
            for t in trains
        ]
    )
    if idx is None: return
    session.mgtno = trains[idx]["ECHDAY_MVMT_MGTNO"]

    stations = fetch_route_stations(session, date, session.mgtno)
    di = choose("승차역 목록입니다. 원하는 승차역 번호를 입력해주세요.", stations)
    if di is None: return
    ai = choose("하차역 목록입니다. 원하는 하차역 번호를 입력해주세요.", stations)
    if ai is None: return
    depart, arrive = stations[di], stations[ai]

    start = time.time()
    while True:
        elapsed = time.time() - start
        all_seats = check_seats(session)
        sys.stdout.write(
            f"\r{depart} → {arrive} ⏱ {elapsed:.3f}s 경과… (취소=0)"
        )
        sys.stdout.flush()
        seats = [s for s in all_seats
                 if depart in s["SSITENAM"] and arrive in s["ESITENAM"] and s["MVMT_DATE"]==date]
        if seats:
            print("\n예약 시도…")
            r = book_seat(session, seats[0])
            print("\n✅ 예약이 완료되었습니다!" if not r.get("rmrk") else f"⚠️ {r['rmrk']}")
            break
        rlist,_,_ = select.select([sys.stdin],[],[],POLL_INTERVAL)
        if rlist and sys.stdin.readline().strip()==CANCEL_CMD:
            print("\n취소")
            break

def scheduled_reservation_flow(session:Session):
    date = input_date()
    if not date:
        return
    trains = fetch_trains(session, date)
    if not trains:
        print("열차 없음")
        return
    idx = choose(
        "조회된 열차 목록입니다. 원하는 열차 번호를 입력해주세요.",
        [
            f"{t['TRN_NM']} | {t.get('SSITENM','')}({t.get('STIME','')}) → {t.get('ESITENM','')}({t.get('ETIME','')})"
            for t in trains
        ]
    )
    if idx is None: return
    session.mgtno = trains[idx]["ECHDAY_MVMT_MGTNO"]

    stations = fetch_route_stations(session, date, session.mgtno)
    di = choose("승차역 목록입니다. 원하는 승차역 번호를 입력해주세요.", stations)
    if di is None: return
    ai = choose("하차역 목록입니다. 원하는 하차역 번호를 입력해주세요.", stations)
    if ai is None: return
    depart, arrive = stations[di], stations[ai]

    # 예약 시작 시간 입력 (현재 시각을 한 번만 표시)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    target_time_str = input(
        f"현재 시각: {now}\n"
        "예약 시작 시간을 입력해주세요 (HHMMSS) ▶ "
    ).strip()
    if not target_time_str.isdigit() or len(target_time_str) != 6:
        print("\n잘못된 시간 형식입니다.")
        return

    now = datetime.datetime.now()
    target_time = datetime.datetime(now.year, now.month, now.day,
                                    int(target_time_str[0:2]),
                                    int(target_time_str[2:4]),
                                    int(target_time_str[4:6]))
    if now < target_time:
        wait_seconds = int((target_time - now).total_seconds())
        for remaining in range(wait_seconds, 0, -1):
            sys.stdout.write(f"\r예약 시작까지 {remaining}초 대기 중…")
            sys.stdout.flush()
            time.sleep(1)
        print()  # 새 줄

    start = time.time()
    while True:
        elapsed = time.time() - start
        all_seats = check_seats(session)
        sys.stdout.write(
            f"\r{depart} → {arrive} ⏱ {elapsed:.3f}s 경과… (취소=0)"
        )
        sys.stdout.flush()
        seats = [s for s in all_seats
                 if depart in s["SSITENAM"] and arrive in s["ESITENAM"] and s["MVMT_DATE"]==date]
        if seats:
            print("\n예약 시도…")
            r = book_seat(session, seats[0])
            print("\n✅ 예약이 완료되었습니다!" if not r.get("rmrk") else f"⚠️ {r['rmrk']}")
            break
        rlist,_,_ = select.select([sys.stdin],[],[],POLL_INTERVAL)
        if rlist and sys.stdin.readline().strip()==CANCEL_CMD:
            print("\n취소")
            break

def seat_check_flow(session: Session):
    date = input_date()
    if not date: return
    trains = fetch_trains(session, date)
    if not trains:
        print("열차 없음")
        return
    idx = choose(
        "조회된 열차 목록입니다. 원하는 열차 번호를 입력해주세요.",
        [
            f"{t['TRN_NM']} | {t.get('SSITENM','')}({t.get('STIME','')}) → {t.get('ESITENM','')}({t.get('ETIME','')})"
            for t in trains
        ]
    )
    if idx is None: return
    session.mgtno = trains[idx]["ECHDAY_MVMT_MGTNO"]
    seats = [s for s in check_seats(session)
             if s["ECHDAY_MVMT_MGTNO"] == session.mgtno and s["MVMT_DATE"] == date]
    if seats:
        print("\n=== 현재 잔여석 목록 ===")
        for i, s in enumerate(seats,1):
            print(f"{i}. 호차{s['TRNCNO_NMBR']} {s['SEAT_NM']} | {s['SSITENAM']} → {s['ESITENAM']}")
    else:
        print("잔여석이 없습니다.")

def main_menu(session:Session):
    while True:
        print("\n=== 메인 메뉴 ===")
        print("1. 예약 시작")
        print("2. 잔여석 요이똥")
        print("3. 잔여석 확인")
        print("4. 예약 확인/취소")
        print("5. 로그아웃")
        print("6. 종료")
        c = input("선택 ▶ ").strip()
        if c=="1":
            reservation_flow(session)
        elif c=="2":
            scheduled_reservation_flow(session)
        elif c=="3":
            seat_check_flow(session)
        elif c=="4":
            # list and cancel
            res_list = fetch_reservations(session)
            if not res_list:
                print("예약 내역이 없습니다.")
            else:
                print("\n=== 예약 내역 ===")
                for i,r in enumerate(res_list,1):
                    print(f"{i}. {r.get('TRN_NM','')} | {r.get('SSITENAM')}→{r.get('ESITENAM')} on {r.get('MVMT_DATE')}")
                idx = choose("취소할 예약 번호를 입력하세요.", [ f"{r.get('TRN_NM')}" for r in res_list ])
                if idx is not None:
                    resp = cancel_reservation(session, res_list[idx])
                    print("✅ 취소 완료!" if resp.get("success") else f"⚠️ 취소 실패: {resp}")
        elif c=="5":
            os.remove(session.cookie_file)
            print("로그아웃됨")
            return  # exit menu to restart at login
        elif c=="6":
            sys.exit(0)

# — 진입점 —
def main():
    while True:
        # 쿠키파일 탐색
        matches = glob.glob(COOKIE_FILE_TEMPLATE.format(login="*"))
        if matches:
            latest = max(matches, key=os.path.getmtime)
            login_id = os.path.basename(latest).split("_",1)[1].rsplit(".",1)[0]
            session = Session(login_id)
            session.cookie_file = latest
            session.opener = make_opener(latest)
            print(f"세션 로드: {login_id}")
            if not extract_main_vars(session):
                os.remove(latest)
                continue  # go back to login screen
        else:
            # 로그인
            print("=== 로그인 ===")
            for k,v in MILITARY_CODES.items():
                print(f"{k}:{v}")

            mil = input("군구분을 선택해주세요 ▶ ").strip()
            uid = input("아이디를 입력해주세요 ▶ ").strip()
            pwd = input("비밀번호를 입력해주세요 ▶ ").strip()

            login_id = f"{mil}{uid}"
            cf = COOKIE_FILE_TEMPLATE.format(login=login_id)
            session = Session(login_id)
            session.cookie_file = cf
            session.opener = make_opener(cf)
            perform_login(session, pwd, cf)
            if not extract_main_vars(session):
                continue  # go back to login screen

        fetch_user_info(session)

        main_menu(session)

main()
