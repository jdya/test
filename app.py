import streamlit as st
import json
import random
from supabase import create_client, Client
from openai import OpenAI
import time
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="정유한의 시험 100점을 향한 여정",
    page_icon="🎯",
    layout="wide"
)

# 눈에 편한 색상 테마 적용
st.markdown("""
<style>
    /* 다크 모드 스타일 */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    .main .block-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .stError {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    .stInfo {
        background-color: #d1ecf1;
        border-color: #bee5eb;
        color: #0c5460;
    }
    
    .stWarning {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #34495e 0%, #2c3e50 100%);
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background-color: #3498db;
        width: 100%;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 5px;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* 라디오 버튼 스타일 */
    .stRadio>div {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Supabase 클라이언트 초기화
@st.cache_resource
def init_supabase():
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            return None
        
        # Supabase 클라이언트 생성 (proxy 인자 제거)
        from supabase import create_client, Client
        client = create_client(supabase_url, supabase_key)
        return client
    except KeyError:
        # secrets에 SUPABASE_URL이나 SUPABASE_KEY가 없는 경우
        return None
    except Exception as e:
        # 오류를 조용히 처리 (사용자에게는 경고만 표시)
        error_msg = str(e)
        # proxy 관련 오류는 무시하고 None 반환
        if 'proxy' in error_msg.lower() or 'unexpected keyword' in error_msg.lower():
            return None
        # 다른 오류는 로그만 남기고 None 반환
        return None

# DeepSeek API 클라이언트 초기화
@st.cache_resource
def init_deepseek():
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        
        if not api_key:
            return None
        
        # DeepSeek은 OpenAI 호환 API를 사용
        # Streamlit Cloud 환경에서 proxies 인자 문제 방지
        try:
            # OpenAI 클라이언트 초기화 시 proxies 인자 제거
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                timeout=60.0
            )
            # 간단한 테스트 호출로 연결 확인 (실제 API 호출은 하지 않음)
            return client
        except TypeError as e:
            # proxies 인자 관련 오류인 경우 다른 방식으로 시도
            error_msg = str(e)
            if 'proxies' in error_msg.lower() or 'unexpected keyword' in error_msg.lower():
                # httpx 클라이언트를 직접 생성하여 proxies 제거
                import httpx
                http_client = httpx.Client(timeout=60.0)
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1",
                    http_client=http_client
                )
                return client
            raise
    except KeyError:
        # secrets에 DEEPSEEK_API_KEY가 없는 경우
        return None
    except Exception as e:
        # 오류를 조용히 처리
        error_msg = str(e)
        # proxies 관련 오류는 무시하고 None 반환
        if 'proxies' in error_msg.lower() or 'unexpected keyword' in error_msg.lower():
            return None
        # 다른 오류도 조용히 처리
        return None

supabase = init_supabase()
deepseek_client = init_deepseek()

# 문제 데이터 로드 (Supabase에서 가져오거나 JSON에서 가져오기)
@st.cache_data
def load_questions():
    # 먼저 Supabase에서 시도
    if supabase:
        try:
            response = supabase.table('questions').select('*').execute()
            if response.data and len(response.data) > 0:
                return response.data
        except Exception as e:
            error_msg = str(e)
            # 테이블이 없는 경우에만 경고 표시
            if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
                # 조용히 JSON 파일로 전환 (첫 실행 시에만 경고)
                pass
            else:
                st.warning(f"Supabase에서 문제를 가져올 수 없습니다. JSON 파일을 사용합니다: {e}")
    
    # Supabase 실패 시 JSON 파일 사용
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)
            # JSON 데이터를 Supabase 형식에 맞게 변환
            formatted_questions = []
            for q in questions:
                formatted_q = {
                    'id': q.get('id'),
                    'type': q.get('type'),
                    'question': q.get('question'),
                    'sentence': q.get('sentence', ''),
                    'korean': q.get('korean', ''),
                    'options': json.dumps(q.get('options', []), ensure_ascii=False) if isinstance(q.get('options'), list) else q.get('options', ''),
                    'correct_answer': q.get('correct_answer'),
                    'explanation': q.get('explanation', ''),
                    'example': q.get('example', ''),
                    'conversation': q.get('conversation', ''),
                    'words': json.dumps(q.get('words', []), ensure_ascii=False) if isinstance(q.get('words'), list) else q.get('words', ''),
                    'sentences': json.dumps(q.get('sentences', []), ensure_ascii=False) if isinstance(q.get('sentences'), list) else q.get('sentences', ''),
                }
                formatted_questions.append(formatted_q)
            return formatted_questions
    except Exception as e:
        st.error(f"문제 데이터를 로드할 수 없습니다: {e}")
        return []

def parse_question(question):
    """Supabase에서 가져온 문제를 파싱"""
    if isinstance(question, dict):
        # options, words, sentences가 JSON 문자열인 경우 파싱
        # Supabase JSONB 필드는 이미 파이썬 객체로 변환될 수 있음
        if 'options' in question:
            if isinstance(question['options'], str):
                try:
                    question['options'] = json.loads(question['options'])
                except:
                    pass
            elif question['options'] is None:
                question['options'] = []
        
        if 'words' in question:
            if isinstance(question['words'], str):
                try:
                    question['words'] = json.loads(question['words'])
                except:
                    pass
            elif question['words'] is None:
                question['words'] = []
        
        if 'sentences' in question:
            if isinstance(question['sentences'], str):
                try:
                    question['sentences'] = json.loads(question['sentences'])
                except:
                    pass
            elif question['sentences'] is None:
                question['sentences'] = []
    return question

# 로그인 체크
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'student_id' not in st.session_state:
        st.session_state.student_id = None
    if 'student_name' not in st.session_state:
        st.session_state.student_name = None
    
    if not st.session_state.logged_in:
        return False
    return True

# 사용자 확인 (로그인)
def verify_user(student_id, password):
    if not supabase:
        return False, "Supabase 연결 오류"
    try:
        response = supabase.table('users').select('*').eq('student_id', student_id).eq('password', password).execute()
        if len(response.data) > 0:
            return True, "로그인 성공"
        else:
            return False, "아이디 또는 비밀번호가 올바르지 않습니다."
    except Exception as e:
        error_msg = str(e)
        # 테이블이 없는 경우
        if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
            return False, "users 테이블이 없습니다. Supabase 대시보드에서 supabase_schema.sql을 실행해주세요."
        return False, f"로그인 중 오류가 발생했습니다: {error_msg}"

# 사용자 등록 (회원가입)
def register_user(student_id, password):
    if not supabase:
        return False, "Supabase 연결 오류. Supabase를 설정해주세요."
    try:
        # 아이디 중복 체크
        existing = supabase.table('users').select('student_id').eq('student_id', student_id).execute()
        if existing.data:
            return False, "이미 존재하는 아이디입니다."
        
        # 회원가입
        data = {
            'student_id': student_id,
            'password': password
        }
        supabase.table('users').insert(data).execute()
        return True, "회원가입이 완료되었습니다!"
    except Exception as e:
        error_msg = str(e)
        # 테이블이 없는 경우
        if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
            return False, "users 테이블이 없습니다. Supabase 대시보드에서 supabase_schema.sql을 실행해주세요."
        return False, f"회원가입 중 오류가 발생했습니다: {e}"

# 로그인 페이지
def show_login():
    st.title("🎯 정유한의 시험 100점을 향한 여정")
    st.markdown("---")
    
    # 탭 선택
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("로그인")
            if not supabase:
                st.warning("⚠️ Supabase가 연결되지 않았습니다. 회원가입/로그인 기능을 사용하려면 Supabase를 설정해주세요.")
            
            student_id = st.text_input("아이디:", key="login_id", placeholder="아이디를 입력하세요")
            student_password = st.text_input("비밀번호:", type="password", key="login_password", placeholder="비밀번호를 입력하세요")
            
            if st.button("로그인", use_container_width=True, type="primary", key="login_button"):
                if not student_id:
                    st.error("아이디를 입력해주세요.")
                elif not student_password:
                    st.error("비밀번호를 입력해주세요.")
                elif not supabase:
                    st.error("Supabase 연결이 필요합니다.")
                else:
                    # 사용자 확인
                    with st.spinner("로그인 중..."):
                        success, message = verify_user(student_id, student_password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.student_id = student_id
                            st.session_state.student_name = student_id
                            # 세션 상태 초기화
                            if 'show_stats' in st.session_state:
                                del st.session_state.show_stats
                            if 'show_quiz' in st.session_state:
                                del st.session_state.show_quiz
                            if 'quiz_started' in st.session_state:
                                del st.session_state.quiz_started
                            st.rerun()
                        else:
                            st.error(message)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("회원가입")
            if not supabase:
                st.warning("⚠️ Supabase가 연결되지 않았습니다. 회원가입 기능을 사용하려면 Supabase를 설정해주세요.")
            
            new_student_id = st.text_input("아이디:", key="register_id", placeholder="아이디를 입력하세요")
            new_password = st.text_input("비밀번호:", type="password", key="register_password", placeholder="비밀번호를 입력하세요 (4자 이상)")
            confirm_password = st.text_input("비밀번호 확인:", type="password", key="register_confirm_password", placeholder="비밀번호를 다시 입력하세요")
            
            st.markdown("")  # 간격 추가
            
            if st.button("회원가입", use_container_width=True, type="primary", key="register_button"):
                if not new_student_id:
                    st.error("아이디를 입력해주세요.")
                elif not new_password:
                    st.error("비밀번호를 입력해주세요.")
                elif len(new_password) < 4:
                    st.error("비밀번호는 4자 이상이어야 합니다.")
                elif new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif not supabase:
                    st.error("Supabase 연결이 필요합니다.")
                else:
                    # 회원가입
                    success, message = register_user(new_student_id, new_password)
                    if success:
                        st.success(message)
                        st.info("로그인 탭에서 로그인해주세요.")
                    else:
                        st.error(message)

# 사용자 기록 조회
def get_user_records(student_id):
    if not supabase:
        return []
    try:
        response = supabase.table('wrong_answers').select('*').eq('student_id', student_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        error_msg = str(e)
        # 테이블이 없는 경우 조용히 빈 리스트 반환
        if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
            return []
        # 다른 오류는 경고 표시
        st.warning(f"기록을 가져올 수 없습니다: {e}")
        return []

# AI 분석 생성
def generate_ai_analysis(records):
    if not deepseek_client or not records:
        return "기록이 없어 분석할 수 없습니다."
    
    try:
        # 최근 10개 기록만 분석
        recent_records = records[:10]
        
        # 문제 유형별 오답 통계
        type_counts = {}
        for record in recent_records:
            q_type = record.get('question_type', 'unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        prompt = f"""다음은 학생의 영어 문법 문제 오답 기록입니다. 
학생의 약점과 개선 방향을 분석해주세요.

총 오답 수: {len(recent_records)}
문제 유형별 오답:
{json.dumps(type_counts, ensure_ascii=False, indent=2)}

최근 오답 기록:
{json.dumps(recent_records[:5], ensure_ascii=False, indent=2)}

학생에게 친근하고 격려하는 톤으로 다음을 포함하여 분석해주세요:
1. 전체적인 학습 상태 평가
2. 자주 틀리는 문제 유형
3. 개선이 필요한 부분
4. 학습 권장사항

한국어로 답변해주세요."""
        
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "당신은 친절하고 격려하는 영어 선생님입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {e}"

# 스트리밍 해설 생성
def generate_streaming_explanation(question, user_answer, correct_answer):
    if not deepseek_client:
        return None
    
    try:
        # 문제 정보 구성
        question_text = question.get('question', '')
        question_type = question.get('type', '')
        explanation = question.get('explanation', '')
        
        # 객관식 문제인 경우 인덱스를 실제 선택지 텍스트로 변환
        user_answer_text = str(user_answer)
        correct_answer_text = str(correct_answer)
        
        if question_type == 'multiple_choice':
            options = question.get('options', [])
            # 사용자 답변 변환
            try:
                user_index = int(user_answer)
                if 0 <= user_index < len(options):
                    user_answer_text = options[user_index]
            except:
                pass
            
            # 정답 변환
            try:
                correct_index = int(correct_answer)
                if 0 <= correct_index < len(options):
                    correct_answer_text = options[correct_index]
            except:
                pass
        
        # 문제 내용 추가
        problem_content = ""
        if question.get('sentence'):
            problem_content += f"문장: {question.get('sentence')}\n"
        if question.get('korean'):
            problem_content += f"한국어: {question.get('korean')}\n"
        if question.get('example'):
            problem_content += f"보기: {question.get('example')}\n"
        if question.get('conversation'):
            problem_content += f"대화:\n{question.get('conversation')}\n"
        if question_type == 'multiple_choice':
            options = question.get('options', [])
            if options:
                problem_content += f"선택지:\n"
                for i, opt in enumerate(options):
                    problem_content += f"  {i}: {opt}\n"
        
        prompt = f"""학생이 다음 문제를 틀렸습니다. 친절하고 이해하기 쉽게 해설을 해주세요.

문제: {question_text}
{problem_content}
문제 유형: {question_type}
학생의 답: {user_answer_text}
정답: {correct_answer_text}
기본 해설: {explanation}

학생이 왜 틀렸는지, 정답이 왜 정답인지, 비슷한 문제를 어떻게 접근해야 하는지 설명해주세요.
한국어로 친근하고 격려하는 톤으로 답변해주세요."""
        
        stream = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "당신은 친절하고 격려하는 영어 선생님입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=True
        )
        
        return stream
    except Exception as e:
        st.error(f"해설 생성 중 오류: {e}")
        return None

# 틀린 문제 저장
def save_wrong_answer(student_id, question, user_answer, correct_answer, ai_explanation=""):
    if not supabase:
        return False
    
    try:
        data = {
            'student_id': student_id,
            'question_id': question.get('id'),
            'question_type': question.get('type', ''),
            'question_text': question.get('question', ''),
            'user_answer': str(user_answer),
            'correct_answer': str(correct_answer),
            'ai_explanation': ai_explanation,
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('wrong_answers').insert(data).execute()
        return True
    except Exception as e:
        error_msg = str(e)
        # 테이블이 없는 경우 조용히 실패 (첫 실행 시)
        if 'PGRST205' in error_msg or 'Could not find the table' in error_msg:
            return False
        # 다른 오류는 경고 표시
        st.warning(f"기록 저장 중 오류: {e}")
        return False

# 통계 페이지
def show_statistics(student_id):
    st.title("📊 학습 통계")
    st.markdown("---")
    
    try:
        records = get_user_records(student_id)
        
        if not records:
            st.info("아직 기록이 없습니다. 문제를 풀어보세요!")
            return
        
        # 전체 통계
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 오답 수", len(records))
        with col2:
            # 최근 7일 오답 수
            try:
                recent_7days = [r for r in records if (datetime.now() - datetime.fromisoformat(r['created_at'].replace('Z', '+00:00'))).days < 7]
                st.metric("최근 7일 오답", len(recent_7days))
            except:
                st.metric("최근 7일 오답", 0)
        with col3:
            # 문제 유형별 통계
            type_counts = {}
            for r in records:
                q_type = r.get('question_type', 'unknown')
                type_counts[q_type] = type_counts.get(q_type, 0) + 1
            most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "없음"
            st.metric("가장 많이 틀린 유형", most_common_type)
        with col4:
            # 오늘 오답 수
            try:
                today = [r for r in records if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).date() == datetime.now().date()]
                st.metric("오늘 오답", len(today))
            except:
                st.metric("오늘 오답", 0)
        
        st.markdown("---")
        
        # 문제 유형별 차트
        st.subheader("문제 유형별 오답 분포")
        type_counts = {}
        for r in records:
            q_type = r.get('question_type', 'unknown')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        if type_counts:
            st.bar_chart(type_counts)
        
        # 최근 오답 기록
        st.subheader("최근 오답 기록")
        for i, record in enumerate(records[:10]):
            try:
                created_at = record.get('created_at', '')
                if created_at:
                    date_str = created_at[:10] if len(created_at) >= 10 else created_at
                else:
                    date_str = "날짜 없음"
                
                question_text = record.get('question_text', '')
                question_preview = question_text[:50] + "..." if len(question_text) > 50 else question_text
                
                with st.expander(f"문제 {i+1}: {question_preview} ({date_str})"):
                    st.write(f"**문제 유형:** {record.get('question_type', '')}")
                    st.write(f"**내 답:** {record.get('user_answer', '')}")
                    st.write(f"**정답:** {record.get('correct_answer', '')}")
                    if record.get('ai_explanation'):
                        st.write(f"**AI 해설:** {record.get('ai_explanation', '')}")
            except Exception as e:
                st.warning(f"기록 {i+1}을 표시하는 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"통계를 불러오는 중 오류가 발생했습니다: {e}")
        st.info("Supabase 연결을 확인하거나 잠시 후 다시 시도해주세요.")

# 메인 앱
def main():
    # 로그인 체크
    if not check_login():
        show_login()
        return
    
    student_id = st.session_state.student_id
    student_name = st.session_state.student_name
    
    # 사이드바
    with st.sidebar:
        st.title(f"👋 {student_name}님")
        st.markdown("---")
        
        if st.button("📊 통계 보기", use_container_width=True):
            st.session_state.show_stats = True
            st.session_state.show_quiz = False
            st.rerun()
        
        if st.button("📝 문제 풀기", use_container_width=True):
            st.session_state.show_stats = False
            st.session_state.show_quiz = True
            st.rerun()
        
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.session_state.student_name = None
            st.session_state.show_stats = False
            st.session_state.show_quiz = False
            st.session_state.quiz_started = False
            st.rerun()
        
        st.markdown("---")
        
        # 지난 기록 및 AI 분석 (캐싱하여 성능 개선)
        analysis_key = f'ai_analysis_{student_id}'
        if analysis_key not in st.session_state:
            records = get_user_records(student_id)
            if records:
                st.subheader("📈 지난 기록 분석")
                with st.spinner("AI가 분석 중..."):
                    try:
                        analysis = generate_ai_analysis(records)
                        st.session_state[analysis_key] = analysis
                        st.info(analysis)
                    except Exception as e:
                        st.warning(f"AI 분석 중 오류가 발생했습니다: {e}")
        else:
            records = get_user_records(student_id)
            if records:
                st.subheader("📈 지난 기록 분석")
                st.info(st.session_state[analysis_key])
    
    # 통계 페이지 또는 퀴즈 페이지
    if st.session_state.get('show_stats', False):
        show_statistics(student_id)
    else:
        if st.session_state.get('show_quiz', True):
            show_quiz(student_id)
        else:
            show_statistics(student_id)

# 퀴즈 페이지
def show_quiz(student_id):
    questions = load_questions()
    
    if not questions:
        st.error("문제를 불러올 수 없습니다.")
        return
    
    # 세션 상태 초기화
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.question_ids = []
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.show_result = False
    
    # 퀴즈 시작
    if not st.session_state.quiz_started:
        st.title("🎯 정유한의 시험 100점을 향한 여정")
        st.markdown("---")
        st.subheader("문제 풀기 준비")
        st.info(f"총 {len(questions)}문제 중 20문제가 랜덤으로 출제됩니다.")
        
        if st.button("시작하기", use_container_width=True, type="primary"):
            # 20문제 랜덤 선택
            all_ids = list(range(len(questions)))
            random.shuffle(all_ids)
            st.session_state.question_ids = all_ids[:20]
            st.session_state.current_index = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.quiz_started = True
            st.session_state.show_result = False
            st.rerun()
        return
    
    # 결과 페이지
    if st.session_state.current_index >= len(st.session_state.question_ids):
        if not st.session_state.show_result:
            st.session_state.show_result = True
        
        st.title("🎉 퀴즈 결과")
        st.markdown("---")
        
        score = st.session_state.score
        total = len(st.session_state.question_ids)
        percentage = (score / total * 100) if total > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("정답", f"{score}문제")
        with col2:
            st.metric("오답", f"{total - score}문제")
        with col3:
            st.metric("정답률", f"{percentage:.1f}%")
        
        st.progress(score / total)
        
        # 문제 복습
        with st.expander("📖 문제 복습하기", expanded=False):
            for idx, answer_data in enumerate(st.session_state.answers):
                question = parse_question(answer_data['question'])
                is_correct = answer_data['is_correct']
                
                st.markdown(f"### 문제 {idx + 1} {'✅' if is_correct else '❌'}")
                st.markdown(f"**{question.get('question', '')}**")
                
                if question.get('type') == 'multiple_choice':
                    if question.get('sentence'):
                        st.markdown(f"*{question['sentence']}*")
                    if question.get('korean'):
                        st.info(f"한국어: {question['korean']}")
                
                # 내 답
                user_answer = answer_data['user_answer']
                if question.get('type') == 'multiple_choice':
                    try:
                        user_index = int(user_answer)
                        options = question.get('options', [])
                        if user_index < len(options):
                            user_answer_text = options[user_index]
                        else:
                            user_answer_text = user_answer
                    except:
                        user_answer_text = user_answer
                else:
                    user_answer_text = user_answer
                
                if is_correct:
                    st.success(f"내 답: {user_answer_text}")
                else:
                    st.error(f"내 답: {user_answer_text}")
                    correct_answer = answer_data['correct_answer']
                    if question.get('type') == 'multiple_choice':
                        try:
                            correct_index = int(correct_answer)
                            options = question.get('options', [])
                            if correct_index < len(options):
                                correct_answer_text = options[correct_index]
                            else:
                                correct_answer_text = correct_answer
                        except:
                            correct_answer_text = correct_answer
                    else:
                        correct_answer_text = correct_answer
                    st.success(f"정답: {correct_answer_text}")
                
                st.info(f"💡 해설: {answer_data.get('explanation', '')}")
                if answer_data.get('ai_explanation'):
                    st.info(f"🤖 AI 해설: {answer_data.get('ai_explanation', '')}")
                st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 다시 풀기", use_container_width=True):
                st.session_state.quiz_started = False
                st.rerun()
        with col2:
            if st.button("📊 통계 보기", use_container_width=True):
                st.session_state.show_stats = True
                st.session_state.show_quiz = False
                st.rerun()
    
    else:
        # 퀴즈 페이지
        current_index = st.session_state.current_index
        question_id = st.session_state.question_ids[current_index]
        question = parse_question(questions[question_id])
        question_num = current_index + 1
        total = len(st.session_state.question_ids)
        
        # 진행률 표시
        progress = question_num / total
        st.progress(progress)
        st.caption(f"문제 {question_num} / {total}")
        
        st.title(f"문제 {question_num}")
        st.markdown(f"### {question.get('question', '')}")
        
        # 문제 내용 표시
        if question.get('type') == 'multiple_choice':
            if question.get('sentence'):
                st.markdown(f"**{question['sentence']}**")
            if question.get('example'):
                st.info(f"[보기] {question['example']}")
            if question.get('korean'):
                st.info(f"한국어: {question['korean']}")
            if question.get('conversation'):
                st.markdown(f"```\n{question['conversation']}\n```")
            
            # 객관식 선택
            options = question.get('options', [])
            selected = st.radio(
                "답을 선택하세요:",
                options,
                key=f"question_{question_id}",
                label_visibility="collapsed"
            )
            selected_index = options.index(selected) if selected else None
            
        elif question.get('type') == 'rearrange':
            if question.get('korean'):
                st.info(f"한국어: {question['korean']}")
            if question.get('sentence'):
                st.markdown(f"*{question['sentence']}*")
            words = question.get('words', [])
            if words:
                st.caption(f"주어진 단어: {', '.join(words)}")
            selected = st.text_input(
                "문장을 입력하세요:",
                key=f"question_{question_id}",
                placeholder="문장을 입력하세요"
            )
            selected_index = None
            
        elif question.get('type') in ['sentence_combination', 'sentence_completion', 'sentence_correction', 'fill_blank']:
            sentences = question.get('sentences', [])
            if sentences:
                for sentence in sentences:
                    st.markdown(f"- {sentence}")
            if question.get('sentence'):
                st.markdown(f"*{question['sentence']}*")
            if question.get('korean'):
                st.info(f"한국어: {question['korean']}")
            
            if question.get('type') == 'fill_blank':
                selected = st.text_input(
                    "답을 입력하세요:",
                    key=f"question_{question_id}",
                    placeholder="because 또는 because of를 입력하세요"
                )
            else:
                selected = st.text_area(
                    "답을 입력하세요:",
                    key=f"question_{question_id}",
                    placeholder="문장을 입력하세요",
                    height=100
                )
            selected_index = None
        
        # 정답 확인 상태 확인
        answer_key = f'answer_checked_{question_id}'
        if answer_key not in st.session_state:
            st.session_state[answer_key] = False
        
        # 정답 확인 버튼
        if not st.session_state[answer_key]:
            if st.button("✅ 정답 확인", use_container_width=True, type="primary"):
                if selected is None or (isinstance(selected, str) and not selected.strip()):
                    st.warning("답을 입력하거나 선택해주세요.")
                else:
                    # 정답 체크
                    is_correct = False
                    user_answer = str(selected_index) if selected_index is not None else selected.strip()
                    
                    if question.get('type') == 'multiple_choice':
                        correct_index = question.get('correct_answer', -1)
                        is_correct = (selected_index == correct_index)
                    else:
                        correct_answer = str(question.get('correct_answer', '')).strip().lower()
                        user_answer_lower = user_answer.lower()
                        is_correct = (correct_answer == user_answer_lower)
                    
                    # 결과 표시
                    full_explanation = ""
                    if is_correct:
                        st.success("🎉 정답입니다!")
                        st.session_state.score += 1
                        explanation_text = question.get('explanation', '')
                        if explanation_text:
                            st.info(f"💡 해설: {explanation_text}")
                    else:
                        st.error("❌ 틀렸습니다.")
                        correct_answer = question.get('correct_answer', '')
                        if question.get('type') == 'multiple_choice':
                            try:
                                correct_index = int(correct_answer)
                                options = question.get('options', [])
                                if correct_index < len(options):
                                    correct_answer_text = options[correct_index]
                                else:
                                    correct_answer_text = correct_answer
                            except:
                                correct_answer_text = correct_answer
                        else:
                            correct_answer_text = correct_answer
                        st.info(f"정답: {correct_answer_text}")
                        
                        # 기본 해설 표시
                        explanation_text = question.get('explanation', '')
                        if explanation_text:
                            st.info(f"💡 해설: {explanation_text}")
                        
                        # AI 스트리밍 해설
                        st.markdown("### 🤖 AI 맞춤 해설")
                        explanation_placeholder = st.empty()
                        full_explanation = ""
                        
                        stream = generate_streaming_explanation(question, user_answer, correct_answer)
                        if stream:
                            for chunk in stream:
                                if chunk.choices and len(chunk.choices) > 0:
                                    delta = chunk.choices[0].delta
                                    if hasattr(delta, 'content') and delta.content:
                                        full_explanation += delta.content
                                        explanation_placeholder.markdown(full_explanation)
                        
                        # 틀린 문제 저장
                        save_wrong_answer(student_id, question, user_answer, correct_answer, full_explanation)
                    
                    # 답변 저장
                    ai_explanation_text = full_explanation if not is_correct else ''
                    st.session_state.answers.append({
                        'question_id': question_id,
                        'user_answer': user_answer,
                        'is_correct': is_correct,
                        'correct_answer': question.get('correct_answer', ''),
                        'explanation': question.get('explanation', ''),
                        'ai_explanation': ai_explanation_text,
                        'question': question
                    })
                    
                    # 정답 확인 완료 표시
                    st.session_state[answer_key] = True
                    st.session_state[f'answer_result_{question_id}'] = {
                        'is_correct': is_correct,
                        'user_answer': user_answer,
                        'full_explanation': full_explanation
                    }
                    st.rerun()
        else:
            # 이미 정답 확인한 경우 결과 표시
            result = st.session_state.get(f'answer_result_{question_id}', {})
            is_correct = result.get('is_correct', False)
            
            if is_correct:
                st.success("🎉 정답입니다!")
                explanation_text = question.get('explanation', '')
                if explanation_text:
                    st.info(f"💡 해설: {explanation_text}")
            else:
                st.error("❌ 틀렸습니다.")
                correct_answer = question.get('correct_answer', '')
                if question.get('type') == 'multiple_choice':
                    try:
                        correct_index = int(correct_answer)
                        options = question.get('options', [])
                        if correct_index < len(options):
                            correct_answer_text = options[correct_index]
                        else:
                            correct_answer_text = correct_answer
                    except:
                        correct_answer_text = correct_answer
                else:
                    correct_answer_text = correct_answer
                st.info(f"정답: {correct_answer_text}")
                
                explanation_text = question.get('explanation', '')
                if explanation_text:
                    st.info(f"💡 해설: {explanation_text}")
                
                full_explanation = result.get('full_explanation', '')
                if full_explanation:
                    st.markdown("### 🤖 AI 맞춤 해설")
                    st.markdown(full_explanation)
            
            st.markdown("---")
            
            # 다음 문제로 이동 버튼
            if st.button("다음 문제로", use_container_width=True, type="primary", key=f"next_{question_id}"):
                # 현재 문제의 상태 초기화
                del st.session_state[answer_key]
                if f'answer_result_{question_id}' in st.session_state:
                    del st.session_state[f'answer_result_{question_id}']
                st.session_state.current_index += 1
                st.rerun()

if __name__ == "__main__":
    main()
