import re
from datetime import datetime

class Signal:
    def __init__(self, time, pair, direction):
        self.time = time  # HH:MM
        self.pair = pair
        self.direction = direction
        self.result = None
        self.gale_level = 0

class TradeSignalParser:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.signals = []
        self.results = []
        self.date = ""

    def parse(self):
        signal_blocks = self.raw_text.split("Exa-bot")
        signal_map = {}

        for block in signal_blocks:
            if "✅ WIN" in block or "✖ Loss" in block:
                match = re.search(r"📊(.*?)⏱(\d{2}:\d{2})🔋M1\|.\s*-»\s*(PUT|CALL)", block)
                if match:
                    pair, time, direction = match.groups()
                    key = (time.strip(), pair.strip(), direction.strip())
                    signal_map[key] = "✅" if "✅ WIN" in block else "✖"
            elif "📊" in block and "⏱" in block:
                match = re.search(r"\[(\d{1,2}/\d{1,2}/\d{4})", block)
                if match:
                    self.date = datetime.strptime(match.group(1), "%m/%d/%Y").strftime("%Y.%m.%d")

                match = re.search(r"📊(.*?)\n⏱(\d{2}:\d{2}):\d{2}\n🔋M1\n(.+)\n", block)
                if match:
                    pair, time, direction = match.groups()
                    signal = Signal(time.strip(), pair.strip(), direction.strip().split()[1])
                    self.signals.append(signal)

        # Attach results to signals
        counter = {}
        for signal in self.signals:
            key = (signal.time, signal.pair, signal.direction)
            if key in signal_map:
                signal.result = signal_map[key]
            counter[key] = counter.get(key, 0) + 1
            signal.gale_level = counter[key] - 1

    def format_summary(self):
        output = [
            "━━━━━━━━━━━━━━━━━━", 
            f"📆 Date: {self.date}",
            "━━━━━━━━━━━━━━━━━━", 
            "📈 𝐎𝐓𝐂-𝐌𝐀𝚁𝐊𝙴𝚃 𝐓𝐫𝐚𝐝𝐞s:",
            "━━━━━━━━━━━━━━━━━━"
        ]

        g0 = g1 = total = win = 0

        for s in self.signals:
            result = s.result or ""
            gale = "¹" if s.gale_level == 1 else ""
            output.append(f"❒ {s.time} - {s.pair} - {s.direction}  {result}{gale}")

            total += 1
            if result == "✅":
                win += 1
                if s.gale_level == 0:
                    g0 += 1
                elif s.gale_level == 1:
                    g1 += 1

        win_rate = (win / total * 100) if total else 0

        output += [
            "━━━━━━━━━━━━━━━━━━",
            "🔸 𝙶𝙰𝙻𝙴 𝚁𝚎𝚜𝚞𝚕𝐭s:",
            f"▪️ 𝙶𝙰𝙻𝙴 𝟶 → {g0}x2 ⋅◈⋅ ({g0 / total * 100:.0f}%)",
            f"▪️ 𝙶𝙰𝙻𝙴 𝟷 → {g1}x1 ⋅◈⋅ ({g1 / total * 100:.2f}%)",
            "━━━━━━━━━━━━━━━━━━",
            "📊 𝚃𝚘𝚝𝚊𝚕 𝚁𝐚𝐭e:",
            f"{win}x{total} ⋅◈⋅ ({win_rate:.2f}%)",
            "━━━━━━━━━━━━━━━━━━"
        ]
        return "\n".join(output)

if __name__ == "__main__":
    # Fallback CLI version due to lack of tkinter
    print("Paste your trade signal log below. Press Enter twice to process:")
    import sys
    input_text = ""
    for line in sys.stdin:
        if line.strip() == "":
            break
        input_text += line

    parser = TradeSignalParser(input_text)
    parser.parse()
    summary = parser.format_summary()
    print("\n\nFormatted Summary:\n")
    print(summary)
