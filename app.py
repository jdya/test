import streamlit as st
import json
import random

# 페이지 설정
st.set_page_config(
    page_title="영어 문법 퀴즈",
    page_icon="📚",
    layout="wide"
)

# 문제 데이터 로드
@st.cache_data
def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

questions = load_questions()

# 세션 상태 초기화
if 'question_ids' not in st.session_state:
    question_ids = list(range(len(questions)))
    random.shuffle(question_ids)
    st.session_state.question_ids = question_ids
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.show_result = False

# 메인 페이지
if st.session_state.current_index >= len(st.session_state.question_ids):
    # 결과 페이지
    st.title("🎉 퀴즈 결과")
    
    score = st.session_state.score
    total = len(questions)
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
            question = answer_data['question']
            is_correct = answer_data['is_correct']
            
            st.markdown(f"### 문제 {idx + 1} {'✅' if is_correct else '❌'}")
            
            st.markdown(f"**{question['question']}**")
            
            if question['type'] == 'multiple_choice':
                if 'sentence' in question:
                    st.markdown(f"*{question['sentence']}*")
                if 'korean' in question:
                    st.info(f"한국어: {question['korean']}")
            
            # 내 답
            user_answer = answer_data['user_answer']
            if question['type'] == 'multiple_choice':
                try:
                    user_index = int(user_answer)
                    if user_index < len(question['options']):
                        user_answer_text = question['options'][user_index]
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
                if question['type'] == 'multiple_choice':
                    try:
                        correct_index = int(correct_answer)
                        if correct_index < len(question['options']):
                            correct_answer_text = question['options'][correct_index]
                        else:
                            correct_answer_text = correct_answer
                    except:
                        correct_answer_text = correct_answer
                else:
                    correct_answer_text = correct_answer
                st.success(f"정답: {correct_answer_text}")
            
            st.info(f"💡 해설: {answer_data['explanation']}")
            st.divider()
    
    if st.button("🔄 다시 풀기", use_container_width=True):
        st.session_state.question_ids = list(range(len(questions)))
        random.shuffle(st.session_state.question_ids)
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()

else:
    # 퀴즈 페이지
    current_index = st.session_state.current_index
    question_id = st.session_state.question_ids[current_index]
    question = questions[question_id]
    question_num = current_index + 1
    total = len(questions)
    
    # 진행률 표시
    progress = question_num / total
    st.progress(progress)
    st.caption(f"문제 {question_num} / {total}")
    
    st.title(f"문제 {question_num}")
    st.markdown(f"### {question['question']}")
    
    # 문제 내용 표시
    if question['type'] == 'multiple_choice':
        if 'sentence' in question:
            st.markdown(f"**{question['sentence']}**")
        if 'example' in question:
            st.info(f"[보기] {question['example']}")
        if 'korean' in question:
            st.info(f"한국어: {question['korean']}")
        if 'conversation' in question:
            st.markdown(f"```\n{question['conversation']}\n```")
        
        # 객관식 선택
        options = question['options']
        selected = st.radio(
            "답을 선택하세요:",
            options,
            key=f"question_{question_id}",
            label_visibility="collapsed"
        )
        selected_index = options.index(selected) if selected else None
        
    elif question['type'] == 'rearrange':
        if 'korean' in question:
            st.info(f"한국어: {question['korean']}")
        if 'sentence' in question:
            st.markdown(f"*{question['sentence']}*")
        st.caption(f"주어진 단어: {', '.join(question['words'])}")
        selected = st.text_input(
            "문장을 입력하세요:",
            key=f"question_{question_id}",
            placeholder="문장을 입력하세요"
        )
        selected_index = None
        
    elif question['type'] in ['sentence_combination', 'sentence_completion', 'sentence_correction', 'fill_blank']:
        if 'sentences' in question:
            for sentence in question['sentences']:
                st.markdown(f"- {sentence}")
        if 'sentence' in question:
            st.markdown(f"*{question['sentence']}*")
        if 'korean' in question:
            st.info(f"한국어: {question['korean']}")
        
        if question['type'] == 'fill_blank':
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
    
    # 정답 확인 버튼
    if st.button("✅ 정답 확인", use_container_width=True, type="primary"):
        if selected is None or (isinstance(selected, str) and not selected.strip()):
            st.warning("답을 입력하거나 선택해주세요.")
        else:
            # 정답 체크
            is_correct = False
            user_answer = str(selected_index) if selected_index is not None else selected.strip()
            
            if question['type'] == 'multiple_choice':
                correct_index = question.get('correct_answer', -1)
                is_correct = (selected_index == correct_index)
            else:
                correct_answer = str(question.get('correct_answer', '')).strip().lower()
                user_answer_lower = user_answer.lower()
                is_correct = (correct_answer == user_answer_lower)
            
            # 결과 표시
            if is_correct:
                st.success("🎉 정답입니다!")
                st.session_state.score += 1
            else:
                st.error("❌ 틀렸습니다.")
                correct_answer = question.get('correct_answer', '')
                if question['type'] == 'multiple_choice':
                    try:
                        correct_index = int(correct_answer)
                        if correct_index < len(question['options']):
                            correct_answer_text = question['options'][correct_index]
                        else:
                            correct_answer_text = correct_answer
                    except:
                        correct_answer_text = correct_answer
                else:
                    correct_answer_text = correct_answer
                st.info(f"정답: {correct_answer_text}")
            
            # 해설 표시
            st.info(f"💡 해설: {question.get('explanation', '')}")
            
            # 답변 저장
            st.session_state.answers.append({
                'question_id': question_id,
                'user_answer': user_answer,
                'is_correct': is_correct,
                'correct_answer': question.get('correct_answer', ''),
                'explanation': question.get('explanation', ''),
                'question': question
            })
            
            # 다음 문제로 이동
            st.session_state.current_index += 1
            st.rerun()
