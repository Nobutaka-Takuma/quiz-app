import streamlit as st
import json
import random
import os

# --- ファイル読み込み関数 ---
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_comments(file_path, comments):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

# ファイルパス
problems_file = "problems.json"
comments_file = "comments.json"
subjects_file = "master_subjects.json"
chapters_file = "master_chapters.json"
sections_file = "master_sections.json"
subsections_file = "master_subsections.json"

# データロード
problems = load_json(problems_file)
comments = load_json(comments_file)
subjects = load_json(subjects_file)
chapters = load_json(chapters_file)
sections = load_json(sections_file)
subsections = load_json(subsections_file)

# --- Streamlitアプリ ---
st.title("みんなで学ぼう！問題集アプリ")

if not problems:
    st.warning("問題データが存在しません。problems.jsonを確認してください。")
    st.stop()

if 'problems' not in st.session_state:
    st.session_state.problems = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False

if not st.session_state.problems:
    # --- カテゴリ選択 ---
    selected_subject = st.selectbox("科目を選んでください", list(subjects.keys()))

    if selected_subject:
        subject_chapters = list(set([p["chapter_id"] for p in problems if p.get("subject_id") == selected_subject]))

        if subject_chapters:
            selected_chapter = st.selectbox("Chapterを選んでください", subject_chapters)

            if selected_chapter:
                chapter_sections = list(set([p["section_id"] for p in problems if p.get("subject_id") == selected_subject and p.get("chapter_id") == selected_chapter]))

                if chapter_sections:
                    selected_section = st.selectbox("Sectionを選んでください", chapter_sections)

                    filtered_problems = [p for p in problems if p["subject_id"] == selected_subject and p["chapter_id"] == selected_chapter and p["section_id"] == selected_section]

                    if st.button("このカテゴリでスタート"):
                        st.session_state.problems = filtered_problems
                        st.session_state.current_index = 0
                        st.session_state.score = 0
                        st.session_state.show_explanation = False
                        st.rerun()
                else:
                    st.warning("選択されたChapterに対応するSectionが存在しません。problems.jsonを確認してください。")
                    st.stop()
        else:
            st.warning("選択された科目に対応するChapterが存在しません。problems.jsonを確認してください。")
            st.stop()
else:
    # --- 問題出題フェーズ ---
    if st.session_state.current_index >= len(st.session_state.problems):
        st.balloons()
        st.success(f"全問終了！あなたのスコアは {st.session_state.score} / {len(st.session_state.problems)} です。")
        if st.button("最初からやり直す"):
            st.session_state.problems = []
            st.session_state.current_index = 0
            st.session_state.score = 0
            st.rerun()
        st.stop()

    current_problem = st.session_state.problems[st.session_state.current_index]

    st.markdown(f"### 問題 {st.session_state.current_index + 1}")
    st.write(current_problem["question"])

    selected = st.radio("選択肢を選んでください", current_problem["options"])

    if st.button("回答する"):
        st.session_state.show_explanation = True
        if selected == current_problem["answer"]:
            st.success("正解です！")
            st.session_state.score += 1
        else:
            st.error(f"不正解です。正解は「{current_problem['answer']}」です。")

    if st.session_state.show_explanation:
        explanation = current_problem.get("explanation", "解説はありません。")
        st.info(f"解説：{explanation}")

        # コメント表示
        st.markdown("#### この問題へのコメント")
        problem_key = current_problem["question"]
        problem_comments = comments.get(problem_key, [])
        if problem_comments:
            for idx, comment in enumerate(problem_comments, 1):
                st.write(f"{idx}. {comment}")
        else:
            st.write("コメントはまだありません。")

        # コメント投稿
        new_comment = st.text_input("コメントを入力してください")
        if st.button("コメントを送信"):
            if new_comment.strip():
                if problem_key not in comments:
                    comments[problem_key] = []
                comments[problem_key].append(new_comment.strip())
                save_comments(comments_file, comments)
                st.success("コメントを保存しました！")
                st.rerun()
            else:
                st.warning("コメントが空です。入力してください。")

        if st.button("次の問題へ"):
            st.session_state.current_index += 1
            st.session_state.show_explanation = False
            st.rerun()
