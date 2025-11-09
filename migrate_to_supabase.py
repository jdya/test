"""
Supabase로 문제 데이터를 마이그레이션하는 스크립트
"""
import json
from supabase import create_client, Client
import streamlit as st

# Supabase 클라이언트 초기화
def init_supabase():
    try:
        # Streamlit secrets에서 가져오기
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except:
        # 직접 설정 (스크립트 실행 시)
        import os
        from dotenv import load_dotenv
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if supabase_url and supabase_key:
            return create_client(supabase_url, supabase_key)
        return None

def create_tables(supabase: Client):
    """Supabase에 테이블 생성 SQL (Supabase 대시보드에서 직접 실행 필요)"""
    sql = """
    -- questions 테이블 생성
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        type TEXT NOT NULL,
        question TEXT NOT NULL,
        sentence TEXT,
        korean TEXT,
        options JSONB,
        correct_answer TEXT NOT NULL,
        explanation TEXT,
        example TEXT,
        conversation TEXT,
        words JSONB,
        sentences JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- wrong_answers 테이블 생성
    CREATE TABLE IF NOT EXISTS wrong_answers (
        id SERIAL PRIMARY KEY,
        student_name TEXT NOT NULL,
        question_id INTEGER,
        question_type TEXT,
        question_text TEXT,
        user_answer TEXT,
        correct_answer TEXT,
        ai_explanation TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- 인덱스 생성
    CREATE INDEX IF NOT EXISTS idx_wrong_answers_student_name ON wrong_answers(student_name);
    CREATE INDEX IF NOT EXISTS idx_wrong_answers_created_at ON wrong_answers(created_at);
    """
    print("SQL 스크립트:")
    print(sql)
    print("\n위 SQL을 Supabase 대시보드의 SQL Editor에서 실행하세요.")

def check_table_exists(supabase: Client, table_name: str):
    """테이블이 존재하는지 확인"""
    try:
        supabase.table(table_name).select('*').limit(1).execute()
        return True
    except Exception as e:
        error_msg = str(e)
        if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
            return False
        # 다른 오류는 테이블이 비어있을 수도 있으므로 True 반환
        return True

def migrate_questions(supabase: Client):
    """JSON 파일의 문제를 Supabase로 마이그레이션"""
    # 테이블 존재 확인
    if not check_table_exists(supabase, 'questions'):
        print("\n❌ 'questions' 테이블이 존재하지 않습니다!")
        print("먼저 Supabase 대시보드에서 'supabase_schema.sql' 파일의 SQL을 실행하세요.")
        print("또는 Supabase 대시보드 > SQL Editor에서 다음 SQL을 실행하세요:\n")
        print("=" * 50)
        with open('supabase_schema.sql', 'r', encoding='utf-8') as f:
            print(f.read())
        print("=" * 50)
        return
    
    # JSON 파일 읽기
    with open('questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Supabase에 삽입
    migrated = 0
    errors = 0
    for q in questions:
        try:
            data = {
                'id': q.get('id'),
                'type': q.get('type'),
                'question': q.get('question'),
                'sentence': q.get('sentence', ''),
                'korean': q.get('korean', ''),
                'options': q.get('options', []),
                'correct_answer': str(q.get('correct_answer', '')),
                'explanation': q.get('explanation', ''),
                'example': q.get('example', ''),
                'conversation': q.get('conversation', ''),
                'words': q.get('words', []),
                'sentences': q.get('sentences', [])
            }
            
            # 이미 존재하는지 확인
            try:
                existing = supabase.table('questions').select('id').eq('id', q.get('id')).execute()
                if existing.data:
                    # 업데이트
                    supabase.table('questions').update(data).eq('id', q.get('id')).execute()
                    print(f"✓ 업데이트: 문제 {q.get('id')}")
                else:
                    # 삽입
                    supabase.table('questions').insert(data).execute()
                    print(f"✓ 삽입: 문제 {q.get('id')}")
                migrated += 1
            except Exception as e:
                errors += 1
                print(f"✗ 오류 (문제 {q.get('id')}): {e}")
        except Exception as e:
            errors += 1
            print(f"✗ 오류 (문제 {q.get('id')}): {e}")
    
    print(f"\n✅ 총 {migrated}개 문제 마이그레이션 완료!")
    if errors > 0:
        print(f"⚠️  {errors}개 문제에서 오류 발생")

if __name__ == "__main__":
    print("=" * 50)
    print("Supabase 마이그레이션 스크립트")
    print("=" * 50)
    
    supabase = init_supabase()
    if not supabase:
        print("\n❌ Supabase 연결 실패!")
        print("환경 변수 또는 .streamlit/secrets.toml 파일을 확인하세요.")
        print("\n필요한 설정:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        exit(1)
    
    print("\n✅ Supabase 연결 성공!")
    
    print("\n1. 테이블 생성 SQL 확인")
    print("-" * 50)
    create_tables(supabase)
    
    print("\n2. 문제 데이터 마이그레이션 시작...")
    print("-" * 50)
    migrate_questions(supabase)
    
    print("\n" + "=" * 50)
    print("완료!")
    print("=" * 50)

