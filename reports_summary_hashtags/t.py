# reports.csv 파일의 귀국 보고서 내용을 기반으로 요약 컬럼 생성

import os
import openai
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime

# 1. .env 파일 로드 및 API 키 설정

if not os.path.exists(".env"):
    raise FileNotFoundError(".env 파일이 존재하지 않습니다.")
else:
    load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 2. CSV 파일 불러오기

file_path = "reports.csv"
df = pd.read_csv(file_path)

# 3. 사용할 컬럼만 추출하고 결측값 처리

text_columns = ['출국전', '공항도착후', '학교생활', '대학소개', '소감']
df[text_columns] = df[text_columns].fillna('')

def truncate_text(text, max_chars=1000):
    return text[:max_chars]

# 4. 요약 생성 함수

def generate_summary_location(row):
    출국전 = truncate_text(row['출국전'], 1000)
    공항도착후 = truncate_text(row['공항도착후'], 1000)
    학교생활 = truncate_text(row['학교생활'], 1000)
    대학소개 = truncate_text(row['대학소개'], 1000)
    소감 = truncate_text(row['소감'], 1000)


    prompt = f"""
    # Task
    다음은 교환학생 귀국 보고서의 내용입니다.

    출국전: {출국전}
    공항도착후: {공항도착후}
    학교생활: {학교생활}
    대학소개: {대학소개}
    소감: {소감}

    이 정보를 바탕으로 '위치 및 교통'에 관한 내용을 한두 문장으로 요약해 주세요.

    # 출력 형식
    summary_location: <내용>

    # 출력 예시
    'summary_location: 도심 캠퍼스에 위치해 있으며, 지하철역과 가까워 이동이 매우 편리했습니다.'

    # 제약 조건
    <내용>은 "~합니다."체로 작성

    """
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
        summary = content.split("summary_location:")[-1].strip()
        return summary
    except Exception as e:
        return f"[ERROR] {str(e)}"

# 5. 전체 데이터 요약 생성

summary_locations = []
for i, row in df.iterrows():
    print(f"Processing row {i+1}/{len(df)}...")
    summary = generate_summary_location(row)
    summary_locations.append(summary)
    time.sleep(1.2)  # Rate limit 방지용

# 6. 결과 저장

df['summary_location'] = summary_locations

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"reports_with_summary_{timestamp}.csv"

df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"n요약 완료! 결과가 '{output_path}'로 저장되었습니다.")
