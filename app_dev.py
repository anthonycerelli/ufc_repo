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
    "Jiří Procházka vs Alex Pereira": {
        "image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/background_image_sm/s3/2023-10/102723-hero-main-event-spotlight-pereira-prochazka.jpg?h=d1cb525d&itok=lN0fhLFW",
        "Winner of Main Event": ["Jiří Procházka", "Alex Pereira", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Decision"],
    },
    "Sergei Pavlovich vs Tom Aspinall": {
        "image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/background_image_sm/s3/2023-11/110323-hero-aspinall-pavlovich-by-the-numbers.jpg?h=d1cb525d&itok=5Z_qOxa8",
        "Winner of Co-Main Event": ["Sergei Pavlovich", "Tom Aspinall", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Jéssica Andrade vs Mackenzie Dern": {
        "image": "https://mmajunkie.usatoday.com/wp-content/uploads/sites/91/2023/08/Mackenzie-Dern-vs.-Jessica-Andrade-UFC-295-combo-split.jpg?w=1000&h=576&crop=1",
        "Winner": ["Jéssica Andrade", "Mackenzie Dern", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Matt Frevola vs Benoit Saint-Denis": {
        "image": "https://mmajunkie.usatoday.com/wp-content/uploads/sites/91/2023/09/matt-frevola-benoit-saint-denis-ufc-295.png?w=1000&h=562&crop=1",
        "Winner": ["Matt Frevola", "Benoit Saint-Denis", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
    "Diego Lopes vs Pat Sabatini": {
        "image": "https://cdn.vox-cdn.com/thumbor/mK2tQUPR8LzaLVJXtifd7m2P6wk=/0x0:3255x2232/1200x0/filters:focal(0x0:3255x2232):no_upscale()/cdn.vox-cdn.com/uploads/chorus_asset/file/25063041/1595299476.jpg",
        "Winner": ["Diego Lopes", "Pat Sabatini", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
    },
}

st.title('UFC 295 Live Competition Dashboard')

# Admin interface for updating correct answers
if st.checkbox('Admin Interface'):
    password = st.text_input("Enter Password", type='password')
    if password == 'tony':
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
    else:
        st.error('Wrong password')

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
            "Winner of Main Event": ["Jiří Procházka", "Alex Pereira", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5", "Decision"],
        }
        all_answers.extend(questions_form("Jiří Procházka vs Alex Pereira", fight1_questions, fights_questions["Jiří Procházka vs Alex Pereira"]['image']))

        # Fight 2
        fight2_questions = {
            "Winner of Co-Main Event": ["Sergei Pavlovich", "Tom Aspinall", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Sergei Pavlovich vs Tom Aspinall", fight2_questions, fights_questions["Sergei Pavlovich vs Tom Aspinall"]['image']))

        # Fight 3
        fight3_questions = {
            "Winner": ["Jéssica Andrade", "Mackenzie Dern", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Jéssica Andrade vs Mackenzie Dern", fight3_questions, fights_questions["Jéssica Andrade vs Mackenzie Dern"]['image']))

        # Fight 4
        fight4_questions = {
            "Winner": ["Matt Frevola", "Benoit Saint-Denis", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Matt Frevola vs Benoit Saint-Denis", fight4_questions, fights_questions["Matt Frevola vs Benoit Saint-Denis"]['image']))

        # Fight 5
        fight5_questions = {
            "Winner": ["Diego Lopes", "Pat Sabatini", "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Decision"],
        }
        all_answers.extend(questions_form("Diego Lopes vs Pat Sabatini", fight5_questions, fights_questions["Diego Lopes vs Pat Sabatini"]['image']))

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
