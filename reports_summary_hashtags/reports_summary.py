# # reports.csv 파일의 귀국 보고서 내용을 기반으로 요약 컬럼 생성
# import os
# import openai
# import pandas as pd
# from dotenv import load_dotenv
# import time
# from datetime import datetime

# # 1. .env 파일 로드 및 API 키 설정
# if not os.path.exists(".env"):
#     raise FileNotFoundError(".env 파일이 존재하지 않습니다.")
# else:
#     load_dotenv()
# openai.api_key = os.environ.get("OPENAI_API_KEY")

# # 2. CSV 파일 불러오기
# file_path = "reports_cleaned.csv"
# df = pd.read_csv(file_path)


# # 3. 사용할 컬럼만 추출하고 결측값 처리
# text_columns = ['출국전', '공항도착후', '학교생활', '대학소개', '소감']
# df[text_columns] = df[text_columns].fillna('')

# def strip_code_block(text: str) -> str:
#     # ```로 감싸진 블록 제거
#     if text.startswith("```") and text.endswith("```"):
#         return "\n".join(text.strip("`").splitlines()[1:-1]).strip()
#     return text.strip("`").strip()


# def truncate_text(text, max_chars=1000):
#     return text[:max_chars]

# # 4. 공통 요약 생성 함수
# def generate_summary(row, topic: str, label: str, example: str):
#     출국전 = truncate_text(row['출국전'])
#     공항도착후 = truncate_text(row['공항도착후'])
#     학교생활 = truncate_text(row['학교생활'])
#     대학소개 = truncate_text(row['대학소개'])
#     소감 = truncate_text(row['소감'])

#     prompt = f"""
# # Task
# 다음은 교환학생 귀국 보고서의 내용입니다.

# 출국전: {출국전}
# 공항도착후: {공항도착후}
# 학교생활: {학교생활}
# 대학소개: {대학소개}
# 소감: {소감}

# 이 정보를 바탕으로 '{topic}'에 관한 내용을 한두 문장으로 요약해 주세요.

# # 출력 형식
# {label}: <내용>

# # 출력 예시
# {label}: {example}

# # 제약 조건
# - <내용>은 '~합니다.' 체로 작성해 주세요.
# """

#     # if len(prompt) > 10000:
#     #     return f"[SKIPPED: Prompt too long]"

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an assistant that summarizes student exchange program reports."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=250,
#             temperature=0.7
#         )
#         content = response['choices'][0]['message']['content']
#         summary_raw = content.split(f"{label}:")[-1].strip()
#         summary_clean = strip_code_block(summary_raw)
#         print(summary_clean)
#         return summary_clean

#     except Exception as e:
#         print(f"[ERROR] {str(e)}")
#         return ""

# # 5. 전체 데이터 요약 생성
# summary_location_list = []
# summary_weather_list = []
# summary_academic_list = []
# summary_safety_list = []

# for i, row in df.iterrows():
#     print(f"Processing row {i+1}/{len(df)}...")

#     summary_location = generate_summary(
#         row,
#         topic="위치 및 교통",
#         label="summary_location",
#         example="도심 캠퍼스에 위치해 있으며, 지하철역과 가까워 이동이 매우 편리합니다."
#     )

#     summary_weather = generate_summary(
#         row,
#         topic="날씨",
#         label="summary_weather",
#         example="겨울이 매우 추운 지역으로, 방한 준비가 철저히 필요합니다."
#     )

#     summary_academic = generate_summary(
#         row,
#         topic="학교시설 및 학업",
#         label="summary_academic",
#         example="시설이 잘 갖춰져 있고, 수업 난이도는 전반적으로 적절했습니다."
#     )

#     summary_safety = generate_summary(
#         row,
#         topic="생활환경 및 안전",
#         label="summary_safety",
#         example="야간에도 비교적 안전한 분위기로 생활이 안정적이었습니다."
#     )

#     summary_location_list.append(summary_location)
#     summary_weather_list.append(summary_weather)
#     summary_academic_list.append(summary_academic)
#     summary_safety_list.append(summary_safety)

#     time.sleep(1.2)  # Rate limit 방지

# # 6. 결과 저장
# df['summary_location'] = summary_location_list
# df['summary_weather'] = summary_weather_list
# df['summary_academic'] = summary_academic_list
# df['summary_safety'] = summary_safety_list

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# output_path = f"reports_with_summary_{timestamp}.csv"
# df.to_csv(output_path, index=False, encoding="utf-8-sig")

# print(f"\n요약 완료! 결과가 '{output_path}'로 저장되었습니다.")
