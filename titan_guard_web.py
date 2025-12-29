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
st.markdown("Nhập URL TikTok → Tạo video 9:16 pro với watermark, CTA, hashtag trending VN!")

video_url = st.text_input("URL TikTok:", placeholder="https://www.tiktok.com/...")
watermark = st.text_input("Watermark (shop/username):", value="@MyShopVN")
cta = st.text_input("CTA (kêu gọi follow/shop):", value="Follow để nhận deal hot! 🔥")
add_caption = st.checkbox("Thêm caption + hashtag trending VN", value=True)

if st.button("TẠO VIDEO PRO"):
    if not video_url:
        st.error("Nhập URL đi bạn!")
    else:
        with st.spinner("Đang tải và xử lý..."):
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                outtmpl = f"{TEMP_DIR}/video_{timestamp}.%(ext)s"

                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio/best',
                    'outtmpl': outtmpl,
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    title = info.get('title', 'Video')

                files = glob.glob(f"{TEMP_DIR}/video_{timestamp}.*")
                path = files[0] if files else None

                if not path:
                    st.error("Không tải được video!")
                else:
                    # Load video
                    clip = VideoFileClip(path)
                    duration = clip.duration
                    final_clip = clip.subclip(0, min(15, duration))

                    # Chuyển dọc 9:16 + blur background
                    bg = final_clip.resize(width=1080*1.5).crop(x_center=final_clip.w//2, width=1080, height=1920).resize(0.1).resize(10)
                    dark = ColorClip((1080,1920), (0,0,0)).set_opacity(0.4).set_duration(final_clip.duration)
                    fg = final_clip.resize(width=1080).set_position('center')
                    layers = [bg, dark, fg]

                    # Watermark đơn giản (text)
                    if watermark:
                        wm = TextClip(watermark, fontsize=36, color='white')
                        wm = wm.set_position(('right','bottom')).set_duration(final_clip.duration).margin(right=20, bottom=40).set_opacity(0.8)
                        layers.append(wm)

                    # CTA đơn giản
                    if cta:
                        cta_clip = TextClip(cta, fontsize=70, color='yellow')
                        cta_clip = cta_clip.set_position('center').set_start(final_clip.duration - 5).set_duration(5).crossfadein(0.5)
                        layers.append(cta_clip)

                    # Caption + hashtag
                    if add_caption:
                        hashtags = " ".join(random.sample(["#Xuhuong", "#TikTokVN", "#FYP", "#Viral", "#GiángSinh2025"], 5))
                        caption = f"{title[:60]}...\n{hashtags}"
                        txt = TextClip(caption, fontsize=45, color='white')
                        txt = txt.set_position(('center','bottom')).set_duration(final_clip.duration).margin(bottom=120)
                        layers.append(txt)

                    final = CompositeVideoClip(layers, size=(1080,1920))
                    output_path = f"{OUTPUT_DIR}/final_{timestamp}.mp4"
                    final.write_videofile(output_path, fps=30, preset='ultrafast', threads=4)

                    st.success("HOÀN THÀNH!")
                    st.video(output_path)
                    with open(output_path, "rb") as f:
                        st.download_button("TẢI VIDEO VỀ", f, file_name="TitanGuard_PRO.mp4")

            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
