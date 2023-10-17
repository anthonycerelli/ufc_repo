import streamlit as st
import pandas as pd
from airtable import Airtable

# Connect to Airtable
data_airtable = Airtable('appBsLc1OGVqdyvmx', 'data', api_key='patYKIypdUwOIHfnZ.9f46b6ae621f442b8a7be503fd4572b48bba4c4acec46ad2263cba6c6d0baef3')
answers_airtable = Airtable('appBsLc1OGVqdyvmx', 'answers', api_key='patYKIypdUwOIHfnZ.9f46b6ae621f442b8a7be503fd4572b48bba4c4acec46ad2263cba6c6d0baef3')

# Read data from Airtable into pandas DataFrame
data_records = data_airtable.get_all()
answers_records = answers_airtable.get_all()

data = pd.DataFrame([record['fields'] for record in data_records])
answers = pd.DataFrame([record['fields'] for record in answers_records])

st.text("Columns in data DataFrame:")
st.write(data.columns.tolist()) 

st.text("Columns in answers DataFrame:")
st.write(answers.columns.tolist())

# Questions and options
fights_questions = {
    "Islam Makhachev vs Alexander Volkanovski": {
        "Winner of Main Event": ["Alexander Volkanovski", "Islam Makhachev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Decision"],
    },
    "Kamaru Usman vs Khamzat Chimaev": {
        "Winner of Co-Main Event": ["Kamaru Usman", "Khamzat Chimaev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Magomed Ankalaev vs Johnny Walker": {
        "Winner": ["Magomed Ankalaev #2", "Johnny Walker #7", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Ikram Aliskerov vs Warlley Alves": {
        "Winner": ["Ikram Aliskerov", "Warlley Alves", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Said Nurmagomedov vs Muin Gafurov": {
        "Winner": ["Said Nurmagomedov", "Muin Gafurov", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Tim Elliott vs Muhammad Mokaev": {
        "Winner": ["Tim Elliott", "Muhammad Mokaev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
}

st.title('UFC 294 Live Competition Dashboard')

# Admin interface for updating correct answers
if st.checkbox('Admin Interface'):
    st.subheader('Update Correct Answers')
    if not answers.empty:
        selected_fight = st.selectbox('Select Fight', answers['Fight'].unique())
        fight_questions = answers[answers['Fight'] == selected_fight]
        selected_question = st.selectbox('Select Question', fight_questions['Question'].unique())

        # Getting options for the selected fight and question
        options = fights_questions[selected_fight][selected_question]
        correct_answer = st.selectbox('Correct Answer', options)

        points = st.number_input('Points', value=0)

        if st.button('Update Answer'):
            # Update the correct answer in the answers Airtable
            answer_records = answers_airtable.search('Fight', selected_fight)
            
            for record in answer_records:
                if record['fields']['Question'] == selected_question:
                    answers_airtable.update(record['id'], {'Correct Answer': correct_answer, 'Points': points})
                    break

            # Update points for users who got the correct answer in the data Airtable
            prediction_records = data_airtable.search('Fight', selected_fight)
            
            for record in prediction_records:
                if record['fields']['Question'] == selected_question and record['fields']['Answer'] == correct_answer:
                    data_airtable.update(record['id'], {'Points': points})

            st.success(f'Correct answer updated for {selected_fight} - {selected_question}.')

    else:
        st.warning('Please add fights and questions to the answers.csv file.')

# User registration or login
name = st.text_input('Enter your name to log in or register:')

if name:
    st.write(f"Welcome {name}!")

    # If user is registered, show their predictions and score (you can add a real score calculation later)
    if name in data['Name'].values:
        user_data = data[data['Name'] == name]
        st.table(user_data[['Fight', 'Question', 'Answer']])

    # If new user, show prediction form
    else:
        # Function to display questions for each fight
        def questions_form(fight_title, questions):
            st.subheader(fight_title)
            answers = []
            for title, options in questions.items():
                key = f"{fight_title}: {title}"
                answer = st.selectbox(title, options, key=key)
                answers.append((fight_title, title, answer))
            return answers

        # Collect user predictions for each fight
        all_answers = []

        # Fight 1
        fight1_questions = {
            "Winner of Main Event": ["Alexander Volkanovski", "Islam Makhachev", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Decision"],
        }
        all_answers.extend(questions_form("Islam Makhachev vs Alexander Volkanovski", fight1_questions))

        # Fight 2
        fight2_questions = {
            "Winner of Co-Main Event": ["Kamaru Usman", "Khamzat Chimaev", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Kamaru Usman vs Khamzat Chimaev", fight2_questions))

        # Fight 3
        fight3_questions = {
            "Winner": ["Magomed Ankalaev #2", "Johnny Walker #7", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Magomed Ankalaev vs Johnny Walker", fight3_questions))

        # Fight 4
        fight4_questions = {
            "Winner": ["Ikram Aliskerov", "Warlley Alves", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Ikram Aliskerov vs Warlley Alves", fight4_questions))

        # Fight 5
        fight5_questions = {
            "Winner": ["Said Nurmagomedov", "Muin Gafurov", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Said Nurmagomedov vs Muin Gafurov", fight5_questions))

        # Fight 6
        fight6_questions = {
            "Winner": ["Tim Elliott", "Muhammad Mokaev", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Tim Elliott vs Muhammad Mokaev", fight6_questions))

        if st.button('Submit Predictions'):
            # Save user predictions to the data DataFrame and CSV file
            for fight, question, answer in all_answers:
                record = {'Name': name, 'Photo': 'photo_path_here', 'Fight': fight, 'Question': question, 'Answer': answer, 'Points': 0.0}
                data = data.append(record, ignore_index=True)
                data_airtable.insert(record)
            st.success('Predictions submitted!')

        # Display user's total points
        if name in data['Name'].values:
                total_points = data[data['Name'] == name]['Points'].sum()
                st.write(f"Your total points: {total_points}")

# Show all predictions and answers (optional, for testing)
if st.checkbox('Show all players and their total points'):
    st.write('Players Points:')
    players_points = data.groupby('Name')['Points'].sum().reset_index()  # Grouping data by name and summing points
    st.write(players_points)
