import streamlit as st                                  # Streamlit UI 프레임워크
from audiorecorder import audiorecorder                 # 마이크 음성 녹음 컴포넌트
from openai_service import stt, ask_gpt, tts             # STT / GPT 질의 / TTS 함수들

def main():                                              # 메인 함수
    st.set_page_config(                                  # 페이지 기본 설정
        page_title='Voice Chatbot',                      # 브라우저 탭 제목
        page_icon='🎤',                                  # 페이지 아이콘
        layout='wide'                                    # 와이드 레이아웃
    )
    st.header('🎤Voice Chatbot🎤')                        # 상단 헤더
    st.markdown('---')                                   # 구분선
    
    with st.expander("Voice Chatbot 프로그램 처리절차", expanded=False):  # 설명 접기 영역
        st.write("""                                     # 처리 절차 설명 텍스트
            1. 녹음하기 버튼을 눌러 질문을 녹음합니다.
            2. 녹음이 완료되면 Whisper로 음성을 텍스트로 변환합니다.
            3. 변환된 텍스트를 LLM에 전달합니다.
            4. 응답을 TTS로 음성 변환합니다.
            5. 질문/답변을 채팅 형식으로 출력합니다.
        """)
        
    system_prompt = '당신은 친절한 챗봇입니다. 사용자의 질문에 50단어 이내로 간결하게 답변해주세요'  # 시스템 프롬프트
    
    if 'messages' not in st.session_state:               # 세션에 메시지 기록이 없으면
        st.session_state['messages'] = [                 # 메시지 리스트 초기화
            {'role': 'system', 'content': system_prompt} # system 메시지 추가
        ]
        
    if 'check_reset' not in st.session_state:            # 초기화 플래그 없으면
        st.session_state['check_reset'] = False          # False로 초기화
        
    with st.sidebar:                                     # 사이드바 영역
        model = st.radio(                                # GPT 모델 선택 라디오 버튼
            label='GPT 모델',
            options=['gpt-4.1-mini', 'gpt-5-nano', 'gpt-5.2'],
            index=0
        )
        print(f'{model = }')                             # 선택된 모델 콘솔 출력
        
    if st.button(label='초기화'):                         # 초기화 버튼 클릭 시
        st.session_state['messages'] = [                 # 메시지 초기화
            {'role': 'system', 'content': system_prompt}
        ]
        st.session_state['check_reset'] = True           # 초기화 플래그 ON
        
    col1, col2 = st.columns(2)                            # 두 개 컬럼 생성
    
    with col1:                                           # 왼쪽 컬럼
        st.subheader('녹음하기')                          # 녹음 섹션 제목
        audio = audiorecorder()                           # 음성 녹음
        
        if (audio.duration_seconds > 0) and (not st.session_state['check_reset']):  # 녹음 완료 & 초기화 아님
            st.audio(audio.export().read())               # 녹음된 음성 재생
            
            query: str = stt(audio)                       # 음성을 텍스트로 변환
            print(f'{query = }')                          # 변환된 텍스트 출력
            
            st.session_state['messages'].append({         # 사용자 메시지 저장
                "role": 'user',
                "content": query
            })
            
            response: str = ask_gpt(                      # GPT에 질의
                st.session_state['messages'],
                model
            )
            print(f'{response = }')                       # GPT 응답 출력
            
            st.session_state['messages'].append({         # GPT 응답 저장
                'role': 'assistant',
                'content': response
            })
            
            base64_encoded_audio: str = tts(response)     # 응답을 음성으로 변환
            
            st.html(f'''                                  # 자동 재생 오디오 HTML
                <audio autoplay="true">
                    <source src="data:audio/mp3,{base64_encoded_audio}"/>
                </audio>
            ''')
        else:
            st.session_state['check_reset'] = False       # 초기화 플래그 해제
    
    with col2:                                           # 오른쪽 컬럼
        st.subheader('질문/답변')                         # 채팅 영역 제목
        
        if (audio.duration_seconds > 0) and (not st.session_state['check_reset']):  # 조건 확인
            for message in st.session_state['messages']:  # 모든 메시지 순회
                role = message['role']                    # 메시지 역할
                content = message['content']              # 메시지 내용
                
                if role == 'system':                      # system 메시지는 건너뜀
                    continue
                
                with st.chat_message(role):               # 채팅 UI 생성
                    st.write(content)                     # 메시지 출력
                    
                    
main()
