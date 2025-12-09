import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pdf2image import convert_from_bytes

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Configuration for the model
# NOTE: Ensure 'gemini-2.5-flash' is available in your account. 
# If not, fallback to 'gemini-1.5-flash'
MODEL_NAME = 'gemini-2.5-flash' 

def get_gemini_response(input_prompt, content):
    """
    Handles both text-only and image-based (multimodal) requests.
    content can be a string (text) or a list containing an image.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content([input_prompt, content])
    return response.text

# --- UI SETUP ---
st.set_page_config(page_title="Resume Roaster", layout="wide")
st.title("🔥 The Brutal Google Resume Reviewer")
st.write("Built with Gemini & Google Cloud")

# Create tabs for the two options
tab1, tab2 = st.tabs(["✍️ Paste Text", "📂 Upload PDF (Visual Roast)"])

# --- OPTION 1: PASTE TEXT (Your original code) ---
with tab1:
    st.subheader("Text-Based Roast")
    st.info("Good for checking content, keywords, and grammar.")
    
    resume_text = st.text_area("Paste your resume summary here:", height=300, key="text_input")

    if st.button("Roast My Text", key="text_btn"):
        if resume_text:
            with st.spinner("Gemini is reading your text..."):
                prompt = """
                Act as a brutal Google Recruiter. 
                Analyze this resume snippet and give 3 specific, hard reasons why you would REJECT it. 
                Then give 1 way to fix it to make it Google-ready.
                """
                # For text, we pass the text as the second argument
                feedback = get_gemini_response(prompt, resume_text)
                st.markdown(feedback)
        else:
            st.warning("Paste something first!")

# --- OPTION 2: UPLOAD PDF (New Visual Roast) ---
with tab2:
    st.subheader("Visual & Layout Roast")
    st.info("Gemini will look at the actual design, whitespace, and formatting of your PDF.")
    
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

    if st.button("Roast My PDF", key="pdf_btn"):
        if uploaded_file is not None:
            with st.spinner("Converting PDF to image and judging your design choices..."):
                try:
                    # 1. Convert PDF to Image (first page only for speed)
                    # poppler_path=None assumes poppler is in your PATH. 
                    # If on Windows and it fails, you might need: poppler_path=r'C:\path\to\poppler\bin'
                    images = convert_from_bytes(uploaded_file.read())
                    first_page_image = images[0]

                    # 2. Define the Vision Prompt
                    vision_prompt = """
                    Act as a brutal Google Recruiter. 
                    Look at this resume image. I want you to roast two things:
                    1. The VISUAL LAYOUT: Comment on the whitespace, font choice, density, and formatting. Is it ugly? Is it hard to read?
                    2. The CONTENT: Pick one specific bullet point that is weak and explain why.
                    
                    Be harsh but helpful.
                    """

                    # 3. Call Gemini with the Image
                    feedback = get_gemini_response(vision_prompt, first_page_image)
                    
                    # Display the image alongside the feedback
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(first_page_image, caption="What Gemini saw", use_column_width=True)
                    with col2:
                        st.markdown(feedback)

                except Exception as e:
                    st.error(f"Error processing PDF. Make sure 'Poppler' is installed on your system. Details: {e}")
        else:
            st.warning("Please upload a PDF file first!")