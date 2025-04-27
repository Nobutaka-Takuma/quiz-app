import streamlit as st
import json
import random
import os

# --- 問題集ファイルの読み込み ---
def load_problems(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        st.error("問題ファイルが見つかりません！")
        return []

# --- コメントファイルの読み込みと保存 ---
def load_comments(file_path):
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
problems = load_problems(problems_file)
comments = load_comments(comments_file)

# --- Streamlitアプリ ---
st.title("みんなで学ぼう！問題集アプリ")

if not problems:
    st.stop()

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.show_explanation = False

# インデックスが問題数を超えたらリセット
if st.session_state.current_index >= len(problems):
    st.session_state.current_index = 0
    st.session_state.score = 0

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
            st.experimental_rerun()
        else:
            st.warning("コメントが空です。入力してください。")

    if st.button("次の問題へ"):
        st.session_state.current_index += 1
        st.session_state.show_explanation = False

        if st.session_state.current_index >= len(problems):
            st.balloons()
            st.success(f"全問終了！あなたのスコアは {st.session_state.score} / {len(problems)} です。")
            if st.button("最初からやり直す"):
                st.session_state.current_index = 0
                st.session_state.score = 0
        else:
            st.rerun()
