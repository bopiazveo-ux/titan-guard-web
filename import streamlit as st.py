import streamlit as st
import yt_dlp
from moviepy.editor import *
import glob
import os
import numpy as np
from datetime import datetime
import random
import tempfile

# Thư mục tạm và output
TEMP_DIR = tempfile.gettempdir()
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Caption sạch + hashtag trending VN tháng 12/2025
def generate_caption(text):
    if not text:
        return "Video hot từ TikTok! 🎄✨"
    clean_text = str(text)[:120]
    if len(str(text)) > 120:
        clean_text += "..."
    return clean_text + " 🔥"

st.set_page_config(page_title="TitanGuard PRO", page_icon="🛡️")

st.title("🛡️ TitanGuard PRO 2025")
st.markdown("**Tạo video dọc TikTok/Reels/Shorts siêu viral chỉ trong 1 click!**")
st.markdown("Nhập URL TikTok → Chọn tùy chọn → Tải video pro có watermark, CTA, caption + hashtag trending VN 🎄")

video_url = st.text_input("🔗 Nhập URL TikTok hoặc YouTube Shorts:", placeholder="https://www.tiktok.com/...")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛡️ Bảo vệ & Kêu gọi hành động")
    add_watermark = st.checkbox("Thêm Watermark (góc dưới)", value=True)
    watermark_text = st.text_input("Nội dung watermark:", value="@MyShopVN")

    add_cta = st.checkbox("Thêm CTA lớn (Follow/Shop)", value=True)
    cta_text = st.text_input("Nội dung CTA:", value="Follow ngay để nhận deal hot! 🔥")
    cta_position = st.selectbox("Vị trí CTA:", ["end", "middle", "start"], index=0)
    cta_zoom = st.checkbox("Hiệu ứng zoom nhẹ", value=True)
    cta_icon = st.text_input("Icon động cho CTA:", value="🔥")

with col2:
    st.subheader("✂️ Tối ưu video")
    add_caption = st.checkbox("Caption + Hashtag trending VN", value=True)
    auto_hook = st.checkbox("Auto cắt 15s đầu (hook mạnh)", value=True)

if st.button("🚀 TẠO VIDEO PRO NGAY!", type="primary"):
    if not video_url.strip():
        st.error("⚠️ Vui lòng nhập URL video!")
    else:
        with st.spinner("Đang tải và xử lý video... (1-3 phút, vui lòng chờ)"):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                outtmpl = f"{TEMP_DIR}/video_{timestamp}.%(ext)s"

                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio/best',
                    'outtmpl': outtmpl,
                    'quiet': True,
                    'noplaylist': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    title = info.get('title', 'Video TikTok')

                files = glob.glob(f"{TEMP_DIR}/video_{timestamp}.*")
                if not files:
                    st.error("Không tải được video! Thử URL khác.")
                else:
                    path = files[0]

                    # Xử lý video (logic đơn giản nhưng đầy đủ)
                    try:
                        clip = VideoFileClip(path)
                    except:
                        audio_clip = AudioFileClip(path)
                        clip = ColorClip((1080,1920), color=(0,0,0)).set_duration(audio_clip.duration).set_audio(audio_clip)

                    duration = clip.duration
                    final_clip = clip.subclip(0, min(15, duration)) if auto_hook else clip

                    # Background blur nếu có video
                    try:
                        bg = final_clip.resize(width=1080*1.5).crop(x_center=final_clip.w//2, width=1080, height=1920).resize(0.1).resize(10)
                        dark = ColorClip((1080,1920), (0,0,0)).set_opacity(0.4).set_duration(final_clip.duration)
                        fg = final_clip.resize(width=1080).set_position('center')
                        layers = [bg, dark, fg]
                    except:
                        layers = [ColorClip((1080,1920), (0,0,0)).set_duration(final_clip.duration)]

                    # Watermark
                    if add_watermark:
                        wm = TextClip(watermark_text, fontsize=36, color='white', font='Arial-Bold', stroke_color='black', stroke_width=2)
                        wm = wm.set_position(('right','bottom')).set_duration(final_clip.duration).margin(right=20, bottom=40, opacity=0).set_opacity(0.8)
                        layers.append(wm)

                    # CTA nâng cao
                    if add_cta:
                        cta_dur = min(5, final_clip.duration)
                        start_time = {"end": final_clip.duration - cta_dur, "middle": final_clip.duration/2 - cta_dur/2, "start": 0}[cta_position]
                        cta = TextClip(cta_text, fontsize=70, color='yellow', font='Arial-Bold', stroke_color='black', stroke_width=5)
                        cta = cta.set_position('center').set_start(start_time).set_duration(cta_dur)
                        if cta_zoom:
                            cta = cta.resize(lambda t: 1 + 0.2*min(t/1.5,1))
                        cta = cta.crossfadein(0.5).crossfadeout(0.5)
                        layers.append(cta)

                        if cta_icon:
                            icon = TextClip(cta_icon, fontsize=120, color='red')
                            icon = icon.set_position('center').set_start(start_time).set_duration(cta_dur)
                            icon = icon.set_opacity(lambda t: 0.8 + 0.2*abs(np.sin(6*t)))
                            layers.append(icon)

                    # Caption + Hashtag
                    if add_caption:
                        base = generate_caption(title)
                        hashtags = " ".join(random.sample(["#Xuhuong", "#TikTokVN", "#FYP", "#Viral", "#GiángSinh2025", "#Noel2025", "#HappyNewYear2026", "#ForYou", "#CapCut"], 6))
                        caption_text = f"{base}\n{hashtags}"
                        txt = TextClip(caption_text, fontsize=45, color='white', font='Arial-Bold', stroke_color='black', stroke_width=3)
                        txt = txt.set_position(('center','bottom')).set_duration(final_clip.duration).margin(bottom=120)
                        layers.append(txt)

                    final = CompositeVideoClip(layers, size=(1080,1920))

                    output_path = f"{OUTPUT_DIR}/TitanGuard_{timestamp}.mp4"
                    final.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4, logger=None)

                    st.success("🎉 HOÀN THÀNH! Video TitanGuard PRO đã sẵn sàng!")
                    st.video(output_path)

                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 TẢI VIDEO VỀ MÁY NGAY",
                            data=f,
                            file_name=f"TitanGuard_PRO_{timestamp}.mp4",
                            mime="video/mp4"
                        )

            except Exception as e:
                st.error(f"Đã có lỗi: {str(e)}")
                st.info("Thử lại với URL TikTok khác hoặc kiểm tra kết nối mạng.")

st.markdown("---")
st.caption("TitanGuard Web PRO 2025 - Tool tạo video viral cho shop & creator Việt Nam | Watermark + CTA + Hashtag trending VN")