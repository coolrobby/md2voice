import streamlit as st
import edge_tts
import asyncio
import re
import os
import zipfile
from io import BytesIO

# Function to parse markdown and extract text with language
def parse_markdown(md_text):
    lines = md_text.strip().split('\n')
    parsed_lines = []
    for line in lines:
        if line.startswith('- '):
            line = line[2:].strip()
            parts = []
            while line:
                italic_match = re.match(r'\*(.*?)\*', line)
                if italic_match:
                    italic_text = italic_match.group(1).strip()
                    if italic_text:
                        parts.append(('en', italic_text))
                    line = line[italic_match.end():].strip()
                else:
                    # Find next italic or end
                    next_italic = line.find('*')
                    if next_italic == -1:
                        if line.strip():
                            parts.append(('zh', line.strip()))
                        line = ''
                    else:
                        text = line[:next_italic].strip()
                        if text:
                            parts.append(('zh', text))
                        line = line[next_italic:]
            if parts:
                parsed_lines.append(parts)
    return parsed_lines

# Async function to generate MP3 for a single text segment
async def generate_mp3(text, lang, output_file):
    voice = 'zh-CN-XiaoxiaoNeural' if lang == 'zh' else 'en-US-JennyNeural'
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# Streamlit app
st.title("Markdown to MP3 Converter")

# Input markdown
markdown_input = st.text_area("Enter Markdown list (e.g., - 大家好，我是川哥。 *Hello, I am John.*)", height=200)

if st.button("Generate MP3s"):
    if not markdown_input:
        st.error("Please enter some markdown text.")
    else:
        # Parse markdown
        parsed_lines = parse_markdown(markdown_input)
        
        # Create temporary directory for MP3s
        if not os.path.exists('temp_mp3'):
            os.makedirs('temp_mp3')
        
        # Generate MP3s
        mp3_files = []
        for i, line_parts in enumerate(parsed_lines, 1):
            for j, (lang, text) in enumerate(line_parts, 1):
                output_file = f"temp_mp3/{i}_{lang}.mp3"
                asyncio.run(generate_mp3(text, lang, output_file))
                mp3_files.append(output_file)
                
                # Display audio player
                st.write(f"Line {i}, Part {j}: {text} ({lang})")
                with open(output_file, "rb") as f:
                    st.audio(f, format="audio/mp3")
        
        # Create ZIP for bulk download
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for mp3_file in mp3_files:
                zip_file.write(mp3_file, os.path.basename(mp3_file))
        
        zip_buffer.seek(0)
        st.download_button(
            label="Download All MP3s",
            data=zip_buffer,
            file_name="mp3_files.zip",
            mime="application/zip"
        )
        
        # Clean up
        for mp3_file in mp3_files:
            os.remove(mp3_file)
        os.rmdir('temp_mp3')
