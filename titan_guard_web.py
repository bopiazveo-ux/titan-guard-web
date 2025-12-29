import streamlit as st
import yt_dlp
import glob
import os
import tempfile
from datetime import datetime

# Thư mục tạm
TEMP_DIR = tempfile.gettempdir()
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="TitanGuard PRO 2025", page_icon="🛡️", layout="centered")

st.title("🛡️ TitanGuard PRO 2025")
st.markdown("### Tạo video dọc TikTok/Reels/Shorts siêu viral chỉ trong 1 click!")
st.markdown("Nhập URL TikTok → Tải video pro!")

video_url = st.text_input("🔗 Nhập URL TikTok hoặc YouTube Shorts:", placeholder="https://www.tiktok.com/@user/video/123456789")

if st.button("🚀 TẢI VIDEO NGAY!", type="primary", use_container_width=True):
    if not video_url.strip():
        st.error("⚠️ Vui lòng nhập URL video!")
    else:
        with st.spinner("Đang tải video... Vui lòng chờ 30s-1 phút ⏳"):
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
                    ydl.download([video_url])

                files = glob.glob(f"{TEMP_DIR}/video_{timestamp}.*")
                if not files:
                    st.error("❌ Không tải được video! Thử URL khác.")
                else:
                    path = files[0]
                    st.success("🎉 HOÀN THÀNH! Video đã tải về.")
                    st.video(path)

                    with open(path, "rb") as f:
                        st.download_button(
                            label="📥 TẢI VIDEO VỀ MÁY NGAY",
                            data=f,
                            file_name=f"TitanGuard_{timestamp}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )

            except Exception as e:
                st.error(f"Đã có lỗi: {str(e)}")
                st.info("Gợi ý: Thử URL TikTok khác hoặc kiểm tra kết nối mạng.")

st.markdown("---")
st.caption("TitanGuard PRO 2025 - Tool tải video TikTok đơn giản, miễn phí cho shop & creator Việt Nam")
