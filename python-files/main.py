# import standard libraries
from subprocess import run, DEVNULL
from json import dumps as json_string
from typing import Any
from math import ceil
from urllib.parse import urlparse as url_parse
from socket import error as socket_exception, gethostbyname as host_resolve
from re import search
from time import sleep, time
from msvcrt import getwch as getch, getwche as getche
from os.path import isfile, exists, splitext as split_extension
from base64 import b64encode as base64_encode

# this is to ensure the requirements are installed before importing
run(["pip", "install", "-r", "requirements.txt"], stdout=DEVNULL, stderr=DEVNULL)

# import downloaded libraries
from requests import get, post, patch, delete, Response
from requests.structures import CaseInsensitiveDict
from requests.exceptions import RequestException as request_exception
from validators import url as url_iscorrect
from console import fg
from console.detection import get_size, get_title
from console.utils import strip_ansi, make_line, set_title
from tqdm import tqdm


# struct for url status, 'bool' represents the url validity, the 'int' represents the status code
class URLStatus(tuple[bool, int | None]):
    def __new__(cls, is_valid: bool, status_code: int | None):
        if not isinstance(is_valid, bool):
            raise TypeError("expected bool value for 'is_valid' parameter.")
        if not isinstance(status_code, int) and status_code is not None:
            raise TypeError("expected either int value or None for 'status_code' parameter.")

        return super().__new__(cls, (is_valid, status_code))

    def is_valid(self) -> bool:
        return self[0]

    def status_code(self) -> int | None:
        return self[1]


# this defines constants used throughout the program
class Constants:
    base_url: str = "https://canary.discord.com/api/v10/webhooks/{id}/{token}"

    github_url: str = "https://github.com/ikyynites/webhookSpam"
    github_api_url: str = "https://api.github.com/repos/ikyynites/webhookSpam"

    headers: CaseInsensitiveDict = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    discord_api_status_codes: dict[str, int] = {
        "ratelimit": 429
    }


# this defines some colours used throughout the program
class Colours:
    gray = fg.lightblack
    yellow = fg.lightyellow
    blue = fg.lightblue
    green = fg.lightgreen
    red = fg.lightred


# this defines any text printed throughout the program in one central place
class Text:
    # these texts are private and only used in public texts
    __input_bool: str = Colours.green("[y]") + "/" + Colours.red("[n]") + Colours.yellow(": ")

    # these texts are not centered, colour handled here
    input_url: str = Colours.yellow("enter webhook url: ")
    input_payload: str = Colours.yellow("enter payload type: ") + Colours.blue("[_]") + "\b\b" + Colours.blue
    input_content_message: str = Colours.yellow("enter message: ")
    input_content_amount: str = Colours.yellow("enter amount of messages: ")
    input_tts: str = Colours.yellow("enable text-to-speech on messages? ") + __input_bool + Colours.gray("[_]") + "\b\b"

    url_invalid: str = Colours.gray("url is invalid.")
    url_invalid_error: str = Colours.gray("an unexpected error has occurred, and the url has become invalid.")
    payload_invalid: str = Colours.gray("payload type [{}] is invalid.")
    tts_invalid: str = Colours.gray("tts value [{}] is invalid.")

    payload_options_title: str = Colours.gray("payload types:")
    payload_options: list[str] = [Colours.blue("[0]") + " message spam",
                                  Colours.blue("[1]") + " edit username and avatar",
                                  Colours.blue("[2]") + " delete webhook"]

    program_title: str = "webhook spam"
    restart: str = Colours.gray("press any key to restart (esc to exit)... ")

    ratelimit_reached: str = Colours.gray("ratelimit was reached. retrying in {}")

    # these texts are centered, and need special colour handling. raw strings only
    project_title: str = "webhookSpam"
    project_author: str = "by ikyynites#3610"
    project_description: str = "for punishing scammers who use webhooks to relay your private information back to " \
                               "them on discord."

    # update project info from github, or used predefined values
    try:
        github_api_response = get(Constants.github_api_url).json()
        project_title = github_api_response.get("name")
        project_description = github_api_response.get("description")
    except request_exception:
        pass


