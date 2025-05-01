import streamlit as st
import edge_tts
import asyncio
import re
import os
import zipfile
import shutil
from io import BytesIO
from pydub import AudioSegment

# 语音选项
CHINESE_VOICES = {
    "Xiaoxiao (Female, Natural)": "zh-CN-XiaoxiaoNeural",
    "Yunxi (Male, Lively)": "zh-CN-YunxiNeural",
    "Yunyang (Male, News)": "zh-CN-YunyangNeural",
    "Xiaohan (Female, Gentle)": "zh-CN-XiaohanNeural",
    "Xiaomo (Female, Emotional)": "zh-CN-XiaomoNeural",
    "Xiaorui (Female, Bright)": "zh-CN-XiaoruiNeural",
    "Yunye (Male, Deep)": "zh-CN-YunyeNeural",
    "Yunhao (Male, Energetic)": "zh-CN-YunhaoNeural",
    "Xiaochen (Female, Youthful)": "zh-CN-XiaochenNeural",
    "Xiaoshuang (Female, Childlike)": "zh-CN-XiaoshuangNeural",
}

ENGLISH_VOICES = {
    "Jenny (Female, Conversational)": "en-US-JennyNeural",
    "Guy (Male, Expressive)": "en-US-GuyNeural",
    "Aria (Female, Warm)": "en-US-AriaNeural",
    "Christopher (Male, Calm)": "en-US-ChristopherNeural",
    "Ana (Female, Childlike)": "en-US-AnaNeural",
    "Brandon (Male, Authoritative)": "en-US-BrandonNeural",
    "Cora (Female, Gentle)": "en-US-CoraNeural",
    "Davis (Male, Friendly)": "en-US-DavisNeural",
    "Elizabeth (Female, Elegant)": "en-US-ElizabethNeural",
    "Eric (Male, Professional)": "en-US-EricNeural",
    "Jacob (Male, Youthful)": "en-US-JacobNeural",
    "Jane (Female, Expressive)": "en-US-JaneNeural",
    "Jason (Male, Relaxed)": "en-US-JasonNeural",
    "Michelle (Female, Bright)": "en-US-MichelleNeural",
    "Roger (Male, Narrative)": "en-US-RogerNeural",
    "Steffan (Male, Deep)": "en-US-SteffanNeural",
}

BILINGUAL_VOICES = {
    "Xiaoyi (Female, Multilingual)": "zh-CN-XiaoyiNeural",
    "Yunjian (Male, Professional)": "zh-CN-YunjianNeural",
    "Xiaoxuan (Female, Versatile)": "zh-CN-XiaoxuanNeural",
    "Yunze (Male, Mature)": "zh-CN-YunzeNeural",
}

# Markdown 解析函数
def parse_markdown(md_text):
    lines = md_text.strip().split('\n')
    parsed_lines = []
    for line in lines:
        if line.startswith('- '):
            line = line[2:].strip()
            parts = []
            while line:
                italic_match = re.match(r'\*(.*?)\*([,.!?]?)\s*', line)
                if italic_match:
                    italic_text = italic_match.group(1).strip()
                    punctuation = italic_match.group(2) or ''
                    if italic_text:
                        parts.append(('en', italic_text + punctuation))
                    line = line[italic_match.end():].strip()
                else:
                    next_italic = line.find('*')
                    if next_italic == -1:
                        if line.strip():
                            parts.append(('zh', line.strip()))
                        break
                    else:
                        text = line[:next_italic].strip()
                        if text:
                            parts.append(('zh', text))
                        line = line[next_italic:]
            if parts:
                parsed_lines.append(parts)
    st.write("Parsed segments:", parsed_lines)
    return parsed_lines

# 异步语音合成
async def generate_mp3(text, lang, output_file, zh_voice, en_voice):
    try:
        if not text or text.isspace() or all(c in '.,!?;:' for c in text.strip()):
            st.warning(f"Skipping invalid text: '{text}' ({lang})")
            return False
        voice = zh_voice if lang == 'zh' else en_voice
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        st.warning(f"Failed to generate audio for text '{text}' ({lang}): {str(e)}")
        return False

