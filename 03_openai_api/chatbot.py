import os                                                     # 환경변수
import streamlit as st                                        # UI
from openai import OpenAI                                     # OpenAI SDK
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Streamlit Chatbot", layout="centered")  # 페이지 설정
st.title("tts 챗기능")                              # 제목


api_key = os.getenv("openai_key")                         # 키 읽기
if not api_key:                                               # 키 없으면 안내
    st.error("OPENAI_API_KEY 환경변수를 설정하세요.")          # 에러 표시
    st.stop()                                                 # 중단

client = OpenAI(api_key=api_key)                              # 클라이언트 생성

if "messages" not in st.session_state:                        # 대화 기록 없으면
    st.session_state.messages = [                             # 초기 시스템 메시지
        {"role": "system", "content": "You are a helpful assistant."}  # 시스템
    ]

for m in st.session_state.messages[1:]:                       # 시스템 제외 출력
    with st.chat_message(m["role"]):                          # 역할별 말풍선
        st.markdown(m["content"])                             # 내용 표시

user_text = st.chat_input("메시지 입력...")                    # 입력창
if user_text:                                                 # 입력 들어오면
    st.session_state.messages.append({"role": "user", "content": user_text})  # 저장
    with st.chat_message("user"):                             # 유저 말풍선
        st.markdown(user_text)                                # 출력

    with st.chat_message("assistant"):                        # 어시스턴트 말풍선
        with st.spinner("생각 중..."):                         # 로딩
            resp = client.chat.completions.create(            # 응답 생성
                model="gpt-4o-mini",                           # 모델
                messages=st.session_state.messages,            # 대화 전체
                temperature=0.7                                # 다양성
            )
            answer = resp.choices[0].message.content          # 답 추출
            st.markdown(answer)                                # 출력

    st.session_state.messages.append({"role": "assistant", "content": answer})  # 저장
