# 설정 가이드

## Supabase 테이블 생성

Supabase를 사용하려면 먼저 테이블을 생성해야 합니다.

### 방법 1: Supabase 대시보드에서 SQL 실행

1. Supabase 대시보드 접속
2. 왼쪽 메뉴에서 **SQL Editor** 클릭
3. **New Query** 클릭
4. `supabase_schema.sql` 파일의 내용을 복사하여 붙여넣기
5. **Run** 버튼 클릭

### 방법 2: 마이그레이션 스크립트 실행

```bash
python migrate_to_supabase.py
```

스크립트가 테이블이 없음을 감지하면 SQL을 출력하므로, 그 SQL을 Supabase 대시보드에서 실행하면 됩니다.

## 문제 데이터 마이그레이션

테이블을 생성한 후, 문제 데이터를 Supabase로 마이그레이션할 수 있습니다:

```bash
python migrate_to_supabase.py
```

## Supabase 없이 사용하기

Supabase 테이블이 없어도 앱은 정상적으로 작동합니다:
- 문제 데이터는 `questions.json` 파일에서 로드됩니다
- 틀린 문제 기록은 Supabase에 저장되지 않지만, 앱은 계속 작동합니다
- 통계 기능은 Supabase가 없으면 사용할 수 없습니다

## 오류 해결

### "Could not find the table 'public.questions'" 오류

이 오류는 Supabase 테이블이 생성되지 않았을 때 발생합니다.

**해결 방법:**
1. `supabase_schema.sql` 파일의 SQL을 Supabase 대시보드에서 실행
2. 또는 Supabase 없이 JSON 파일로 사용 (앱은 정상 작동)

### 마이그레이션 스크립트 오류

마이그레이션 스크립트를 실행할 때 테이블이 없다는 오류가 나오면:
1. 먼저 `supabase_schema.sql`을 Supabase 대시보드에서 실행
2. 그 다음 마이그레이션 스크립트 실행

