# p2.py
import streamlit as st
from utils import makeMsg, openAiModelArg, geminiTxt, progressBar

st.set_page_config(page_title="여행 예산 견적서", page_icon="💵", layout="wide")
st.title("💵 여행 예산 견적서")

with st.sidebar:
    city = st.text_input("도시", value="도쿄")
    days = st.number_input("여행 일수", min_value=1, max_value=30, value=4, step=1)
    travel_type = st.selectbox("여행 타입", ["저예산", "보통", "프리미엄"], index=1)
    companion = st.selectbox("동행", ["혼자", "커플", "가족", "친구"], index=0)
    model_name = st.selectbox("OpenAI 모델", ["gpt-4o", "gpt-4o-mini"], index=0)

activities = st.multiselect(
    "활동 선택",
    ["도보 관광", "박물관/전시", "사진 촬영", "등산/야외", "해변", "맛집 투어", "쇼핑", "나이트라이프", "테마파크"],
    default=["도보 관광", "맛집 투어"]
)

if "budget_text" not in st.session_state:
    st.session_state.budget_text = ""

if st.button("예산 견적서 만들기"):
    progressBar("예산을 산출 중입니다...")

    # 핵심 요구:
    # - 도시가 속한 국가의 '현지 통화'로만 표기 (통화 기호/코드 함께)
    # - 일차별 분해 금지, '항목별 합계'만
    # - 표 형식: | 항목 | 합계(현지통화) | 메모 |
    # - 항목 제한: 교통, 숙박, 식사, 관광/입장료, 기타(유심/교통카드/팁/보험 등)
    # - 표 아래에 현지 통화 기준 '총합'을 굵게 표시
    # - 숫자는 천 단위 구분(콤마) 사용
    # - 불필요한 설명/서사 금지(표 + 총합만, 필요 최소 메모만)
    system = (
        "너는 여행 예산 플래너다. 사용자가 입력한 도시가 속한 국가의 '현지 통화'로만 금액을 제시한다. "
        "통화 기호와 코드(예: ¥/JPY, €/EUR, $/USD 등)를 함께 사용한다. "
        "반드시 '항목별 합계'만 제시하고 '일차별'로는 분해하지 않는다. "
        "표는 다음 열만 사용한다: | 항목 | 합계(현지통화) | 메모 | "
        "항목은 교통, 숙박, 식사, 관광/입장료, 기타(유심/교통카드/팁/보험 등)로 제한한다. "
        "표 아래에 현지 통화 기준 총합(굵게)을 한 줄로 표시한다. "
        "숫자에는 천 단위 콤마를 사용하고, 불필요한 설명 문단은 넣지 않는다."
    )
    user = (
        f"{city}로 {days}일 여행. 여행 타입은 {travel_type}, 동행은 {companion}. "
        f"활동: {', '.join(activities)}. "
        f"현지 통화로만 항목별 합계와 총합을 제시해줘."
    )

    msgs = makeMsg(system, user)
    body = openAiModelArg(model_name, msgs)
    st.session_state.budget_text = body

    tip = geminiTxt(
        "해당 예산을 기준으로 현지에서 비용을 아끼는 팁 2가지와, "
        "지출이 증가하기 쉬운 위험 요소 1가지를 간단히 한국어 한 문단으로 제안해줘:\n\n" + body
    )

    st.markdown("### 항목별 합계 (현지 통화)")
    st.write(body)
    st.markdown("### 참고 메모")
    st.info(tip)

if st.session_state.budget_text:
    st.download_button(
        "텍스트로 저장 (.txt)",
        data=st.session_state.budget_text,
        file_name=f"{city}_budget_totals_local.txt",
        mime="text/plain"
    )
