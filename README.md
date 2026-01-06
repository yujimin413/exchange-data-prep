# ✈️ exchange-data-prep

> **숭실대 교환학생 정보공유 서비스 [교환학슝] 데이터 전처리 파이프라인**

본 리포지토리는 숭실대학교 교환학생 정보 공유 서비스인 **교환학슝**에 사용되는 파견교 정보와 귀국 보고서 데이터를 정제하고 가공하는 파이썬 스크립트 모음입니다.  
복잡한 엑셀 데이터를 표준화하고, OpenAI API를 활용하여 방대한 학생 후기를 요약 및 해시태그화하는 로직을 포함합니다.

---

## 🛠️ 주요 기능

### 1\. 파견교 정보 데이터 정제 (`School Info Cleaning`)
<img src="https://github.com/user-attachments/assets/4a8d38bd-1629-487d-9ac5-a2211674e21e" width="100%">

학교 측에서 제공하는 Raw Excel 데이터를 서비스 DB에 적재 가능한 형태로 가공합니다.

  * **멀티 헤더 및 공백 처리:** 불규칙한 엑셀 헤더와 데이터의 공백/개행 문자를 정리합니다.
  * **데이터 파싱 및 정규화:**
      * **GPA:** 다양한 표기 방식(4.5만점 환산, 텍스트 혼용 등)을 표준화합니다.
      * **어학 성적:** TOEFL, IELTS, 유럽 언어 기준(CEFR) 등 복잡한 어학 자격 요건을 정규표현식(Regex)으로 분리 및 정제합니다.
      * **전공 분류:** 영어 강의 목록 텍스트를 분석하여 `경영/경제`, `공학/기술` 등 표준화된 전공 카테고리로 매핑합니다.
      * **언어권 추출:** 지원 자격 텍스트를 분석하여 해당 국가/학교의 주 언어권을 자동 추출합니다.


### 2\. 귀국 보고서 AI 요약 (`AI Summarization`)
<img src="https://github.com/user-attachments/assets/aa2efe8b-17de-446e-9a94-9a4377282b60" width="100%">

학생들이 작성한 장문의 귀국 보고서를 OpenAI GPT-3.5 API를 활용하여 주제별로 요약합니다.

  * **4대 카테고리 요약:** `위치 및 교통`, `날씨`, `학교시설 및 학업`, `생활환경 및 안전` 항목으로 내용을 구조화하여 요약합니다.
  * **어조 통일:** 요약된 문장을 "\~합니다" 체로 통일하여 서비스의 일관성을 유지합니다.


### 3\. 학교별 해시태그 생성 (`Hashtag Generation`)
<img src="https://github.com/user-attachments/assets/2b4e305b-bfab-435f-be38-2ea7e9778531" width="100%">

요약된 보고서 데이터를 바탕으로 학교의 특징을 가장 잘 나타내는 \*\*키워드 해시태그(3개)\*\*를 생성합니다.

  * *Ex) \#다운타운근접 \#겨울혹한주의 \#지하철역캠퍼스내*

---

## 🚀 시작하기 (Getting Started)

### 1\. 사전 요구 사항 (Prerequisites)

  * Python 3.10 이상
  * OpenAI API Key

### 2\. 설치 (Installation)

```bash
# 리포지토리 클론
git clone https://github.com/your-username/exchange-data-prep.git

# 패키지 설치
pip install pandas numpy openai python-dotenv openpyxl
```

### 3\. 환경 변수 설정 (.env)

OpenAI API 사용을 위해 프로젝트 루트 경로에 `.env` 파일을 생성하고 키를 입력하세요.

```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 4\. 사용 방법 (Usage)

**Step 1: 파견교 데이터 정제**

```bash
# Jupyter Notebook 실행 후 school_info_0306.xlsx 파일 로드 및 셀 실행
# 결과물: school_info_refined_MMDD.csv
```

**Step 2: 귀국 보고서 요약 생성**

```bash
python generate_summary.py
# 입력: reports.csv
# 출력: reports_with_summary_YYYYMMDD.csv
```

**Step 3: 해시태그 생성**

```bash
python generate_hashtags.py
# 입력: reports_with_summary_YYYYMMDD.csv
# 출력: reports_with_hashtag_YYYYMMDD.csv
```

## 🛠️ 기술 스택 (Tech Stack)

  * **Language:** Python
  * **Data Processing:** Pandas, NumPy, Regular Expressions (Regex)
  * **AI/LLM:** OpenAI API (GPT-3.5 Turbo)
  * **Environment:** Dotenv
