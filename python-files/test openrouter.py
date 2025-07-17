import asyncio
import aiohttp

class OpenRouterChatBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.models = [
            ("DeepSeek V3 0324", "deepseek/deepseek-chat-v3-0324:free"),
            ("DeepSeek-R1T2-Chimera", "tngtech/deepseek-r1t2-chimera:free"),
            ("DeepSeek-R1-0528", "deepseek/deepseek-r1-0528:free"),
            ("DeepSeek-V3-Base", "deepseek/deepseek-v3-base:free"),
            ("Llama-3.1-405B", "meta-llama/llama-3.1-405b-instruct:free"),
            ("Qwen2.5-VL-72B", "qwen/qwen2.5-vl-72b-instruct:free"),
        ]
        self.current_model = self.models[0][1]  # default to first model
        self.history = []

    def show_model_menu(self):
        print("\nAvailable Models:")
        for i, (name, _) in enumerate(self.models):
            print(f"{i + 1}. {name}")
        choice = input("Select model number to switch (or press Enter to keep current): ")
        if choice.isdigit() and 1 <= int(choice) <= len(self.models):
            self.current_model = self.models[int(choice) - 1][1]
            print(f"✅ Switched to: {self.models[int(choice) - 1][0]}")
        else:
            print(f"🔄 Using existing model: {self.get_model_name()}")

    def get_model_name(self):
        for name, id_ in self.models:
            if id_ == self.current_model:
                return name
        return "Unknown"

    async def chat(self):
        print("🤖 OpenRouter AI ChatBot (type 'exit' to quit, 'switch' to change model)")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            elif user_input.lower() == "switch":
                self.show_model_menu()
                continue

            self.history.append({"role": "user", "content": user_input})
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    }

                    payload = {
                        "model": self.current_model,
                        "messages": self.history[-10:],  # limit history
                        "temperature": 0.7,
                        "max_tokens": 1024,
                    }

                    async with session.post(self.base_url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            reply = data["choices"][0]["message"]["content"]
                            self.history.append({"role": "assistant", "content": reply})
                            print(f"{self.get_model_name()} 🤖: {reply}\n")
                        else:
                            error_text = await response.text()
                            print(f"❌ Error {response.status}: {error_text}")
            except Exception as e:
                print(f"⚠️ Error: {e}")

# Replace with your actual key
api_key = "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"

if __name__ == "__main__":
    bot = OpenRouterChatBot(api_key)
    asyncio.run(bot.chat())
