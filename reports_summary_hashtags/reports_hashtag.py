# reports.csv 파일의 귀국 보고서 내용을 기반으로 요약 컬럼 생성
import os
import openai
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime
import re

# 1. .env 파일 로드 및 API 키 설정
if not os.path.exists(".env"):
    raise FileNotFoundError(".env 파일이 존재하지 않습니다.")
else:
    load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 2. CSV 파일 불러오기
file_path = "reports_with_summary_20250509_235933.csv"
df = pd.read_csv(file_path)

# 3. 사용할 컬럼만 추출하고 결측값 처리
text_columns = ['summary_location', 'summary_weather', 'summary_academic', 'summary_safety']
df[text_columns] = df[text_columns].fillna('')

def truncate_text(text, max_chars=1000):
    return text[:max_chars]

# 4. 공통 요약 생성 함수
def generate_hsahtag(row):
    summary_location = truncate_text(row['summary_location'])
    summary_weather = truncate_text(row['summary_weather'])
    summary_academic = truncate_text(row['summary_academic'])
    summary_safety = truncate_text(row['summary_safety'])

    prompt = f"""
[Task]
    다음은 교환학생 귀국 보고서의 내용입니다.

    위치 및 교통: {summary_location}
    날씨: {summary_weather}
    학교시설 및 학업: {summary_academic}
    생활환경 및 안전: {summary_safety}

    이 정보를 바탕으로 학교의 특징을 가장 잘 나타내는 해시태그를 3개 작성하세요.

[출력 형식]
    #내용1 #내용2 #내용3

[출력 예시 1]
    #다운타운근접 #겨울혹한주의 #지하철역캠퍼스내

[출력 예시 2]
    #야간외출자제필요 #온화한날씨 #관광지와가까움

[출력 예시 3]
    #뚜렷한사계절 #치안좋음 #도심속캠퍼스


"""

    if len(prompt) > 10000:
        return f"[SKIPPED: Prompt too long]"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes student exchange program reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        content = response['choices'][0]['message']['content']
        # 해시태그 패턴만 추출 (예: "#내용1 #내용2 #내용3")
        match = re.search(r'#\S+(?:\s+#\S+){2}', content)
        if match:
            return match.group(0).strip()
        else:
            return f"[FORMAT ERROR] {content.strip()}"  # 실패한 경우 원문도 확인용으로 남김

    except Exception as e:
        return f"[ERROR] {str(e)}"

# 5. 전체 데이터 요약 생성
hashtag_list = []
for i, row in df.iterrows():
    print(f"Processing row {i+1}/{len(df)}...")
    hashtag = generate_hsahtag(row)
    hashtag_list.append(hashtag)
    time.sleep(1.2)  # Rate limit 방지용

# 6. 결과 저장
df['hashtag'] = hashtag_list
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"reports_with_hashtag_{timestamp}.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n요약 완료! 결과가 '{output_path}'로 저장되었습니다.")
