import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# Fungsi untuk mengambil semua komentar dari video YouTube tanpa limit
def get_comments(api_key, video_id):
    comments = []
    try:
        # Set up the YouTube API client dengan API key yang diberikan
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Mengambil komentar pertama dari video
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            textFormat='plainText'
        ).execute()

        # Loop untuk terus mengambil komentar hingga tidak ada page token lagi
        while response:
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            # Jika ada nextPageToken, ambil halaman berikutnya
            if 'nextPageToken' in response:
                response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    pageToken=response['nextPageToken'],
                    textFormat='plainText'
                ).execute()
            else:
                break  # Jika tidak ada nextPageToken, hentikan proses
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    return comments

# UI dengan Streamlit
st.title("YouTube Comments Scraper")

# Input API Key dan YouTube Video URL melalui form
if "comments" not in st.session_state:
    st.session_state.comments = []

with st.form(key='youtube_form'):
    api_key = st.text_input("Enter YouTube API Key", type="password")
    video_url = st.text_input("Enter YouTube Video URL")
    
    # Tombol submit
    submit_button = st.form_submit_button(label="Get Comments")

# Jika form di-submit, jalankan scraping komentar
if submit_button:
    if not api_key:
        st.error("Please enter a valid API Key.")
    elif not video_url:
        st.error("Please enter a valid YouTube video URL.")
    else:
        # Ambil video ID dari URL YouTube
        video_id = video_url.split("v=")[-1].split("&")[0]
        st.write(f"Video ID: {video_id}")
        
        # Progress bar
        progress_bar = st.progress(0)
        progress_text = st.empty()
        progress_text.text("Fetching comments...")

        # Ambil semua komentar
        st.session_state.comments = get_comments(api_key, video_id)
        progress_bar.progress(100)  # Selesai mengambil data

        if st.session_state.comments:
            st.success(f"Found {len(st.session_state.comments)} comments.")
        else:
            st.warning("No comments found or invalid video ID.")

# Jika komentar sudah diambil, tampilkan form untuk menyimpan file
if st.session_state.comments:
    # Meminta nama file dari pengguna
    file_name = st.text_input("Enter a name for the file (without extension)", value="youtube_comments")

    # Pilih format file (CSV atau TXT)
    file_format = st.selectbox("Choose file format", ["CSV", "TXT"])

    # Tombol untuk menyimpan file
    if st.button("Save Comments"):
        if file_format == "CSV":
            # Simpan ke file CSV
            df = pd.DataFrame(st.session_state.comments, columns=["Comment"])
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            # Tombol download untuk file CSV
            st.download_button(label="Download CSV", 
                               data=csv_data, 
                               file_name=f"{file_name}.csv", 
                               mime="text/csv")
        elif file_format == "TXT":
            # Simpan ke file TXT
            txt_data = "\n".join(st.session_state.comments).encode('utf-8')
            
            # Tombol download untuk file TXT
            st.download_button(label="Download TXT", 
                               data=txt_data, 
                               file_name=f"{file_name}.txt", 
                               mime="text/plain")
