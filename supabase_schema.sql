-- Supabase 테이블 생성 SQL 스크립트
-- Supabase 대시보드의 SQL Editor에서 실행하세요.

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
    student_id TEXT NOT NULL,
    question_id INTEGER,
    question_type TEXT,
    question_text TEXT,
    user_answer TEXT,
    correct_answer TEXT,
    ai_explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_wrong_answers_student_id ON wrong_answers(student_id);
CREATE INDEX IF NOT EXISTS idx_wrong_answers_created_at ON wrong_answers(created_at);
CREATE INDEX IF NOT EXISTS idx_wrong_answers_question_id ON wrong_answers(question_id);

-- users 테이블 생성 (회원가입/로그인)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    student_id TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- users 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);

-- 기존 테이블이 있다면 컬럼 변경 (마이그레이션)
-- ALTER TABLE wrong_answers RENAME COLUMN student_name TO student_id;
-- DROP INDEX IF EXISTS idx_wrong_answers_student_name;
-- CREATE INDEX IF NOT EXISTS idx_wrong_answers_student_id ON wrong_answers(student_id);

-- RLS (Row Level Security) 정책 설정 (선택사항)
-- ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE wrong_answers ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 설정 (선택사항)
-- CREATE POLICY "Allow public read access" ON questions FOR SELECT USING (true);
-- CREATE POLICY "Allow public insert" ON wrong_answers FOR INSERT WITH CHECK (true);

