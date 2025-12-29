import streamlit as st
import yt_dlp
from moviepy.editor import *
import glob
import os
import numpy as np
from datetime import datetime
import random
import tempfile

# Buộc dùng Pygame renderer để tránh lỗi ImageMagick/ffmpeg
from moviepy.config import change_settings
change_settings({"TEXT_RENDERER": "pygame"})

# Thư mục tạm và output
TEMP_DIR = tempfile.gettempdir()
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Caption sạch đơn giản
def generate_caption(text):
    if not text:
        return "Video hot từ TikTok! 🎄✨"
    clean_text = str(text)[:120]
    if len(str(text)) > 120:
        clean_text += "..."
    return clean_text + " 🔥"

# Giao diện web
st.set_page_config(page_title="TitanGuard PRO 2025", page_icon="🛡️", layout="centered")

st.title("🛡️ TitanGuard PRO 2025")
st.markdown("### Tạo video dọc TikTok/Reels/Shorts siêu viral chỉ trong 1 click!")
st.markdown("Nhập URL TikTok → Chọn tùy chọn → Tải video pro có watermark, CTA, hashtag trending VN 🎅✨")

video_url = st.text_input("🔗 Nhập URL TikTok hoặc YouTube Shorts:", placeholder="https://www.tiktok.com/@user/video/123456789")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🛡️ Bảo vệ & Kêu gọi hành động")
    add_watermark = st.checkbox("Thêm Watermark (góc dưới phải)", value=True)
    watermark_text = st.text_input("Nội dung watermark:", value="@MyShopVN")

    add_cta = st.checkbox("Thêm CTA lớn (Follow/Shop)", value=True)
    cta_text = st.text_input("Nội dung CTA:", value="Follow ngay để nhận deal hot! 🔥")
    cta_position = st.selectbox("Vị trí CTA:", ["end", "middle", "start"], index=0)
    cta_zoom = st.checkbox("Hiệu ứng zoom nhẹ vào CTA", value=True)
    cta_icon = st.text_input("Icon động cho CTA:", value="🔥")

with col2:
    st.subheader("✂️ Tối ưu video")
    add_caption = st.checkbox("Caption + Hashtag trending VN", value=True)
    auto_hook = st.checkbox("Auto cắt 15s đầu (hook mạnh)", value=True)

if st.button("🚀 TẠO VIDEO PRO NGAY!", type="primary", use_container_width=True):
    if not video_url.strip():
        st.error("⚠️ Vui lòng nhập URL video!")
    else:
        with st.spinner("Đang tải và xử lý video... Vui lòng chờ 1-3 phút ⏳"):
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
                    st.error("❌ Không tải được video! Thử URL khác.")
                else:
                    path = files[0]

                    # Load video/audio an toàn
                    try:
                        clip = VideoFileClip(path)
                        has_video = True
                        st.info("✅ Có video thật → hiệu ứng blur đẹp")
                    except:
                        st.warning("Video stream lỗi → dùng audio-only với nền đen")
                        audio_clip = AudioFileClip(path)
                        clip = ColorClip((1080,1920), color=(0,0,0)).set_duration(audio_clip.duration).set_audio(audio_clip)
                        has_video = False

                    duration = clip.duration
                    final_clip = clip.subclip(0, min(15, duration)) if auto_hook else clip

                    # Background blur nếu có video
                    if has_video:
                        bg = final_clip.resize(width=1080*1.5).crop(x_center=final_clip.w//2, width=1080, height=1920).resize(0.1).resize(10)
                        dark = ColorClip((1080,1920), (0,0,0)).set_opacity(0.4).set_duration(final_clip.duration)
                        fg = final_clip.resize(width=1080).set_position('center')
                        layers = [bg, dark, fg]
                    else:
                        layers = [ColorClip((1080,1920), (0,0,0)).set_duration(final_clip.duration)]

                    # Watermark
                    if add_watermark:
                        wm = TextClip(watermark_text, fontsize=36, color='white', font='Arial-Bold',
                                      stroke_color='black', stroke_width=2)
                        wm = wm.set_position(('right','bottom')).set_duration(final_clip.duration)
                        wm = wm.margin(right=20, bottom=40, opacity=0).set_opacity(0.8)
                        layers.append(wm)

                    # CTA nâng cao
                    if add_cta:
                        cta_dur = min(5, final_clip.duration)
                        start_time = final_clip.duration - cta_dur if cta_position == "end" else (final_clip.duration/2 - cta_dur/2) if cta_position == "middle" else 0
                        cta = TextClip(cta_text, fontsize=70, color='yellow', font='Arial-Bold',
                                       stroke_color='black', stroke_width=5)
                        cta = cta.set_position('center').set_start(start_time).set_duration(cta_dur)
                        if cta_zoom:
                            cta = cta.resize(lambda t: 1 + 0.2 * min(t/1.5, 1))
                        cta = cta.crossfadein(0.5).crossfadeout(0.5)
                        layers.append(cta)

                        if cta_icon:
                            icon = TextClip(cta_icon, fontsize=120, color='red')
                            icon = icon.set_position('center').set_start(start_time).set_duration(cta_dur)
                            icon = icon.set_opacity(lambda t: 0.8 + 0.2 * abs(np.sin(6*t)))
                            layers.append(icon)

                    # Caption + Hashtag trending VN
                    if add_caption:
                        base = generate_caption(title)
                        hashtags = " ".join(random.sample([
                            "#Xuhuong", "#TikTokVN", "#FYP", "#Viral", "#ForYou",
                            "#GiángSinh2025", "#Noel2025", "#HappyNewYear2026",
                            "#NămMới2026", "#MerryChristmas", "#Review", "#CapCut"
                        ], 6))
                        caption_text = f"{base}\n{hashtags}"
                        txt = TextClip(caption_text, fontsize=45, color='white', font='Arial-Bold',
                                       stroke_color='black', stroke_width=3)
                        txt = txt.set_position(('center','bottom')).set_duration(final_clip.duration).margin(bottom=120)
                        layers.append(txt)

                    # Tổng hợp và render
                    final = CompositeVideoClip(layers, size=(1080,1920))
                    output_path = f"{OUTPUT_DIR}/TitanGuard_{timestamp}.mp4"
                    final.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac',
                                          preset='ultrafast', threads=4, logger=None)
                    st.success("🎉 HOÀN THÀNH! Video TitanGuard PRO đã sẵn sàng!")
                    st.video(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 TẢI VIDEO VỀ MÁY NGAY",
                            data=f,
                            file_name=f"TitanGuard_PRO_{timestamp}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"Đã có lỗi: {str(e)}")
                st.info("Gợi ý: Thử URL TikTok khác hoặc kiểm tra kết nối mạng.")

st.markdown("---")
st.caption("TitanGuard Web PRO 2025 - Tool tạo video viral miễn phí cho shop & creator Việt Nam | Watermark + CTA + Hashtag trending VN")
