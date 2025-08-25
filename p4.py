# p4.py
import os
import streamlit as st
from utils import (
    get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain,
    makeAudio, progressBar, extract_text_from_image
)

st.set_page_config(page_title="여행 문서/이미지 Q&A", page_icon="🗂", layout="wide")
st.title("🗂 여행 문서/이미지 Q&A")

with st.sidebar:
    st.markdown("### 📤 문서 업로드")
    pdf_docs = st.file_uploader("PDF 업로드", type=["pdf"], accept_multiple_files=True)
    img_docs = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    model_name = st.selectbox("OpenAI 모델", ["gpt-4o", "gpt-4o-mini"], index=0)

if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if (pdf_docs or img_docs) and st.button("📚 문서/이미지 분석 시작"):
    progressBar("자료를 읽는 중...")

    # PDF 텍스트 추출
    text_data = ""
    if pdf_docs:
        text_data += get_pdf_text(pdf_docs)

    # 이미지 텍스트 추출
    if img_docs:
        for img in img_docs:
            text_data += extract_text_from_image(img)

    if text_data.strip():
        chunks = get_text_chunks(text_data)
        vectorstore = get_vectorstore(chunks)
        st.session_state.conversation = get_conversation_chain(vectorstore)
        st.success("✅ 분석 준비 완료! 질문을 입력해보세요.")
    else:
        st.warning("⚠️ 텍스트를 추출할 수 없습니다. (스캔본 품질 확인 필요)")

user_q = st.text_input("궁금한 내용을 입력하세요", placeholder="예: 내 항공편 출발 시간은 언제야?")

if user_q and st.session_state.conversation:
    with st.spinner("검색 중..."):
        response = st.session_state.conversation({"question": user_q})
        answer = response["answer"]
        st.session_state.chat_history.append((user_q, answer))

        st.markdown("### ✨ 답변")
        st.write(answer)

        os.makedirs("audio", exist_ok=True)
        audio_name = "qa_answer.mp3"
        makeAudio(answer, audio_name)
        st.audio(f"audio/{audio_name}")

if st.session_state.chat_history:
    st.markdown("### 💬 대화 기록")
    for q, a in st.session_state.chat_history:
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")
