import streamlit as st
from openai import OpenAI
import requests
import base64

# 设置你的TTS API密钥（这里用ElevenLabs示例，可替换为其他TTS服务）
TTS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
TTS_API_KEY = "sk_bb981b42762f920904beaa5cadee3f18ac8166c487b34c12"  # 替换为你的TTS API Key

# Show title and description.
st.title("📄 Document Question Answering with Text-to-Speech")
st.write(
    "Upload a document, ask a question, and listen to the AI-generated response!"
)

# 嵌入 HTML5 视频播放器（可选）
video_html = """
    <video width="100%" height="auto" controls>
        <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>
"""
st.components.v1.html(video_html, height=400)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        answer = response.choices[0].message.content
        st.write("### AI Response:")
        st.write(answer)

        # 调用 TTS API 将文本转换为语音
        def text_to_speech(text):
            headers = {
                "xi-api-key": TTS_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                "voice": "Rachel"  # 替换为你的TTS API支持的声音
            }

            response = requests.post(TTS_API_URL, json=data, headers=headers)
            if response.status_code == 200:
                return response.content  # 返回音频二进制数据
            else:
                st.error("TTS API 出错，请检查 API Key 或请求参数")
                return None

        # 生成语音
        audio_data = text_to_speech(answer)

        if audio_data:
            # 保存音频文件
            audio_path = "output_audio.mp3"
            with open(audio_path, "wb") as f:
                f.write(audio_data)

            # 在 Streamlit 页面播放音频
            st.audio(audio_path, format="audio/mp3")



