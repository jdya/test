-- 기존 wrong_answers 테이블을 student_id로 마이그레이션하는 SQL
-- Supabase 대시보드의 SQL Editor에서 실행하세요.

-- 1. student_id 컬럼 추가
ALTER TABLE wrong_answers ADD COLUMN IF NOT EXISTS student_id TEXT;

-- 2. 기존 student_name 데이터를 student_id로 복사
UPDATE wrong_answers SET student_id = student_name WHERE student_id IS NULL;

-- 3. student_id를 NOT NULL로 변경
ALTER TABLE wrong_answers ALTER COLUMN student_id SET NOT NULL;

-- 4. 기존 인덱스 삭제 및 새 인덱스 생성
DROP INDEX IF EXISTS idx_wrong_answers_student_name;
CREATE INDEX IF NOT EXISTS idx_wrong_answers_student_id ON wrong_answers(student_id);

-- 5. (선택사항) student_name 컬럼 삭제
-- ALTER TABLE wrong_answers DROP COLUMN student_name;

