import streamlit as st
import pandas as pd
import os

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

# Check if data file exists; if not, create it
if not os.path.exists('data.csv'):
    data = pd.DataFrame(columns=['Name', 'Photo', 'Fight', 'Question', 'Answer', 'Points'])
    data['Points'] = data['Points'].astype(float)  # Ensuring the Points column is of float type
    data.to_csv('data.csv', index=False)
else:
    data = pd.read_csv('data.csv')
    
# Check if answers file exists; if not, create it
if not os.path.exists('answers.csv'):
    answers = pd.DataFrame(columns=['Fight', 'Question', 'Correct Answer', 'Points'])
    for fight, questions in fights_questions.items():
        for question, options in questions.items():
            answers = answers.append({'Fight': fight, 'Question': question, 'Correct Answer': None, 'Points': 0}, ignore_index=True)
    answers.to_csv('answers.csv', index=False)
else:
    answers = pd.read_csv('answers.csv', dtype={'Correct Answer': 'object', 'Points': 'float'})  # Explicitly set the data type for 'Correct Answer' and 'Points'

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
            # Update the correct answer in the answers DataFrame and CSV file
            index = answers[(answers['Fight'] == selected_fight) & (answers['Question'] == selected_question)].index[0]
            answers.at[index, 'Correct Answer'] = correct_answer
            answers.at[index, 'Points'] = points
            answers.to_csv('answers.csv', index=False)

            # Update points for users who got the correct answer
            correct_predictions = data[(data['Fight'] == selected_fight) & (data['Question'] == selected_question) & (data['Answer'] == correct_answer)]
            for idx in correct_predictions.index:
                data.at[idx, 'Points'] = points
            data.to_csv('data.csv', index=False)

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
                data = data.append({'Name': name, 'Photo': 'photo_path_here', 'Fight': fight, 'Question': question, 'Answer': answer}, ignore_index=True)
            data.to_csv('data.csv', index=False)
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