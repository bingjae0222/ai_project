# p3.py
import os
import streamlit as st
from utils import makeMsg, openAiModelArg, geminiTxt, progressBar

st.set_page_config(page_title="짐 꾸리기 체크리스트", page_icon="🧳", layout="wide")
st.title("🧳 짐 꾸리기 체크리스트")

with st.sidebar:
    city = st.text_input("도시", value="도쿄")
    days = st.number_input("여행 일수", min_value=1, max_value=30, value=4, step=1)
    season = st.selectbox("계절", ["봄", "여름", "가을", "겨울"], index=2)
    model_name = st.selectbox("OpenAI 모델", ["gpt-4o", "gpt-4o-mini"], index=0)

activities = st.multiselect(
    "활동 선택",
    ["도보 관광", "박물관/전시", "사진 촬영", "등산/야외", "해변", "맛집 투어", "쇼핑", "비즈니스 미팅"],
    default=["도보 관광", "맛집 투어"]
)
traveler = st.selectbox("여행 타입", ["혼자", "커플", "가족", "친구"], index=0)

if "packing_items" not in st.session_state:
    st.session_state.packing_items = []

if st.button("체크리스트 생성"):
    progressBar("체크리스트를 생성 중입니다...")
    system = (
        "너는 여행 준비 어시스턴트다. 항목을 카테고리별로 제시하되, 각 항목은 한 줄씩 간결하게 나열한다. "
        "필수/선택을 구분하고, 전자기기/의류/세면도구/서류/상비약/기타로 묶어라. "
        "출력은 불릿 리스트 형태(- 기호)로만 제공한다."
    )
    user = f"{city}로 {days}일 {season} 여행을 간다. 여행 타입은 {traveler}이고 활동은 {', '.join(activities)}이다."
    msgs = makeMsg(system, user)
    raw = openAiModelArg(model_name, msgs)
    items = [ln.strip("- ").strip() for ln in raw.splitlines() if ln.strip().startswith("-")]
    st.session_state.packing_items = [it for it in items if it]

    tip = geminiTxt(
        f"아래 짐 목록을 보고, 놓치기 쉬운 필수 2가지만 한국어로 한 문장에 제안해줘.\n\n{raw}"
    )
    st.success("체크리스트 생성 완료")
    st.write(tip)

if st.session_state.packing_items:
    st.markdown("### 체크리스트")
    left, right = st.columns(2)
    half = (len(st.session_state.packing_items)+1)//2
    for i, it in enumerate(st.session_state.packing_items):
        (left if i < half else right).checkbox(it, key=f"pk_{i}")

    all_txt = "\n".join(
        [("- [x] " if st.session_state.get(f"pk_{i}") else "- [ ] ") + it
         for i, it in enumerate(st.session_state.packing_items)]
    )
    checked_items = [
        it for i, it in enumerate(st.session_state.packing_items)
        if st.session_state.get(f"pk_{i}")
    ]
    checked_txt = "\n".join([f"- [x] {it}" for it in checked_items]) if checked_items else ""

    # 📂 txt 폴더 자동 저장 (파일명: 도시_일수일_계절.txt)
    os.makedirs("txt", exist_ok=True)
    base_name = f"{city}_{days}일_{season}"
    with open(f"txt/{base_name}_전체.txt", "w", encoding="utf-8") as f:
        f.write(all_txt)
    if checked_items:
        with open(f"txt/{base_name}_체크됨.txt", "w", encoding="utf-8") as f:
            f.write(checked_txt)

    # 📥 다운로드 버튼
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "전체 항목 저장 (.txt)",
            data=all_txt,
            file_name=f"{base_name}_all.txt",
            mime="text/plain",
        )
    with c2:
        st.download_button(
            "체크된 항목만 저장 (.txt)",
            data=checked_txt if checked_items else "체크된 항목이 없습니다.",
            file_name=f"{base_name}_checked.txt",
            mime="text/plain",
            disabled=not bool(checked_items),
        )
