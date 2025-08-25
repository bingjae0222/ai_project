import os
import streamlit as st

st.set_page_config(page_title="메인", page_icon="🏠", layout="wide")

st.title("🏠 메인 페이지")
st.caption("사이드의 Pages에서 각 기능 페이지로 이동하세요!")


st.markdown("- 🗓 **여행일정 생성기** : OpenAI로 일정 생성 + Gemini 핵심 요약")
st.markdown("- 💵 **여행 예산 견적서** : 활동별 비용 합계 + 현지 통화 출력")
st.markdown(" - 🧳 **짐 꾸리기 체크리스트** : 조건 맞춤형 체크리스트 생성 및 저장")
st.markdown("- 🗂 **문서/이미지 Q&A** : PDF/캡쳐 이미지 업로드 → 텍스트 분석 + 오디오 답변")

st.divider()

# ---------- 사이드바 ----------
with st.sidebar:
    st.subheader("🔑 키 상태")
    st.write("OPENAI_API_KEY:", "✅" if os.getenv("OPENAI_API_KEY") else "❌")
    st.write("GOOGLE_API_KEY:", "✅" if os.getenv("GOOGLE_API_KEY") else "❌")
