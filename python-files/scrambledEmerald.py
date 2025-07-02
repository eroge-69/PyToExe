from os import remove, listdir, walk, chmod
from os.path import join
from requests import get
from shutil import move, rmtree
from subprocess import run, DEVNULL
from zipfile import ZipFile

urls = {
    "base": "https://myrient.erista.me/files/No-Intro/Nintendo%20-%20Game%20Boy%20Advance/Pokemon%20-%20Emerald%20Version%20(USA,%20Europe).zip",
    "patch": "https://github.com/Strackeror/scrambled-emerald/releases/latest/download/pokeemerald.ups",
    "flips": "https://github.com/Alcaro/Flips/releases/latest/download/flips-linux.zip"
}


def download(url, filename):
    with get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)


def extract(zipfile_name, target):
    with ZipFile(zipfile_name) as z:
        z.extractall(target)


def get_patch_version():
    api_url = "https://api.github.com/repos/Strackeror/scrambled-emerald/releases/latest"
    response = get(api_url)
    response.raise_for_status()
    data = response.json()
    return data["tag_name"]


def main():
    download(urls["base"], "base.zip")
    extract("base.zip", "extracted")
    remove("base.zip")

    gba = next(f for f in listdir("extracted") if f.endswith(".gba"))
    gba = join("extracted", gba)

    download(urls["patch"], "patch.ups")

    download(urls["flips"], "flips.zip")
    extract("flips.zip", "flips_tmp")

    for root, _, files in walk("flips_tmp"):
        if "flips" in files:
            move(join(root, "flips"), "flips")
            chmod("flips", 0o755)
            break

    remove("flips.zip")
    rmtree("flips_tmp")

    version = get_patch_version()

    run(["./flips", "--apply", "patch.ups", gba, f"Scrambled_Emerald_{version}.gba"],
        stdout=DEVNULL, stderr=DEVNULL)
    remove("patch.ups")
    rmtree("extracted")
    remove("flips")


if __name__ == "__main__":
    main()
