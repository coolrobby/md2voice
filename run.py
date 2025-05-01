import streamlit as st
import edge_tts
import asyncio
import re
import os
import zipfile
import shutil
import time
from io import BytesIO
from pydub import AudioSegment
import subprocess

# Voice options
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

def check_ffmpeg():
    """Check if ffmpeg/ffprobe is installed and available."""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        subprocess.run(['ffprobe', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def clean_text(text):
    """Clean and normalize text, ensuring proper spacing around punctuation."""
    if not text:
        return ""
    text = text.strip()
    # Normalize spaces around punctuation
    text = re.sub(r'\s*([,.!?;:])\s*', r'\1 ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove invalid characters for TTS
    text = re.sub(r'[^\w\s,.!?;:\u4e00-\u9fff*]', '', text)
    return text.strip()

def parse_markdown(md_text):
    """Parse markdown and extract text with language."""
    lines = md_text.strip().split('\n')
    parsed_lines = []
    
    for line in lines:
        if not line.startswith('- '):
            continue
            
        line = line[2:].strip()
        if not line:
            continue
            
        parts = []
        current_pos = 0
        
        while current_pos < len(line):
            next_asterisk = line.find('*', current_pos)
            
            if next_asterisk == -1:
                remaining_text = clean_text(line[current_pos:])
                if remaining_text:
                    parts.append(('zh', remaining_text))
                break
            elif next_asterisk > current_pos:
                chinese_text = clean_text(line[current_pos:next_asterisk])
                if chinese_text:
                    parts.append(('zh', chinese_text))
            
            end_asterisk = line.find('*', next_asterisk + 1)
            if end_asterisk == -1:
                remaining_text = clean_text(line[current_pos:])
                if remaining_text:
                    parts.append(('zh', remaining_text))
                break
            
            english_text = clean_text(line[next_asterisk + 1:end_asterisk])
            if english_text:
                next_pos = end_asterisk + 1
                while next_pos < len(line) and line[next_pos] in ',.!?;:':
                    english_text += line[next_pos]
                    next_pos += 1
                parts.append(('en', english_text))
            
            current_pos = end_asterisk + 1
            while current_pos < len(line) and line[current_pos].isspace():
                current_pos += 1
        
        if parts:
            parsed_lines.append(parts)
    
    return parsed_lines

async def generate_mp3_with_retry(text, lang, output_file, zh_voice, en_voice, max_retries=3):
    """Generate MP3 with retry mechanism and exponential backoff."""
    if not text or text.isspace() or all(c in ',.!?;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 - ;:' for c in text):
        st.warning(f"Skipping invalid text: '{text}' ({lang})")
        return False

    voice = zh_voice if lang == 'zh' else en_voice
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                return True
            else:
                st.warning(f"Generated file {output_file} is empty or invalid.")
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                st.warning(f"Retry {retry_count}/{max_retries} for text '{text}' ({lang})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            else:
                st.error(f"Failed to generate audio for text '{text}' ({lang}) after {max_retries} retries: {str(e)}")
                return False
    return False

def combine_mp3s(temp_files, output_file):
    """Combine MP3s for a single line with minimal pause."""
    if not temp_files:
        return False

    if not check_ffmpeg():
        st.error("FFmpeg is not installed. Please install FFmpeg to process audio files. See instructions at: https://ffmpeg.org/download.html")
        return False
        
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                audio = AudioSegment.from_mp3(temp_file)
                audio = audio.strip_silence(silence_len=100, silence_thresh=-50)
                if combined.duration_seconds > 0:
                    combined += AudioSegment.silent(duration=150)
                combined += audio
            except Exception as e:
                st.warning(f"Failed to process audio file {temp_file}: {str(e)}")
                continue
    
    if combined.duration_seconds > 0:
        try:
            combined.export(output_file, format="mp3")
            return True
        except Exception as e:
            st.error(f"Failed to export combined audio: {str(e)}")
            return False
    return False

# Streamlit app
st.title("Markdown to MP3 Converter")

# Check for FFmpeg at startup
if not check_ffmpeg():
    st.error("FFmpeg is not installed. This application requires FFmpeg to process audio files. Please install FFmpeg and ensure it is available in your system PATH. Instructions: https://ffmpeg.org/download.html")
else:
    # Voice selection
    st.subheader("Select Voices")
    col1, col2 = st.columns(2)

    with col1:
        zh_voice_name = st.selectbox(
            "Chinese Voice",
            list(CHINESE_VOICES.keys()) + list(BILINGUAL_VOICES.keys()),
            index=0
        )
        zh_voice = CHINESE_VOICES.get(zh_voice_name, BILINGUAL_VOICES.get(zh_voice_name))

    with col2:
        en_voice_name = st.selectbox(
            "English Voice",
            list(ENGLISH_VOICES.keys()) + list(BILINGUAL_VOICES.keys()),
            index=0
        )
        en_voice = ENGLISH_VOICES.get(en_voice_name, BILINGUAL_VOICES.get(en_voice_name))

    # Input markdown
    markdown_input = st.text_area(
        "Enter Markdown list (e.g., - 大家好，我是川哥。 *Hello, I am John.*)",
        height=200,
        value="""- 语法大招，每日一练
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
- 你学会了吗？学英语，到坦克云课堂。"""
    )

    if st.button("Generate MP3s"):
        if not markdown_input:
            st.error("Please enter some markdown text.")
        else:
            with st.spinner('Processing...'):
                # Parse markdown
                parsed_lines = parse_markdown(markdown_input)
                
                # Create temporary directory
                temp_dir = 'temp_mp3'
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Track successful and failed generations
                final_mp3_files = []
                failed_lines = []
                progress_bar = st.progress(0)
                total_lines = len(parsed_lines)
                
                for i, line_parts in enumerate(parsed_lines, 100):
                    temp_files = []
                    line_success = True
                    
                    for j, (lang, text) in enumerate(line_parts, 1):
                        temp_output = f"{temp_dir}/temp_{i}_{j}_{lang}_{time.time()}.mp3"  # Unique filename
                        success = asyncio.run(
                            generate_mp3_with_retry(text, lang, temp_output, zh_voice, en_voice)
                        )
                        if success:
                            temp_files.append(temp_output)
                        else:
                            line_success = False
                        time.sleep(0.5)  # Increased delay to avoid rate limiting
                    
                    # Combine temp MP3s
                    if temp_files:
                        output_file = f"{temp_dir}/{i}.mp3"
                        if combine_mp3s(temp_files, output_file):
                            final_mp3_files.append(output_file)
                            st.write(f"Line {i-99}: {' '.join([text for _, text in line_parts])}")
                            with open(output_file, "rb") as f:
                                st.audio(f, format="audio/mp3")
                        else:
                            line_success = False
                    
                    # Clean up temp files
                    for temp_file in temp_files:
                        if os.path.exists(temp_file):
                            try:
                                os.remove(temp_file)
                            except Exception as e:
                                st.warning(f"Failed to delete temp file {temp_file}: {str(e)}")
                    
                    if not line_success:
                        failed_lines.append(i-99)
                    
                    # Update progress
                    progress_bar.progress((i-99) / total_lines)
                
                # Create ZIP for bulk download
                if final_mp3_files:
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for mp3_file in final_mp3_files:
                            zip_file.write(mp3_file, os.path.basename(mp3_file))
                    
                    zip_buffer.seek(0)
                    st.download_button(
                        label="Download All MP3s",
                        data=zip_buffer,
                        file_name="mp3_files.zip",
                        mime="application/zip"
                    )
                
                # Clean up
                for mp3_file in final_mp3_files:
                    if os.path.exists(mp3_file):
                        try:
                            os.remove(mp3_file)
                        except Exception as e:
                            st.warning(f"Failed to delete file {mp3_file}: {str(e)}")
                
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception as e:
                        st.warning(f"Failed to delete temp directory {temp_dir}: {str(e)}")
                
                # Summary
                st.success(f"Processing complete! Generated {len(final_mp3_files)}/{total_lines} audio files.")
                if failed_lines:
                    st.warning(f"Failed to generate audio for lines: {', '.join(map(str, failed_lines))}")