# this is a wrapper for the 'requests' library, to validate urls before trying to access, handle dicts better, etc.
class Requests:
    @staticmethod
    def validate_url(validation_url: str) -> URLStatus:
        if not url_iscorrect(validation_url):
            return URLStatus(False, None)

        try:
            is_correct: bool = url_iscorrect(validation_url)
            is_resolvable: bool = bool(host_resolve(url_parse(validation_url).hostname))
            status_code: int = get(validation_url).status_code
            is_okay: bool = status_code == 200

            return URLStatus(all([is_correct, is_resolvable, is_okay]), status_code)
        except (request_exception, socket_exception):
            return URLStatus(False, None)

    @staticmethod
    def get(get_url: str) -> Response | URLStatus:
        if not (valid := Requests.validate_url(get_url))[0]:
            return URLStatus(valid[0], valid[1])

        get_response: Response = get(get_url)
        return get_response

    @staticmethod
    def delete(delete_url: str) -> Response | URLStatus:
        if not (valid := Requests.validate_url(delete_url))[0]:
            return URLStatus(valid[0], valid[1])

        delete_response: Response = delete(delete_url)
        return delete_response

    @staticmethod
    def post(post_url: str, post_payload: dict[str, str | bool | list[Any] | None] = None,
             post_params: dict[str, str] = None) -> Response | URLStatus:
        if not (valid := Requests.validate_url(post_url))[0]:
            return URLStatus(valid[0], valid[1])

        if post_payload is None or post_payload == {}:
            post_payload = {}
            content_length: int = 0
        else:
            content_length: int = len(str(post_payload))

        if post_params is not None or post_params != {}:
            for key in post_params:
                value = post_params.get(key)
                if "?" not in post_url.split("/")[-1]:
                    post_url += "?"
                else:
                    post_url += "&"
                post_url += f"{key}={value}"

        post_headers: CaseInsensitiveDict = Constants.headers
        post_headers["Content-Length"] = str(content_length)

        post_response: Response = post(url=post_url, data=json_string(post_payload),
                                       headers=post_headers)
        return post_response

    @staticmethod
    def patch(patch_url: str, patch_payload: dict[str, str | bool | list[Any] | None] = None,
              patch_params: dict[str, str] = None) -> Response | URLStatus:
        if not (valid := Requests.validate_url(patch_url))[0]:
            return URLStatus(valid[0], valid[1])

        if patch_payload is None or patch_payload == {}:
            patch_payload = {}
            content_length: int = 0
        else:
            content_length: int = len(str(patch_payload))

        if patch_params is not None or patch_params != {}:
            for key in patch_params:
                value = patch_params.get(key)
                if "?" not in patch_url.split("/")[-1]:
                    patch_url += "?"
                else:
                    patch_url += "&"
                patch_url += f"{key}={value}"

        patch_headers: CaseInsensitiveDict = Constants.headers
        patch_headers["Content-Length"] = str(content_length)

        patch_response: Response = patch(url=patch_url, data=json_string(patch_payload),
                                         headers=patch_headers)
        return patch_response


# this defines functions for generating payloads to use for the discord webhook api
class Payloads:
    @staticmethod
    def message(content: str, tts: bool) -> dict[str, str | bool]:
        return {"content": content, "tts": tts}

    @staticmethod
    def edit_webhook(new_user: str | None = None, new_avatar_path: str | None = None) -> dict[str, str]:
        payload: dict[str, str] = {}

        if new_user is not None and new_user != "":
            payload["name"] = new_user
        if new_avatar_path is not None and new_avatar_path != "":
            jpeg: list[str] = [".jpg", ".jpeg", ".jfif"]

            path_isvalid: bool = all((exists(new_avatar_path), isfile(new_avatar_path),
                                      (raw_ext := split_extension(new_avatar_path)[1]) in [*jpeg, ".png", ".webp"]))

            if path_isvalid:
                ext: str = "jpeg" if raw_ext in jpeg else "png" if raw_ext == ".png" else "webp"

                with open(new_avatar_path, "rb") as path_filestream:
                    data: str = base64_encode(path_filestream.read()).decode("utf-8")

                payload["avatar"] = f"data:image/{ext};base64,{data}"

        return payload


