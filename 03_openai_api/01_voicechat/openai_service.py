import base64                              # mp3 이진 데이터를 base64 문자열로 변환하기 위한 모듈
from dotenv import load_dotenv             # .env 파일에서 환경변수를 로드하는 모듈
from openai import OpenAI                  # OpenAI API를 사용하기 위한 클라이언트 클래스
import os                                  # 환경변수 접근 및 파일 삭제를 위한 표준 라이브러리

load_dotenv()                              # .env 파일을 읽어 환경변수로 등록
OPENAI_API_KEY = os.environ['openai_key']  # 환경변수에서 OpenAI API 키를 가져옴
client = OpenAI(api_key=OPENAI_API_KEY)    # OpenAI API 클라이언트 객체 생성

def stt(audio):                            # 음성 객체를 받아 STT 결과 텍스트를 반환하는 함수
    output_filepath = 'input.mp3'          # 임시로 저장할 mp3 파일 경로
    audio.export(output_filepath, format='mp3')  # 오디오 객체를 mp3 파일로 저장

    with open(output_filepath, 'rb') as f: # mp3 파일을 바이너리 읽기 모드로 열기
        transcription = client.audio.transcriptions.create(  # Whisper STT API 호출
            model='whisper-1',              # 음성 인식에 사용할 Whisper 모델
            file=f                           # 변환할 오디오 파일
        )

    os.remove(output_filepath)              # 임시로 생성한 mp3 파일 삭제
    return transcription.text               # 음성을 텍스트로 변환한 결과 반환

def ask_gpt(messages, model):               # 메시지 히스토리를 받아 GPT 응답을 생성하는 함수
    return client.chat.completions.create(  # ChatCompletion API 호출
        model=model,                        # 사용할 GPT 모델
        messages=messages,                  # 대화 히스토리 메시지
        top_p=1,                            # 토큰 샘플링 확률 분포 설정
        max_completion_tokens=4096          # 최대 응답 토큰 수 제한
    ).choices[0].message.content             # 생성된 응답 텍스트만 반환

def tts(response: str):                     # 텍스트를 받아 음성(mp3)으로 변환하는 함수
    filename = 'output.mp3'                 # 생성될 음성 파일 이름

    with client.audio.speech.with_streaming_response.create(  # TTS 스트리밍 응답 생성
        model='tts-1',                      # 사용할 TTS 모델
        voice='alloy',                      # 음성 스타일(보이스)
        input=response                     # 음성으로 변환할 텍스트
    ) as resp:
        resp.stream_to_file(filename)       # 스트리밍 결과를 mp3 파일로 저장

    with open(filename, 'rb') as f:          # 생성된 mp3 파일을 바이너리로 읽기
        data = f.read()                     # mp3 파일 전체 읽기
        b64_encoded = base64.b64encode(data).decode()  # mp3를 base64 문자열로 인코딩

    os.remove(filename)                     # 임시로 생성한 mp3 파일 삭제
    return b64_encoded                      # base64 인코딩된 음성 데이터 반환


def stt_file(uploaded_file) -> str:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=(uploaded_file.name, uploaded_file.getvalue())
    )
    return transcription.text

# 바이너리는 사람이 읽는 문자가 아니라, 0과 1 바이트로 된 원본 데이터
# mp3, jpg, png, pdf 같은 파일은 대부분 바이너리 파일이다.
# - 텍스트 형식 : 사람이 읽을 수 있는 글자 데이터 (예: "hello", json문자열, csv내용) 
# - 바이너리 형식 : 파일 자체의 원본 바이트(bytes) 데이터 (예 : mp3, jpg, png, pdf, zip 압축 데이터)
