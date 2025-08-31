import streamlit as st
import openai

# Configure OpenRouter API
openai.api_base = "https://openrouter.ai/api/v1"
#openai.api_key = "your_openrouter_api_key_here"  # Replace with your OpenRouter key

openai.api_key = "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"


st.title("SEO Article Writer with DeepSeek (Free via OpenRouter)")

def generate_article(keyword, writing_style, word_count):
    # Craft a detailed prompt for SEO article generation
    prompt = f"""
    Write a comprehensive SEO-optimized article about: {keyword}
    Writing style: {writing_style}
    Target word count: Approximately {word_count} words
    Structure the article with:
    - An engaging introduction
    - Clear headings and subheadings
    - Bullet points or numbered lists where appropriate
    - Natural inclusion of relevant keywords
    - A concise conclusion
    Ensure the content is original, informative, and valuable to readers.
    """

    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1:free",  # Use a free DeepSeek model :cite[1]:cite[3]
            messages=[{"role": "user", "content": prompt}],
            max_tokens=word_count * 2,  # Adjust based on word count (approx 1 token ≈ 0.75 words)
            temperature=0.7,  # Balance creativity and coherence
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating article: {str(e)}"

# Streamlit UI
keyword = st.text_input("Enter a keyword:")
writing_style = st.selectbox("Select writing style:", ["Casual", "Informative", "Professional", "Witty"])
#word_count = st.slider("Select word count:", min_value=300, max_value=1000, step=100, value=300)
word_count = st.slider("Select word count:", min_value=300, max_value=10000, step=100, value=300)
submit_button = st.button("Generate Article")

if submit_button:
    if not keyword.strip():
        st.warning("Please enter a keyword!")
    else:
        with st.spinner("Generating article via DeepSeek (Free)..."):
            article = generate_article(keyword, writing_style, word_count)
        
        if article.startswith("Error"):
            st.error(article)
        else:
            st.success("Article generated successfully!")
            st.write(article)
            st.download_button(
                label="Download Article",
                data=article,
                file_name=f"{keyword.replace(' ', '_')}_article.txt",
                mime="text/plain"
            )
