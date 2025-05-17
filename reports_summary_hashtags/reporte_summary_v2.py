# summary_ 컬럼 생성 스크립트 최종
import os
import openai
import pandas as pd
from dotenv import load_dotenv
import time
from datetime import datetime
from fuzzywuzzy import process
import re

# 1. 환경 변수 로드
if not os.path.exists(".env"):
    raise FileNotFoundError(".env 파일이 존재하지 않습니다.")
else:
    load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# 2. 파일 불러오기
reports_df = pd.read_csv("reports_cleaned.csv")
school_df = pd.read_csv("school_info_refined.csv")

# 3. 전처리
text_columns = ['출국전', '공항도착후', '학교생활', '대학소개', '소감']
reports_df[text_columns] = reports_df[text_columns].fillna('')
# reports_df['대학명(영문)'] = reports_df['대학명(영문)'].fillna('').str.strip()
reports_df['대학명(영문)'] = reports_df['대학명(영문)'].fillna('').str.strip()
school_df['대학명(영문)'] = school_df['대학명(영문)'].fillna('').str.strip()

import re

def clean_and_strip_summary(text: str) -> str:
    # 1. 코드 블록 제거 (```로 감싸진 경우)
    if text.startswith("```") and text.endswith("```"):
        text = "\n".join(text.strip("`").splitlines()[1:-1]).strip()
    else:
        text = text.strip("`").strip()

    # 2. 마크다운 기호 제거
    text = text.replace("**", "").strip()

    # 3. 중복된 '~합니다.' 제거
    text = re.sub(r'(~합니다\.)(?=.*~합니다\.)', '', text)

    # 4. '~합니다.~합니다.' 같이 중복되는 종결어미 하나로 통일
    text = re.sub(r'(~합니다\.)(\s*/\s*)?(~합니다\.)+', r'\1', text)

    return text.strip()



def truncate_text(text, max_chars=1000):
    return text[:max_chars]

def generate_summary(row, topic: str, label: str, example: str):
    출국전 = truncate_text(row['출국전'])
    공항도착후 = truncate_text(row['공항도착후'])
    학교생활 = truncate_text(row['학교생활'])
    대학소개 = truncate_text(row['대학소개'])
    소감 = truncate_text(row['소감'])

    prompt = f"""
# Task
다음은 교환학생 귀국 보고서의 내용입니다.

출국전: {출국전}
공항도착후: {공항도착후}
학교생활: {학교생활}
대학소개: {대학소개}
소감: {소감}

이 정보를 바탕으로 '{topic}'에 관한 내용을 한두 문장으로 요약해 주세요.

# 출력 형식
{label}: <내용>

# 출력 예시
{label}: {example}

# 제약 조건
- <내용>은 '~합니다.' 체로 작성하되, 마크다운 기호(**, *, ```)는 포함하지 마세요.
- 중복 문장 없이 간결하게 작성해 주세요.

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
        summary_raw = content.split(f"{label}:")[-1].strip()
        summary_clean = clean_and_strip_summary(summary_raw)
        print(summary_clean)
        return summary_clean
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return ""

# 4. 대학별 요약 누적 딕셔너리 생성
summary_dict = {}

for i, row in reports_df.iterrows():
    uni_name = row['대학명(영문)']
    if not uni_name:
        continue

    print(f"Processing report for row {i+1}/{len(reports_df)} : {uni_name}...")

    summaries = {
        "summary_location": generate_summary(
            row,
            topic="위치 및 교통",
            label="summary_location",
            example="도심 캠퍼스에 위치해 있으며, 지하철역과 가까워 이동이 매우 편리합니다."
        ),
        "summary_weather": generate_summary(
            row,
            topic="날씨",
            label="summary_weather",
            example="겨울이 매우 추운 지역으로, 방한 준비가 철저히 필요합니다."
        ),
        "summary_academic": generate_summary(
            row,
            topic="학교시설 및 학업",
            label="summary_academic",
            example="시설이 잘 갖춰져 있고, 수업 난이도는 전반적으로 적절했습니다."
        ),
        "summary_safety": generate_summary(
            row,
            topic="생활환경 및 안전",
            label="summary_safety",
            example="야간에도 비교적 안전한 분위기로 생활이 안정적이었습니다."
        ),
    }

    # 해당 대학명 기준으로 요약 누적
    if uni_name not in summary_dict:
        summary_dict[uni_name] = {k: [] for k in summaries}
    for k, v in summaries.items():
        if v:
            summary_dict[uni_name][k].append(v)

    time.sleep(1.2)  # Rate limit 방지

def refine_summary(combined_text: str, topic: str) -> str:
    """
    여러 개의 요약을 하나로 자연스럽게 통합하는 함수
    """
    prompt = f"""
# Task
다음은 학생들이 작성한 '{topic}'에 대한 요약 내용입니다.
여러 문장이 합쳐져 중복되거나 어색할 수 있으니, 아래 내용을 한두 문장으로 자연스럽고 간결하게 다시 요약해 주세요.

# 입력
{combined_text}

# 출력 형식
- '~합니다.' 체의 한두 문장으로 간결하게 정리
- 중복되지 않게 하나의 문장으로 매끄럽게 통합
- 마크다운 기호, **, *, ``` 등 사용 금지
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites combined summaries to be clean and non-redundant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5,
        )
        refined_text = response['choices'][0]['message']['content'].strip()
        refined_clean = clean_and_strip_summary(refined_text)
        print(refined_clean)
        return refined_clean

    except Exception as e:
        print(f"[ERROR: refine_summary] {e}")
        return combined_text.strip()


# 5. school_info_refined.csv에 요약 내용 병합
unmatched_universities = set()

# 5. school_info_refined.csv에 요약 내용 병합
for idx, row in school_df.iterrows():
    uni_name = row['대학명(영문)']
    if uni_name in summary_dict:
        for key in ['summary_location', 'summary_weather', 'summary_academic', 'summary_safety']:
            combined_text = ' / '.join(summary_dict[uni_name][key])
            topic_map = {
                "summary_location": "위치 및 교통",
                "summary_weather": "날씨",
                "summary_academic": "학교시설 및 학업",
                "summary_safety": "생활환경 및 안전"
            }
            topic = topic_map[key]
            final_summary = refine_summary(combined_text, topic)
            school_df.loc[idx, key] = final_summary
    else:
        unmatched_universities.add(uni_name)

# 5-1. 매칭 실패한 대학 이름 출력
all_report_unis = set(summary_dict.keys())
matched_unis = set(school_df['대학명(영문)'])  # school df 기준
unmatched_in_reports = all_report_unis - matched_unis

if unmatched_in_reports:
    print("\n[매칭 실패: reports.csv의 '대학명(영문)' 중 school_info_refined.csv에 없는 항목]")
    for name in sorted(unmatched_in_reports):
        print(f"- {name}")
else:
    print("\n모든 대학명이 정상적으로 매칭되었습니다.")

# 6. 결과 저장
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"school_info_refined_with_summary_{timestamp}.csv"
school_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n요약 병합 완료! 결과가 '{output_path}'로 저장되었습니다.")