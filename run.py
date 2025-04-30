import asyncio
import streamlit as st
import edge_tts
import re
import tempfile
import os

async def text_to_speech(markdown_input):
    # 定义语音
    voices = {
        "zh": "zh-CN-XiaoxiaoNeural",  # 中文女声
        "en": "en-US-JennyNeural"      # 英文女声
    }
    
    # 解析 Markdown 列表
    lines = [line.strip() for line in markdown_input.strip().split("\n") if line.strip().startswith("- ")]
    
    # 处理每行
    audio_files = []
    for index, line in enumerate(lines, 1):
        line = line[2:].strip()  # 移除 "- "
        sentences = []
        
        # 查找斜体内容 (*text*)
        parts = re.split(r'(\*[^\*]+\*)', line)
        for part in parts:
            if part.startswith("*") and part.endswith("*"):
                # 斜体内容，英文语音
                text = part[1:-1].strip()
                if text:
                    sentences.append((text, "en"))
            else:
                # 普通内容，中文语音
                text = part.strip()
                if text:
                    sentences.append((text, "zh"))
        
        # 构建 SSML
        ssml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        ssml += '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">\n'
        
        for text, lang in sentences:
            ssml += f'  <voice name="{voices[lang]}">{text}</voice>\n'
        
        ssml += '</speak>'
        
        # 生成音频
        output_file = f"{index}.mp3"
        communicate = edge_tts.Communicate(ssml)
        await communicate.save(output_file)
        audio_files.append(output_file)
    
    return audio_files

def main():
    st.title("Markdown to Speech with Edge TTS")
    st.write("输入 Markdown 格式的文本，每行以 `- ` 开头。普通文本使用中文语音，斜体文本（*text*）使用英文语音。")
    
    # 输入区域
    markdown_input = st.text_area(
        "输入 Markdown 文本",
        value="""
- 大家好，我是川哥。 *Hello, I am John.*
- 你好。 *Nice to meet you.*
""",
        height=200
    )
    
    if st.button("生成音频"):
        if markdown_input.strip():
            # 运行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_files = loop.run_until_complete(text_to_speech(markdown_input))
            loop.close()
            
            # 显示音频文件
            st.success("音频生成完成！")
            for audio_file in audio_files:
                with open(audio_file, "rb") as f:
                    st.audio(f, format="audio/mp3")
                    st.download_button(
                        label=f"下载 {audio_file}",
                        data=f,
                        file_name=audio_file,
                        mime="audio/mp3"
                    )
                # 清理临时文件
                if os.path.exists(audio_file):
                    os.remove(audio_file)
        else:
            st.error("请输入有效的 Markdown 文本！")

if __name__ == "__main__":
    main()
