import streamlit as st
import pandas as pd
from airtable import Airtable

# Connect to Airtable
data_airtable = Airtable('appBsLc1OGVqdyvmx', 'data', api_key='patYKIypdUwOIHfnZ.9f46b6ae621f442b8a7be503fd4572b48bba4c4acec46ad2263cba6c6d0baef3')
answers_airtable = Airtable('appBsLc1OGVqdyvmx', 'answers', api_key='patYKIypdUwOIHfnZ.9f46b6ae621f442b8a7be503fd4572b48bba4c4acec46ad2263cba6c6d0baef3')

columns = ['Name', 'Photo', 'Fight', 'Question', 'Answer', 'Points']  # List of all your columns
data_records = data_airtable.get_all()
data_records_fields = [record['fields'] for record in data_records]

# Adding missing columns with None value
for record_fields in data_records_fields:
    for column in columns:
        if column not in record_fields:
            record_fields[column] = None

data = pd.DataFrame(data_records_fields, columns=columns)

answers_records = answers_airtable.get_all()
answers_records_fields = [record['fields'] for record in answers_records]

# Assuming you also want to do the same for answers DataFrame
answers_columns = ['Fight', 'Question', 'Correct Answer', 'Points']  # Update with your actual column names
for record_fields in answers_records_fields:
    for column in answers_columns:
        if column not in record_fields:
            record_fields[column] = None

answers = pd.DataFrame(answers_records_fields, columns=answers_columns)

# Questions and options
fights_questions = {
    "Islam Makhachev (-278) vs Alexander Volkanovski (+225)": {
        "image": "https://talksport.com/wp-content/uploads/sites/5/2023/02/islam-makhachev-russia-reacts-victory-795103440.jpg",
        "Winner of Main Event": ["Alexander Volkanovski", "Islam Makhachev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Decision"],
    },
    "Kamaru Usman (+270) vs Khamzat Chimaev (-340)": {
        "image": "https://phantom-marca.unidadeditorial.es/fa3ad42ae77eb388cf89ec04d9316a0d/resize/1200/f/jpg/assets/multimedia/imagenes/2023/10/11/16970567736424.jpg",
        "Winner of Co-Main Event": ["Kamaru Usman", "Khamzat Chimaev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Magomed Ankalaev (-375) vs Johnny Walker (+295)": {
        "image": "https://mmajunkie.usatoday.com/wp-content/uploads/sites/91/2023/07/Magomed-Ankalaev-vs.-Johnny-Walker-UFC-294-split.jpg?w=1000&h=600&crop=1",
        "Winner": ["Magomed Ankalaev #2", "Johnny Walker #7", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Ikram Aliskerov (-650) vs Warlley Alves (+455)": {
        "image": "https://i.ytimg.com/vi/z_kYbobkTyc/maxresdefault.jpg?sqp=-oaymwEmCIAKENAF8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGH8gIygTMA8=&rs=AOn4CLDXQl63aM3t_eWcQrY0m9Q28ox56A",
        "Winner": ["Ikram Aliskerov", "Warlley Alves", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Said Nurmagomedov (-218) vs Muin Gafurov (+180)": {
        "image": "https://staticg.sportskeeda.com/editor/2023/10/750f9-16974355420280-1920.jpg?w=840",
        "Winner": ["Said Nurmagomedov", "Muin Gafurov", "Draw"],
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
        def questions_form(fight_title, questions, image):
            st.subheader(fight_title)
            st.image(image)
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
        all_answers.extend(questions_form("Islam Makhachev vs Alexander Volkanovski", fight1_questions, fights_questions["Islam Makhachev (-278) vs Alexander Volkanovski (+225)"]['image']))

        # Fight 2
        fight2_questions = {
            "Winner of Co-Main Event": ["Kamaru Usman", "Khamzat Chimaev", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Kamaru Usman vs Khamzat Chimaev", fight2_questions, fights_questions["Kamaru Usman (+270) vs Khamzat Chimaev (-340)"]['image']))

        # Fight 3
        fight3_questions = {
            "Winner": ["Magomed Ankalaev #2", "Johnny Walker #7", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Magomed Ankalaev vs Johnny Walker", fight3_questions, fights_questions["Magomed Ankalaev (-375) vs Johnny Walker (+295)"]['image']))

        # Fight 4
        fight4_questions = {
            "Winner": ["Ikram Aliskerov", "Warlley Alves", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Ikram Aliskerov vs Warlley Alves", fight4_questions, fights_questions["Ikram Aliskerov (-650) vs Warlley Alves (+455)"]['image']))

        # Fight 5
        fight5_questions = {
            "Winner": ["Said Nurmagomedov", "Muin Gafurov", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Said Nurmagomedov vs Muin Gafurov", fight5_questions, fights_questions["Said Nurmagomedov (-218) vs Muin Gafurov (+180)"]['image']))

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
