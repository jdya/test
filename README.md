# 정유한의 시험 100점을 향한 여정 🎯

영어 문법 문제를 풀고 AI가 맞춤 해설을 제공하는 학습 플랫폼입니다.

## 주요 기능

- 🔐 **로그인 시스템**: 교사용 간편 암호로 로그인
- 📚 **10문제 랜덤 출제**: 50문제 중 10문제를 랜덤으로 선택
- 🤖 **AI 맞춤 해설**: DeepSeek AI가 틀린 문제에 대해 스트리밍 방식으로 해설 제공
- 💾 **학습 기록 저장**: 틀린 문제를 Supabase에 자동 저장
- 📊 **통계 및 분석**: 사용자별 학습 통계 및 AI 분석 제공
- 📈 **지난 기록 분석**: AI가 학습자의 약점과 개선 방향을 분석

## 설치 및 실행

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Supabase 설정

1. Supabase 프로젝트 생성
2. `supabase_schema.sql` 파일의 SQL을 Supabase 대시보드의 SQL Editor에서 실행
3. `.streamlit/secrets.toml` 파일에 Supabase 정보 입력

### 3. DeepSeek API 설정

1. DeepSeek API 키 발급
2. `.streamlit/secrets.toml` 파일에 API 키 입력

### 4. 문제 데이터 마이그레이션 (선택사항)

Supabase에 문제 데이터를 저장하려면:

```bash
python migrate_to_supabase.py
```

또는 Supabase 대시보드에서 직접 데이터를 입력할 수 있습니다.

### 5. 앱 실행

```bash
streamlit run app.py
```

## 설정 파일

### `.streamlit/secrets.toml`

```toml
# DeepSeek API 키
DEEPSEEK_API_KEY = "your-api-key"

# Supabase 연결 정보
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"

# 교사용 간편 암호
TEACHER_PASSWORD = "your-password"
```

## 데이터베이스 구조

### questions 테이블
- `id`: 문제 ID (Primary Key)
- `type`: 문제 유형 (multiple_choice, rearrange, sentence_combination 등)
- `question`: 문제 텍스트
- `sentence`: 문장
- `korean`: 한국어 번역
- `options`: 선택지 (JSONB)
- `correct_answer`: 정답
- `explanation`: 기본 해설
- 기타 필드...

### wrong_answers 테이블
- `id`: 레코드 ID (Primary Key, Auto Increment)
- `student_name`: 학생 이름
- `question_id`: 문제 ID
- `question_type`: 문제 유형
- `question_text`: 문제 텍스트
- `user_answer`: 사용자 답변
- `correct_answer`: 정답
- `ai_explanation`: AI 해설
- `created_at`: 생성 시간

## 사용 방법

1. **로그인**: 이름과 교사용 간편 암호를 입력하여 로그인
2. **문제 풀기**: 10문제가 랜덤으로 출제됩니다
3. **해설 확인**: 틀린 문제는 AI가 맞춤 해설을 제공합니다
4. **통계 확인**: 사이드바에서 통계를 확인하고 AI 분석을 받을 수 있습니다

## 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **AI**: DeepSeek API

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.
