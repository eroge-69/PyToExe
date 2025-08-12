# Define all licence keys
licence_keys = [
    "b5i37-3yg8d-28t3j-59hs2-0dv28",  # LicenceKey1
    "u2y38-2gj47-3ii86-3hj72-nbf38",  # LicenceKey2
    "3qZlW-a5BH8-Vfso8-rbus1-cu2n2",  # LicenceKey3
    "1jcMp-SMT2D-x8Avy-9qRAT-p18oD",  # LicenceKey4
    "Zp467-kec1T-e3ywO-sYo6s-U9sVF",  # LicenceKey5
    "09Nbp-JFT8Z-D1HIA-mnyWv-3DTwr",  # LicenceKey6
    "6d2eC-fBmfL-PcShy-QDpsm-KHfng",  # LicenceKey7
    "QWd6D-wOnYo-kolWs-u5oxW-Uzic0",  # LicenceKey8
    "SCTvG-fuhO0-7lvND-eMyC8-6xC6S",  # LicenceKey8
    "BoqhK-doQ2F-wDoRa-I6nYF-meGNN",  # LicenceKey9
    "tI8Rr-x3Vcb-2qFnm-mujYU-2yzze",  # LicenceKey10
    "cqGx2-XijxC-RhywW-E7e5s-dssCx",  # LicenceKey11
    "lXDy1-FmQRD-M5aVF-sII2U-aaso6",  # LicenceKey12
    "fHO6a-fYDnF-UPDku-ivW4j-CgA5q",  # LicenceKey13
    "3oQ8u-QuzwK-zjiT2-2yGyA-UZYEd",  # LicenceKey14
    "2OEzA-aT0PD-pUkTF-BOWuI-qzv3Q",  # LicenceKey15
    "jVrjv-s75rw-lu4tV-G5GzN-uqtmL",  # LicenceKey16
    "ob70V-huQWi-b6KpD-115PP-U4mp8",  # LicenceKey17
    "QittH-B5TAq-b8Yzx-2bakg-7UA56",  # LicenceKey18
    "IqDHG-J7rnI-MW7WD-8Tsnq-0TGxm",  # LicenceKey19
    "GcEIk-YK94F-TOEKp-pld5j-Sq1qM",  # LicenceKey20
    "ZLqNI-xyMLB-PPDly-yTmhS-2PNKb",  # LicenceKey21
    "zoe0K-MOkzJ-8ONrZ-vJuTi-bIEEH",  # LicenceKey22
    "UPrKC-YQgoW-u44vB-1hU23-ZFBdw",  # LicenceKey23
    "hR7tX-Nx4qq-NM4tc-6aJbH-K4Dpf",  # LicenceKey24
    "B6cFJ-JzVNK-vUH6P-6AuZt-hpw2M",  # LicenceKey25
    "befl7-rj1b4-ZbhMR-US0wu-z1ISG",  # LicenceKey26
    "eZvUn-VXDFS-Irp1n-FMI6h-eSJL8",  # LicenceKey27
    "HOEc9-bNK48-qmHwY-7z2yt-ti75V",  # LicenceKey28
    "MRHXl-HMRIm-Sy7PS-Wi6IL-q0x9p",  # LicenceKey29
    "lBSLQ-rrolc-DeoPj-IWQOe-8d76B",  # LicenceKey30
    "KJKm6-xzKZz-obFhI-cJuR1-jH3gE",  # LicenceKey31
    "yMM0p-8vUQI-yAGmW-VSUTv-5Pt9S",  # LicenceKey32
    "bpFMJ-o3LA3-hLyIh-wkUOu-pzEvU",  # LicenceKey33
    "rUnNv-aNSQD-JE9vo-zdi3S-ABscA",  # LicenceKey34
    "Oi7gX-h25Sk-A1xWL-b6Cot-FLRLw",  # LicenceKey35
    "af97j-4yAw7-SXLKg-8bn1d-7enI8",  # LicenceKey36
    "2yUth-yFDGU-UhpTd-2fU5t-3LHGw",  # LicenceKey37
    "YPFQf-fMRna-SF8g7-WWEIb-F4lPM",  # LicenceKey38
    "sjhCW-4S6Dp-oRQ4g-wgr7y-w4X9k",  # LicenceKey39
    "7L8uk-kt9kb-JL94V-sUiBo-eLgis",  # LicenceKey40
    "aF3eg-wF9Yq-Qrwkt-SM3e8-5SfBp",  # LicenceKey41
    "DS4QV-rXavR-JKawg-e7Vfy-yvlLd",  # LicenceKey42
    "PqOxa-43AZc-YlcIL-TQtDi-awpnt",  # LicenceKey43
    "JEsqT-eUCsP-YRtZV-obUbT-sexR0",  # LicenceKey44
    "jlKVL-PJ088-W7MND-bRSXf-MTvDC",  # LicenceKey45
    "tV2OU-1CxpT-vBOCl-WYvAq-i6Gus",  # LicenceKey46
    "x5Ydz-ALoxh-VQgtY-9Z0Q3-bu6nL",  # LicenceKey47
    "6hRzS-teUnp-xxgcD-PEFmW-6ohjN",  # LicenceKey48
    "PXBUE-Wm5fT-SSB4T-Hcvko-c090X",  # LicenceKey49
    "H5tSq-xh0Dr-fCyiI-Y7pL4-XvU2m",  # LicenceKey50
    "giig7-3bbi5-5kb58-rkb95-4iw9y"   # LicenceKey51
    

]

# Ask the user for input
a = input("Enter Licence Key: ")
b = input("Enter Buyer name: ")

# Check if it matches any key
if a in licence_keys:
    print(f"You Bought it, {b}!")
else:
    print("You Didn't Buy")
