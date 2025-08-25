# app.py
import streamlit as st

# 페이지 등록 (너가 보여준 st.Page / st.navigation 패턴)
pg_main = st.Page("main.py", title="메인", icon="🏠")
pg_p1   = st.Page("p1.py",   title="여행일정 생성기", icon="🗓")
pg_p2   = st.Page("p2.py",   title="여행 예산 견적서", icon="💵")
pg_p3   = st.Page("p3.py",   title="짐 꾸리기 체크리스트", icon="🧳")
pg_p4 = st.Page("p4.py", title="여행 서류 정리 도우미", icon="🗂")


nav = st.navigation([pg_main, pg_p1, pg_p2,pg_p3,pg_p4])
nav.run()
