import os



def main():

  inp, out = "input.txt", "output.txt"

  if not os.path.exists(inp):

    print("HATA: input.txt bulunamadı.")

    input("Devam etmek için tuşa basın...")

    return

  with open(inp, "r", encoding="utf-8", errors="ignore") as f:

    lines = f.readlines()

  res = []

  for i, l in enumerate(lines):

    if l.rstrip().endswith("0"):

      res += lines[i+1:i+7]

  with open(out, "w", encoding="utf-8") as f:

    f.writelines(res)

  print("Tamamlandı! output.txt oluşturuldu.")

  input("Çıkmak için tuşa basın...")



if __name__ == "__main__":

  main()