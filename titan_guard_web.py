import streamlit as st
import yt_dlp
from moviepy.editor import *
import glob
import os
import tempfile
import random
from datetime import datetime

# Thư mục
TEMP_DIR = tempfile.gettempdir()
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.title("🛡️ TitanGuard PRO 2025 - Video Dọc Viral")
st.markdown("### Nhập URL TikTok → Tạo video 9:16 pro với watermark, CTA, hashtag trending VN!")

video_url = st.text_input("URL TikTok:", placeholder="https://www.tiktok.com/...")
watermark = st.text_input("Watermark (shop/username):", value="@MyShopVN")
cta = st.text_input("CTA (kêu gọi follow/shop):", value="Follow để nhận deal hot! 🔥")
add_caption = st.checkbox("Thêm caption + hashtag trending VN", value=True)

if st.button("🚀 TẠO VIDEO PRO NGAY!", type="primary", use_container_width=True):
    if not video_url:
        st.error("Nhập URL đi bạn!")
    else:
        with st.spinner("Đang tải và xử lý video... Chờ 1-3 phút nhé ⏳"):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                outtmpl = f"{TEMP_DIR}/video_{timestamp}.%(ext)s"

                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio/best',
                    'outtmpl': outtmpl,
                    'quiet': True,
                    'noplaylist': True,
                    'impersonate': 'chrome',  # Fix cảnh báo impersonate
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    title = info.get('title', 'Video TikTok')

                files = glob.glob(f"{TEMP_DIR}/video_{timestamp}.*")
                if not files:
                    st.error("Không tải được video! Thử URL khác.")
                else:
                    path = files[0]

                    # Fix video_fps
                    try:
                        clip = VideoFileClip(path)
                        has_video = True
                    except:
                        st.warning("File chỉ có audio → tạo nền đen")
                        audio_clip = AudioFileClip(path)
                        clip = ColorClip((1080,1920), color=(0,0,0)).set_duration(audio_clip.duration).set_audio(audio_clip)
                        has_video = False

                    duration = clip.duration
                    final_clip = clip.subclip(0, min(15, duration))

                    # Background
                    if has_video:
                        bg = final_clip.resize(width=1080*1.5).crop(x_center=final_clip.w//2, width=1080, height=1920).resize(0.1).resize(10)
                        dark = ColorClip((1080,1920), (0,0,0)).set_opacity(0.4).set_duration(final_clip.duration)
                        fg = final_clip.resize(width=1080).set_position('center')
                        layers = [bg, dark, fg]
                    else:
                        layers = [ColorClip((1080,1920), (0,0,0)).set_duration(final_clip.duration)]

                    # Watermark (text đơn giản)
                    if watermark.strip():
                        wm = TextClip(watermark.strip(), fontsize=36, color='white', font='Arial-Bold')
                        wm = wm.set_position(('right','bottom')).set_duration(final_clip.duration).margin(right=20, bottom=40).set_opacity(0.8)
                        layers.append(wm)

                    # CTA
                    if cta.strip():
                        cta_dur = min(5, final_clip.duration)
                        cta_clip = TextClip(cta.strip(), fontsize=70, color='yellow', font='Arial-Bold')
                        cta_clip = cta_clip.set_position('center').set_start(final_clip.duration - cta_dur).set_duration(cta_dur).crossfadein(0.5).crossfadeout(0.5)
                        layers.append(cta_clip)

                    # Caption + Hashtag trending VN (dùng Markdown thay TextClip)
                    if add_caption:
                        hashtags = " ".join(random.sample([
                            "#Xuhuong", "#TikTokVN", "#FYP", "#Viral", "#GiángSinh2025", "#Noel2025"
                        ], 5))
                        caption_text = f"**{title[:80]}...**\n{hashtags}"
                        st.markdown(caption_text)

                    # Tổng hợp và render
                    final = CompositeVideoClip(layers, size=(1080,1920))
                    output_path = f"{OUTPUT_DIR}/final_{timestamp}.mp4"
                    final.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac', preset='ultrafast', threads=4, logger=None)

                    st.success("🎉 HOÀN THÀNH! Video TitanGuard PRO đã sẵn sàng!")
                    st.video(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("TẢI VIDEO VỀ", f, file_name="TitanGuard_PRO.mp4", use_container_width=True)

            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
                st.info("Gợi ý: Thử URL TikTok khác hoặc kiểm tra kết nối mạng.")

st.markdown("---")
st.caption("TitanGuard Web PRO 2025 - Tool tạo video viral miễn phí cho shop & creator Việt Nam")
