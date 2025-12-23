
import streamlit as st
import pandas as pd
import sqlite3
import pickle
import plotly.express as px
from database import create_db

# this is configuration
st.set_page_config(page_title="Student Performance System", layout="wide", page_icon="👩‍🎓")
st.title("🎓 Student Performance Prediction System")

# database initalization
create_db()

# database connectivity
def get_db():
    return sqlite3.connect("students.db", check_same_thread=False)

# model loading
try:
    model = pickle.load(open("model.pkl", "rb"))
except:
    st.error("error!! model.pkl not found. Train the model first.")
    st.stop()

# login functions
def login(username, password):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()
    return user

# session start
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# login 
if not st.session_state.logged_in:
    st.subheader(" Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.role = user[3]
            st.success(f"Welcome {user[1]} ({user[3]})")
            st.rerun()
        else:
            st.error("Please enter valid credentials")

# after login function
else:
    st.sidebar.write(f" Logged in as: **{st.session_state.username} ({st.session_state.role})**")

    menu = (
        ["Dashboard", "Add/Delete Student", "Manage Users", "Logout"]
        if st.session_state.role == "teacher"
        else ["Dashboard", "Logout"]
    )

    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Logout":
        st.session_state.logged_in = False
        st.rerun()

    # student dashboard
    if choice == "Dashboard" and st.session_state.role == "student":
        st.header("Student Performence Dashboard")
        conn = get_db()
        df = pd.read_sql("SELECT * FROM academic_data WHERE student_id=?", conn, params=(st.session_state.username,))
        conn.close()

        if df.empty:
            st.warning("No academic records found.")
        else:
            st.subheader("Your Academic Records")
            st.dataframe(df)

            st.markdown("### Performance Trends")
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Score", df["semester_score"].iloc[-1])
            col2.metric("Average Attendance", f"{df['attendance'].mean():.1f}%")
            col3.metric("Study Hours Today", df["study_hours"].iloc[-1])

            # charts of performence
            st.plotly_chart(px.line(df, x="record_id", y="semester_score", markers=True, title="Score Trend"), use_container_width=True)
            st.plotly_chart(px.line(df, x="record_id", y="attendance", markers=True, title="Attendance Trend"), use_container_width=True)
            st.plotly_chart(px.line(df, x="record_id", y="study_hours", markers=True, title="Study Hours Trend"), use_container_width=True)

    # teacher dashboard
    if choice == "Dashboard" and st.session_state.role == "teacher":
        st.header("Teacher Dashboard")
        conn = get_db()
        df = pd.read_sql("SELECT * FROM academic_data", conn)
        st.dataframe(df)
        conn.close()

        if df.empty:
            st.warning("No student records yet.")
        else:
            # quick metrics
            st.markdown("### Summary Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Students", len(df))
            col2.metric("Average Score", f"{df['semester_score'].mean():.1f}")
            col3.metric("Pass Percentage", f"{(df['prediction']=='Pass').mean()*100:.1f}%")

            # charts
            st.plotly_chart(px.bar(df, x="full_name", y="semester_score", color="prediction", title="Score Comparison", hover_data=["attendance","study_hours"]), use_container_width=True)
            st.plotly_chart(px.scatter(df, x="study_hours", y="semester_score", color="prediction", size="attendance", title="Study Hours vs Score", hover_data=["full_name"]), use_container_width=True)
            st.plotly_chart(px.pie(df, names="prediction", title="Pass vs Fail Ratio"), use_container_width=True)

    # add or delete student
    if choice == "Add/Delete Student" and st.session_state.role == "teacher":
        st.header(" Add /  Delete Student")
        with st.expander(" Add New Student"):
            student_id = st.text_input("Student Username")
            full_name = st.text_input("Full Name")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            semester_score = st.number_input("Semester Score (0-100)", min_value=0, max_value=100, step=1)
            study_hours = st.number_input("Average Daily Study Hours", 0, 12)
            attendance = st.number_input("Attendance (%)", 0, 100)

            if st.button("Predict & Save Record"):
                # rule for predicting result
                if semester_score >= 60 and attendance >= 75:
                    result = "Pass"
                else:
                    prediction_value = model.predict([[semester_score, study_hours, attendance]])[0]
                    result = "Pass" if prediction_value == 1 else "Fail"

                conn = get_db()
                conn.execute("""
                    INSERT INTO academic_data
                    (student_id, full_name, gender, semester_score, study_hours, attendance, prediction)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (student_id, full_name, gender, semester_score, study_hours, attendance, result))
                conn.commit()
                conn.close()
                st.success(f"Record saved successfully ✔ Prediction: {result}")

        with st.expander("🗑 Delete Student"):
            delete_user = st.text_input("Enter Student Username to Delete")
            if st.button("Delete Student"):
                if delete_user.strip() == "":
                    st.error("Enter a valid username")
                else:
                    conn = get_db()
                    try:
                        conn.execute("DELETE FROM users WHERE username=? AND role='student'", (delete_user,))
                        conn.execute("DELETE FROM academic_data WHERE student_id=?", (delete_user,))
                        conn.commit()
                        st.success(f"Student '{delete_user}' deleted successfully ✔")
                    except Exception as e:
                        st.error(f"Error deleting student: {e}")
                    conn.close()

    # user managemant
    if choice == "Manage Users" and st.session_state.role == "teacher":
        st.header(" Manage Users")
        st.subheader(" Add New User")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["student", "teacher"])
        if st.button("Create User"):
            conn = get_db()
            try:
                conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, new_role))
                conn.commit()
                st.success("User created successfully ✔")
            except:
                st.error("oops!! Username already exists")
            conn.close()

            #session end