# this defines helpful utility functions used throughout the program
class Utils:
    @staticmethod
    def center(*values, sep=" ") -> str:
        value: str = sep.join(values)
        string_centered: str = strip_ansi(make_line(string=value, width=len(value), center=True))

        return string_centered

    @staticmethod
    def make_line(distance_from_edge: int = 1, _fallback=80):
        width = get_size((_fallback, 0)).columns - (distance_from_edge * 2)
        return Colours.gray(strip_ansi(make_line(width=width, center=True)))

    @staticmethod
    def header() -> None:
        print("\n" + Colours.yellow(Utils.center(Text.project_title)))
        print(Colours.gray(Utils.center(Text.project_author)))

        print("\n" + Utils.center(Text.project_description))

        print("\n" + Utils.make_line(2) + "\n")

    @staticmethod
    def string_to_bool(string: str, default_value: bool = False) -> bool:
        if string.lower() in ["yes", "y"]:
            return True
        elif string.lower() in ["no", "n"]:
            return False
        return default_value


# define main function
def main():
    url_input: str = str(input(Text.input_url)).strip()
    url_isvalid: URLStatus = Requests.validate_url(url_input)

    while not url_isvalid.is_valid():
        print(Text.url_invalid + "\n")
        url_input: str = str(input(Text.input_url)).strip()
        url_isvalid = Requests.validate_url(url_input)

    url_id: str = search("[0-9]{19}", url_input).group()
    url_token: str = search("[a-zA-z0-9_-]{68}", url_input).group()

    url: str = Constants.base_url.format(id=url_id, token=url_token)

    print("\n" + Text.payload_options_title)
    for payload_option in Text.payload_options:
        print(" " + payload_option)

    payload_type: Any = -1
    while payload_type not in range(len(Text.payload_options)):
        print("\n" + Text.input_payload, end="", flush=True)
        payload_type: Any = getche()
        print(fg.default)

        temp_payload_type: str = str(payload_type)

        try:
            payload_type = int(payload_type)
        except ValueError:
            payload_type = -1

        if payload_type not in range(len(Text.payload_options)):
            print(Text.payload_invalid.format(temp_payload_type), end="\x1b[F" * 2, flush=True)
    print("\x1b[2K", end="", flush=True)

    match payload_type:
        case 0:
            content: str = str(input("\n" + Text.input_content_message))
            content_amount: int = int(input(Text.input_content_amount))

            if content_amount <= 0:
                print("'content_amount' cannot be less than or equal to 0, setting 'content_amount' to 1")
                content_amount = 1

            tts: Any = ""
            while tts not in [True, False]:
                print("\n" + Text.input_tts, end="", flush=True)
                tts: Any = getche()
                temp_tts: str = str(tts)

                if tts == "y":
                    print("\b\b" + Colours.green("[y]"))
                    tts = True
                elif tts == "n":
                    print("\b\b" + Colours.red("[n]"))
                    tts = False
                else:
                    print(fg.default)

                if tts not in [True, False]:
                    print(Text.tts_invalid.format(temp_tts), end="\x1b[F" * 2, flush=True)
            print("\x1b[2K", end="", flush=True)

            print()
            rate_limits: int = 0
            for _ in tqdm(range(content_amount), ascii=True, desc="messages", bar_format=Colours.yellow("{desc}: ")
                          + Colours.gray("{n_fmt}/{total_fmt} ({percentage:3.0f}%)") + " [{bar}] "
                          + Colours.gray("({elapsed})")):
                post_response = Requests.post(url, Payloads.message(content, tts), {"wait": "true"})
                if isinstance(post_response, Response):
                    if post_response.status_code == Constants.discord_api_status_codes.get("ratelimit"):
                        print()
                        rate_limits += 1
                        retry_after: int = (ceil(float(post_response.json().get("retry_after"))) + 1) * rate_limits
                        for i in range(retry_after, 0, -1):
                            start: float = time()
                            i_seconds: int = i % 60
                            i_minutes: int = i // 60
                            retry_after_timestamp = f"{i_minutes:02}:{i_seconds:02}"
                            print(Text.ratelimit_reached.format(retry_after_timestamp), end="\r", flush=True)
                            elapsed: float = time() - start
                            sleep(max(1 - elapsed, 0))
                        print("\x1b[2K\x1b[F", end="", flush=True)

                        Requests.post(url, Payloads.message(content, tts), {"wait": "true"})
                else:
                    print()
                    print(Text.url_invalid_error)
                    return


# execute main function
if __name__ == "__main__":
    old_title = get_title()
    set_title(Text.program_title)

    Utils.header()
    while True:
        main()

        print("\n" + Text.restart, end="", flush=True)
        if getch() == "\x1b":
            print("\n\n" + Utils.make_line(2) + "\n")
            break

        print("\n\n" + Utils.make_line(10) + "\n")

    set_title(old_title)
