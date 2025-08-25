import streamlit as st
from utils import makeMsg, openAiModelArg, geminiTxt, progressBar

st.set_page_config(page_title="여행일정 생성기", page_icon="🗓", layout="wide")

st.title("🗓 여행일정 생성기")

with st.sidebar:
    city = st.text_input("도시", value="도쿄")
    days = st.number_input("여행 일수", min_value=1, max_value=14, value=3, step=1)
    model_name = st.selectbox("OpenAI 모델", ["gpt-4o", "gpt-4o-mini"], index=0)

st.markdown("#### 특이사항 (선택)")
ask = st.text_area("예: 미슐랭, 애니 성지, 저예산, 비건 식당 등", value="")

if st.button("✍️ 일정 만들기"):
    progressBar("여행 일정을 생성 중입니다...")

    system = (
        "너는 여행 플래너다. 비용/동선/시간을 고려해서 현실적인 일정표를 한국어로 상당히 구체적으로 작성한다. "
        "각 일자별로 오전/오후/저녁 구분, 이동수단/예상시간/간단한 팁을 포함하라."
    )
    user = f"{city}로 {days}일 여행 일정을 만들어줘. {ask}" if ask else f"{city}로 {days}일 여행 일정을 만들어줘."
    msgs = makeMsg(system, user)

    try:
        plan = openAiModelArg(model_name, msgs)
        st.success("일정 생성 완료!")
        st.markdown("### 결과")
        st.write(plan)

        st.markdown("### 💡 핵심 한 줄 요약")
        tip = geminiTxt(f"아래 일정을 1~2줄로 요약해줘.\n\n{plan}")
        st.info(tip)
    except Exception as e:
        st.error(f"생성 실패: {e}")
