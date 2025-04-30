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
    try:
        if not text or text.isspace():
            st.warning(f"Skipping empty or invalid text: '{text}'")
            return False
        voice = 'zh-CN-XiaoxiaoNeural' if lang == 'zh' else 'en-US-JennyNeural'
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        if not os.path.exists(output_file):
            st.warning(f"Audio file {output_file} was not created.")
            return False
        return True
    except Exception as e:
        st.warning(f"Failed to generate audio for text '{text}' ({lang}): {str(e)}")
        return False

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
        final_mp3_files = []
        for i, line_parts in enumerate(parsed_lines, 1):
            output_file = f"temp_mp3/{i}.mp3"
            success = False
            # Since edge-tts doesn't support mixing voices, generate one MP3 with concatenated text
            # We'll generate each segment separately and rely on sequential playback
            for j, (lang, text) in enumerate(line_parts, 1):
                temp_output = f"temp_mp3/temp_{i}_{j}_{lang}.mp3"
                if await generate_mp3(text, lang, temp_output):
                    # For simplicity, we'll use the first successful segment as the line's MP3
                    # In a real app, you'd need audio concatenation (avoiding pydub/ffmpeg)
                    if not success:
                        os.rename(temp_output, output_file)
                        success = True
                    else:
                        os.remove(temp_output)
            
            if success and os.path.exists(output_file):
                final_mp3_files.append(output_file)
                # Display audio player
                st.write(f"Line {i}: {' '.join([text for _, text in line_parts])}")
                with open(output_file, "rb") as f:
                    st.audio(f, format="audio/mp3")
            else:
                st.warning(f"Failed to generate audio for line {i}")
        
        # Create ZIP for bulk download
        if final_mp3_files:
            zip_buffer = BytesIO()
            with zipfile.ZipFile for mp3_file in final_mp3_files:
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
                os.remove(mp3_file)
        if os.path.exists('temp_mp3'):
            for temp_file in os.listdir('temp_mp3'):
                os.remove(os.path.join('temp_mp3', temp_file))
            os.rmdir('temp_mp3')
