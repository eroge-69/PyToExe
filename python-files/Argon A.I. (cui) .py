from ollama import chat

# Choose the model you want to use
#
#
#
#
#
model_name = 'gemma3:1b'  # Replace with your desired model
#
#
#
#
#
# Initialize conversation with a system prompt (optional)
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

# Start a loop to take user input
while True:
    user_input = input("You: ")
    if not user_input:  # Exit loop on empty input
        break
    
    # Append user message to the conversation
    messages.append({"role": "user", "content": user_input})
    
    # Get the model's response
    response = chat(model=model_name, messages=messages)
    
    # Print the assistant's reply
    print("Bot:", response.message.content)
    
    # Append assistant's reply to the conversation
    messages.append({"role": "assistant", "content": response.message.content})