# 批量异步调用入口
async def generate_all_mp3_tasks(tasks):
    results = []
    for task in tasks:
        result = await generate_mp3(*task)
        results.append(result)
    return results

def run_async_tasks(tasks):
    try:
        return asyncio.run(generate_all_mp3_tasks(tasks))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(generate_all_mp3_tasks(tasks))

# 合并 MP3
def combine_mp3s(temp_files, output_file):
    if not temp_files:
        return
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            audio = AudioSegment.from_mp3(temp_file)
            combined += audio
            if temp_file != temp_files[-1]:
                combined += AudioSegment.silent(duration=100)
    if combined:
        combined.export(output_file, format="mp3")

# Streamlit UI
st.title("📄 Markdown to MP3 Converter")

st.subheader("🎙️ Select Voices")
col1, col2 = st.columns(2)

with col1:
    zh_voice_name = st.selectbox("Chinese Voice", list(CHINESE_VOICES.keys()) + list(BILINGUAL_VOICES.keys()), index=0)
    zh_voice = CHINESE_VOICES.get(zh_voice_name, BILINGUAL_VOICES.get(zh_voice_name))

with col2:
    en_voice_name = st.selectbox("English Voice", list(ENGLISH_VOICES.keys()) + list(BILINGUAL_VOICES.keys()), index=0)
    en_voice = ENGLISH_VOICES.get(en_voice_name, BILINGUAL_VOICES.get(en_voice_name))

markdown_input = st.text_area("📥 Enter Markdown list", height=250, value="""- 语法大招，每日一练
- 请作题。什么时候用*are you*, 什么时候用*do you*?
- 记住口诀，非常简单！有动词原型用*do you?*，没有动词原型，用*Are you*?
- *like*是动词原型
- 所以用*do you?*
- *play*是动词原型
- 所以用*do you?*
- *watching*不是动词原型
- 所以用*are you*?
- *going*不是动词原型
- 所以用*are you*?
- *want*是动词原型
- 所以用*do you*?
- 你学会了吗？学英语，到坦克云课堂。""")

if st.button("▶️ Generate MP3s"):
    if not markdown_input:
        st.error("Please enter some markdown text.")
    else:
        parsed_lines = parse_markdown(markdown_input)
        os.makedirs('temp_mp3', exist_ok=True)
        final_mp3_files = []
        async_tasks = []

        for i, line_parts in enumerate(parsed_lines, 100):
            for j, (lang, text) in enumerate(line_parts, 1):
                temp_output = f"temp_mp3/temp_{i}_{j}_{lang}.mp3"
                async_tasks.append((text, lang, temp_output, zh_voice, en_voice))

        task_results = run_async_tasks(async_tasks)

        task_index = 0
        for i, line_parts in enumerate(parsed_lines, 100):
            temp_files = []
            for j, (lang, text) in enumerate(line_parts, 1):
                temp_output = f"temp_mp3/temp_{i}_{j}_{lang}.mp3"
                if task_results[task_index]:
                    temp_files.append(temp_output)
                task_index += 1

            output_file = f"temp_mp3/{i}.mp3"
            combine_mp3s(temp_files, output_file)

            if os.path.exists(output_file):
                final_mp3_files.append(output_file)
                st.write(f"Line {i}: {' '.join([text for _, text in line_parts])}")
                with open(output_file, "rb") as f:
                    st.audio(f, format="audio/mp3")

            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        st.warning(f"Failed to delete temp file {temp_file}: {str(e)}")

        if final_mp3_files:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for mp3_file in final_mp3_files:
                    zip_file.write(mp3_file, os.path.basename(mp3_file))
            zip_buffer.seek(0)
            st.download_button("⬇️ Download All MP3s", zip_buffer, "mp3_files.zip", "application/zip")

        for mp3_file in final_mp3_files:
            if os.path.exists(mp3_file):
                try:
                    os.remove(mp3_file)
                except Exception as e:
                    st.warning(f"Failed to delete file {mp3_file}: {str(e)}")
        if os.path.exists('temp_mp3'):
            try:
                shutil.rmtree('temp_mp3')
            except Exception as e:
                st.warning(f"Failed to delete temp_mp3 directory: {str(e)}")
