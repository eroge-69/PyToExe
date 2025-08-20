import signal
import google.generativeai as genai

API_KEY = "AIzaSyDaO9c1s-kxHg32Wk27jqsZ46s4K-rR5co"  # Replace with your API key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()

def extract_text_from_response(response):
    """Extracts text from a Gemini response."""
    try:
        if hasattr(response, "text") and response.text:
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            candidates = response.candidates
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    content = candidate.content
                    if hasattr(content, "parts") and content.parts:
                        parts = content.parts
                        if parts and len(parts) > 0:
                            part = parts[0]
                            if hasattr(part, "text") and part.text:
                                return part.text
        return None  # No text found
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

# Initial message
response = chat.send_message("hello")
output = extract_text_from_response(response)

if output:
    print("Gemini:", output)
else:
    print("Gemini: No response or extraction failed.")

print("Chat with Gemini! Type 'exit' to quit.")
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = chat.send_message(user_input)
        output = extract_text_from_response(response)

        if output:
            print("Gemini:", output)
        else:
            print("Gemini: No response or extraction failed.")

    except KeyboardInterrupt:
        print("\nCtrl+C detected. You can copy the text now. Press Enter to continue chatting, or type 'exit' to quit.")
        input()  # Wait for user to press Enter