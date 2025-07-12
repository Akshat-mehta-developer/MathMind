import streamlit as st
from ai_question_generator import generate_questions
from utils import load_users, save_users, update_score, get_topics_by_grade, log_quiz_result
import time
import random
from PIL import Image
import base64

# Load and encode your image
# image_path = "image.png"
# with open(image_path, "rb") as f:
#     img_bytes = f.read()
#     img_base64 = base64.b64encode(img_bytes).decode()


def show_greeting_with_image(image_path, text):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    img_base64 = base64.b64encode(img_bytes).decode()
    # display: flex; justify-content: left; padding: 20px; margin-top:-110px;
    st.markdown(
        f"""
        <div style='        position: absolute;
        left: -250px;
        display: flex;
        align-items: left;
        z-index: 1000;
        margin-top:-70px;'>
                <img src="data:image/jpeg;base64,{img_base64}"
                     style="width: 12vw; max-width: 800px; height: auto; border-radius: 10px;" />
            <h2 style='margin: 0; margin-top: 45px;'>{text}</h2>
            

        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="MathMind - AI Quiz", page_icon="🧠")

QUOTES = ['“Pure mathematics is, in its way, the poetry of logical ideas.” – Albert Einstein',
'“Go down deep enough into anything & you will find mathematics.” – Dean Schlicter',
'“Mathematics is the most beautiful & most powerful creation of the human spirit.” – Stefan Banach',
'“The only way to learn mathematics is to do mathematics.” – Paul Halmos',
'“Mathematics is not about numbers or algorithms: it is about understanding.” – William Paul',
'“Mathematics gives us hope that every problem has a solution.”',
'“Success in math doesn’t come from memorizing formulas — it comes from understanding patterns.”'
]

# Initialize session state
for key in ['username', 'quiz_started', 'score', 'questions', 'current_q', 'start_time', 'grade', 'topic', 'level', 'user_answers', 'quiz_ended', 'view_history']:
    if key not in st.session_state:
        st.session_state[key] = None if key in ['username', 'grade', 'topic', 'level'] else False if key in ['quiz_started', 'quiz_ended', 'view_history'] else 0 if key in ['score', 'current_q'] else []

# Load users
data = load_users()

# --- LOGIN/REGISTER PAGE ---
if not st.session_state.username:
    st.title("🧠 MathMind Login/Register")
    username_input = st.text_input("Enter Username")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            if not username_input:
                st.warning("Enter a username to register.")
            elif username_input in data:
                st.error("Username already exists. Please choose another or login.")
            else:
                data[username_input] = {"score": 0, "grade": 1, "history": []}
                save_users(data)
                st.success(f"User '{username_input}' registered successfully! Please login.")
    with col2:
        if st.button("Login"):
            if not username_input:
                st.warning("Enter your username to login.")
            elif username_input not in data:
                st.error("Username not found. Please register first.")
            else:
                st.session_state.username = username_input
                st.session_state.grade = data[username_input].get("grade", 1)
                st.session_state.score = data[username_input].get("score", 0)
                st.session_state.quiz_ended = False
                st.session_state.quiz_started = False
                st.session_state.current_q = 0
                st.session_state.user_answers = []
                st.rerun()

else:
    # st.markdown(f"### 🚀👋 Hi, **{st.session_state.username}**!")
    if st.session_state.username:
        col1, col2 = st.columns([1, 2])
        # with col1:
        #     st.image(image, width=1500)

        # Display larger image using custom HTML
        # st.markdown(
        #     f"""
        #     <div style='display: flex; justify-content: left; padding: 20px; margin-top:-170px;'>
        #         <img src="data:image/jpeg;base64,{img_base64}"
        #              style="width: 12vw; max-width: 800px; height: auto; border-radius: 10px;" />
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )
        if not st.session_state.view_history and not st.session_state.quiz_started and not st.session_state.quiz_ended:
            # Start Quiz page
            show_greeting_with_image("image.png", f"<span style='color:yellow;'>Hi, {st.session_state.username}!</span>  Let's start the quiz")
        elif st.session_state.view_history:
            # Quiz History page
            show_greeting_with_image("image.png", f"Here's your 🕘 Quiz History !")
        elif st.session_state.quiz_ended:
            # Quiz Results page
            show_greeting_with_image("image.png",
                                     f"Here's how you performed.")
        # with col2:
        #     st.markdown(f"## Hi, **{st.session_state.username}**!")

    # --- SIDEBAR ---
    st.sidebar.title("📊 User Profile")
    st.sidebar.markdown(f"👤 **User:** {st.session_state.username}")
    st.sidebar.markdown(f"🎓 **Grade:** {st.session_state.grade}")
    st.sidebar.markdown(f"🏆 **Total Score:** {data[st.session_state.username]['score']}")

    if st.sidebar.button("Logout"):
        st.session_state.username = None
        st.session_state.quiz_started = False
        st.session_state.quiz_ended = False
        st.rerun()

    if st.sidebar.button("View Quiz History"):
        st.session_state.view_history = True
        st.session_state.quiz_started = False
        st.session_state.quiz_ended = False
        st.rerun()

    if st.sidebar.button("Start New Quiz"):
        st.session_state.view_history = False
        st.session_state.quiz_ended = False
        st.session_state.quiz_started = False
        st.session_state.current_q = 0
        st.session_state.user_answers = []
        st.rerun()

    if st.session_state.view_history:


        # st.title("🕘 Quiz History")
        history = data[st.session_state.username].get("history", [])
        if history:
            headers = ["Date", "Grade", "Topic", "Level", "Score"]
            rows = []
            for record in history:
                rows.append([
                    record.get("date", "Unknown"),
                    record.get("grade", ""),
                    record.get("topic", ""),
                    record.get("level", ""),
                    record.get("score", "")
                ])
            st.table([headers] + rows)
        else:
            st.info("No quiz history found.")
        st.stop()

    # --- QUIZ START PAGE ---
    if not st.session_state.quiz_started and not st.session_state.quiz_ended:
        st.title("🎯 Start Quiz")
        sg = "Select your Grade"
        st.markdown(f"<div style='color:grey; margin-top:10px;'>{sg}</div>", unsafe_allow_html=True)
        selected_grade = st.selectbox("", list(range(1, 13)), index=st.session_state.grade - 1)

        topics = get_topics_by_grade(selected_grade)

        ct = "Choose a Topic"
        st.markdown(f"<div style='color:grey; margin-top:11px;'>{ct}</div>", unsafe_allow_html=True)
        selected_topic = st.selectbox("", topics)


        d = "Difficulty"
        st.markdown(f"<div style='color:grey; margin-top:12px;'>{d}</div>", unsafe_allow_html=True)
        selected_level = st.radio("", ["Easy", "Medium", "Hard"], horizontal=True)

        if st.button("Start Quiz"):

            with st.spinner(""):
                quote = random.choice(QUOTES)
                # st.markdown(f"<div style='color:#0042ff; font-size:18px; text-align: left; position: absolute; "
                #             f"left: -250px; top: -350px; font-style: italic; "
                #             f"background-color: peach; padding:10px;'>"
                #             f"Learn while it loads.&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</div>",
                #             unsafe_allow_html=True)
                st.markdown(f"<div style='color:#0042ff;text-align: left; position: absolute; border-radius: 15px;"
                            f"left: -250px; top: -330px; background-color:#8cbff0;  font-style: italic;"
                            f"max-width:200px; padding:10px;'><p>Learn while it loads</p><em><h3>{quote}</h3></em></div>", unsafe_allow_html=True)

                questions = []
                generated_texts = set()
                for _ in range(10):
                    while True:
                        qdata = generate_questions(selected_grade, selected_topic, selected_level)
                        question_text = qdata["question"].strip()
                        if question_text not in generated_texts:
                            generated_texts.add(question_text)
                            questions.append(qdata)
                            break
                st.session_state.questions = questions

            st.session_state.quiz_started = True
            st.session_state.quiz_ended = False
            st.session_state.score = 0
            st.session_state.current_q = 0
            st.session_state.user_answers = []
            st.session_state.start_time = time.time()
            st.session_state.grade = selected_grade
            st.session_state.topic = selected_topic
            st.session_state.level = selected_level

            data[st.session_state.username]["grade"] = selected_grade
            save_users(data)
            st.rerun()

    # --- QUIZ RUNNING PAGE ---
    elif st.session_state.quiz_started:
        elapsed = time.time() - st.session_state.start_time
        remaining = 600 - elapsed
        timer_placeholder = st.empty()

        if remaining <= 0:
            timer_placeholder.markdown(f"<h3 style='color: red;'>⏰ Time's up! Quiz over.</h3>", unsafe_allow_html=True)
            st.session_state.quiz_started = False
            st.session_state.quiz_ended = True
            update_score(st.session_state.username, st.session_state.score, data)
            log_quiz_result(st.session_state.username, st.session_state.grade, st.session_state.topic,
                            st.session_state.level, st.session_state.score, st.session_state.user_answers)
            st.rerun()
        else:
            mins, secs = int(remaining // 60), int(remaining % 60)
            timer_placeholder.markdown(f"<h4 style='color: green;'>⏱️ Time Left: {mins:02d}:{secs:02d}</h4>", unsafe_allow_html=True)

        qdata = st.session_state.questions[st.session_state.current_q]
        st.markdown(f"<span style='color:#828690; font-size:14px;'>Question {st.session_state.current_q + 1} / 10</span>", unsafe_allow_html=True)
        # st.write(qdata["question"])
        st.markdown(
            f"<div style='font-size: 24px;'>{qdata['question']}</div>",
            unsafe_allow_html=True
        )

        options = qdata["wrong_options"] + [qdata["correct_option"]]
        random.shuffle(options)
        # selected_answer = st.radio("Select your answer:", options, key=st.session_state.current_q)
        q_index = st.session_state.current_q  # Current question index
        radio_key = f"answer_{q_index}"

        # Load or preserve user's selection
        if radio_key not in st.session_state:
            st.session_state[radio_key] = None

        selected_answer = st.radio(
            "Choose an option:",
            options,
            index=options.index(st.session_state[radio_key]) if st.session_state[radio_key] else 0,
            key=radio_key,
        )

        # selected_answer = st.session_state[radio_key]

        # Save selection on every change (use st.session_state directly)
        # st.session_state[radio_key] = selected_answer

        if st.button("Submit Answer", key=f"submit_{st.session_state.current_q}"):
            is_correct = selected_answer == qdata["correct_option"]
            st.session_state.user_answers.append({
                "question": qdata["question"],
                "correct": qdata["correct_option"],
                "chosen": selected_answer,
                "is_correct": is_correct
            })
            if is_correct:
                st.session_state.score += 10
            st.session_state.current_q += 1

            if st.session_state.current_q >= 10:
                st.session_state.quiz_started = False
                st.session_state.quiz_ended = True
                update_score(st.session_state.username, st.session_state.score, data)
                log_quiz_result(st.session_state.username, st.session_state.grade, st.session_state.topic,
                                st.session_state.level, st.session_state.score, st.session_state.user_answers)
            st.rerun()

    # --- RESULTS PAGE ---
    elif st.session_state.quiz_ended:

        st.title("🏆 Quiz Results")
        # st.markdown(f"Your Score: **{st.session_state.score}/100**")
        st.markdown(f"<h1>Your Score: <span style='color:yellow;'>{st.session_state.score}/100</h1></span></h1>",
                    unsafe_allow_html=True)


        def get_polite_feedback(correct, chosen):
            remarks = [
                        "Mistakes are proof you're trying.",
                        "Keep going — every expert was once a beginner!",
                        "No worries! Growth comes from challenges.",
                        "Every step counts — keep moving forward!",
                        "Your effort matters more than perfection - keep improving.",
                        "Each question is a chance to improve.",
                        "Believe in your brain — it’s learning!",
                        "Courage is continuing after a mistake.",
                        "This is how learning happens — keep trying!"
                            ]
            return f"{random.choice(remarks)}"
                    # f"The correct answer was **{correct}**, but you chose **{chosen}**.")


        for idx, ans in enumerate(st.session_state.user_answers):
            is_correct = ans["is_correct"]
            color = "#27ff00" if is_correct else "#ff0000"

            st.markdown(f"**Q{idx + 1}:** {ans['question']}")
            # st.markdown(f"**Your Answer:** <span style='color:{color}; font-weight:bold; font-size:20px;'>{ans['chosen']}❌</span>",
            #             unsafe_allow_html=True)
            if not is_correct:
                st.markdown(f"**Your Answer:** <span style='color:{color}; font-weight:bold; font-size:20px;'>{ans['chosen']}❌</span>",
                        unsafe_allow_html=True)
            elif is_correct:
                st.markdown(f"**Your Answer:** <span style='color:{color}; font-weight:bold; font-size:20px;'>{ans['chosen']}✅</span>",
                        unsafe_allow_html=True)
            st.markdown(f"**Correct Answer:** <span style='color:#27ff00; font-weight:bold;  font-size:20px;'>{ans['correct']}✅</span>",
                        unsafe_allow_html=True)
            # st.markdown(f"**Correct Answer:** {ans['correct']}")

            if not is_correct:
                feedback = get_polite_feedback(ans["correct"], ans["chosen"])
                st.markdown(f"<span style='color:#0042ff; font-size:20px;'>{feedback}</span>", unsafe_allow_html=True)


            st.markdown("---")

        if st.button("Start New Quiz"):
            st.session_state.quiz_ended = False
            st.session_state.quiz_started = False
            st.session_state.current_q = 0
            st.session_state.user_answers = []
            st.rerun()
