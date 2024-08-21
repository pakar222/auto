import os
import google.generativeai as genai
import requests
import streamlit as st
import time

# Validasi API Key Google Gemini
def validate_google_gemini_api_key(api_key):
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    json_data = {'contents': [{'role': 'user', 'parts': [{'text': 'Give me five subcategories of jazz?'}]}]}
    response = requests.post(
        'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent',
        params=params, headers=headers, json=json_data
    )
    return response.status_code == 200

# Fungsi untuk mendapatkan saran kata kunci
def get_keyword_suggestions(topic, api_key):
    prompt = f"""
                Buatkan 3 keyword dari judul "{topic}". keyword yang dihasilkan adalah satu kata. tuliskan keyword secara langsung dengan format : keyword 1,keyword 2,keyword 3."""
    generation_config = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    response = model.generate_content(prompt)
    return [keyword.strip() for keyword in response.text.split(',') if keyword.strip()]

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)

# Set page config
st.set_page_config(page_title='Auto Generator Artikel V2',layout='wide')

# Initialize session state for API key
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'keywords' not in st.session_state:
    st.session_state.keywords = []
# Title and sidebar
st.title('Generate Artikel SEO dengan AI')
st.subheader("Buat Artikel SEO Berkualitas dengan Kemudahan AI")
with st.sidebar:
    st.title("Auto Generate Artikel")
    st.subheader('by gudanginformatika.com')
    st.image("./qr.png",width=200,use_column_width=100)
    st.caption('Jika Anda ingin mendukung proyek kami, kami sangat menghargainya!')
    if not st.session_state.api_key_valid:
        api_key = st.text_input('Masukkan API Key Google Gemini Anda', type='password')
        if st.button('Validate API Key'):
            if validate_google_gemini_api_key(api_key):
                st.session_state.api_key_valid = True
                st.session_state.api_key = api_key
                st.success('API Key valid!')
            else:
                st.error('API Key tidak valid')

if st.session_state.api_key_valid:
    genai.configure(api_key=st.session_state.api_key)
    
    # Input fields for article generation
    topik_artikel = st.text_input('Topik Artikel', placeholder="Masukkan topik artikel di sini")

    if st.button('Get Keyword Suggestions'):
        if topik_artikel:
            with st.spinner('Mengambil saran kata kunci...'):
                keyword_suggestions = get_keyword_suggestions(topik_artikel, st.session_state.api_key)
                if keyword_suggestions:
                    st.session_state.keywords = keyword_suggestions
                else:
                    st.error('Tidak dapat mengambil saran kata kunci.')
        else:
            st.error('Topik artikel belum diisi.')

    if st.session_state.keywords:
        selected_keywords = st.multiselect(
            'Pilih atau tambahkan kata kunci SEO', 
            options=st.session_state.keywords,
            default=st.session_state.keywords
        )
        st.session_state.keywords = selected_keywords

    gaya_bahasa = st.radio("Gaya Bahasa",
                           ["Informatif", "Naratif", "Kasual","Formal","Kreatif"],
                           captions=["Memberikan informasi yang akurat dan bermanfaat kepada pembaca",
                                     "Menceritakan sebuah kisah yang menarik dan engaging bagi pembaca.",
                                     "Meyakinkan pembaca untuk mengambil tindakan tertentu, seperti membeli produk, mendaftar newsletter, atau mendukung suatu opini.",
                                     "Menciptakan suasana yang santai dan bersahabat dengan pembaca.",
                                     "Menyampaikan informasi yang serius dan kredibel kepada pembaca.",
                                     "Menyampaikan informasi dengan cara yang unik dan imajinatif."])
    num_len = st.slider("Jumlah Kata Artikel", min_value=500, max_value=2000, step=100, value=1000)

    if st.button('Generate Artikel'):
        if 'keywords' in st.session_state and topik_artikel:
            with st.spinner('Memproses artikel...'):
                # Generate article prompt
                keywords = ', '.join(st.session_state.keywords)
                prompt = f"""
                Anda adalah seorang spesialis SEO dengan pengalaman dalam membuat artikel SEO berkualitas. 
                Topik artikel ini adalah "{topik_artikel}". Kata kunci SEO yang harus digunakan dalam artikel ini adalah "{keywords}". 
                Tulis artikel blog dengan gaya penulisan {gaya_bahasa}. Artikel harus memiliki jumlah kata {num_len}. 
                Pastikan artikel ini relevan, informatif, dan sesuai dengan standar SEO untuk memaksimalkan visibilitas di mesin pencari.
                """

                # Generate content
                generation_config = {
                    "temperature": 1.0,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                }

                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                )
                
                response = model.generate_content(prompt)
                article_content = response.text.strip()
                output = stream_data(article_content)
                # Display generated content
                st.write("Artikel yang Dihasilkan:")
                st.write_stream(output)
                
                # Option to edit the content
                edited_content = st.text_area("Edit Artikel", article_content, height=300)

                # Download button for the article
                st.download_button("Download Artikel", data=edited_content, file_name="artikel_seo.txt", mime="text/plain")
        else:
            st.error("Topik artikel atau kata kunci belum diisi.")
