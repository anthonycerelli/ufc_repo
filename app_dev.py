import streamlit as st
import pandas as pd
import plotly.express as px
from airtable import Airtable

# Define a function to fetch and return data from Airtable
def fetch_data(airtable_instance, columns):
    records = airtable_instance.get_all()
    records_fields = [record['fields'] for record in records]
    
    # Adding missing columns with None value
    for record_fields in records_fields:
        for column in columns:
            if column not in record_fields:
                record_fields[column] = None
    
    return pd.DataFrame(records_fields, columns=columns)

# Define a function to fetch and return player points
def get_player_points(data):
    return data.groupby('Name')['Points'].sum().reset_index()

def fetch_betting_odds(fight_title):
    # This function should fetch betting odds from your data source.
    # For demonstration, I'm returning dummy data. Replace this with your actual data fetching logic.
    odds = {
        "Leon Edwards vs Colby Covington": "Leon Edwards (-145) favourite",
        "Alexandre Pantoja vs Brandon Royval": "Alexandre Pantoja (-217) favourite",
        "Shavkat Rakhmonov vs Stephen Thompson": "Shavkat Rakhmonov (-465) favourite",
        "Tony Ferguson vs Paddy Pimblett": "Paddy Pimblett (-310) favourite",
        "Josh Emmett vs Bryce Mitchell": "Bryce Mitchell (-200) favourite"
    }
    return odds.get(fight_title, "Odds not available")

# Airtable connection details
airtable_details = {
    'app_id': 'appBsLc1OGVqdyvmx',
    'data_table': 'data',
    'answers_table': 'answers',
    'api_key': 'patYKIypdUwOIHfnZ.9f46b6ae621f442b8a7be503fd4572b48bba4c4acec46ad2263cba6c6d0baef3'
}

# Connect to Airtable
data_airtable = Airtable(airtable_details['app_id'], airtable_details['data_table'], api_key=airtable_details['api_key'])
answers_airtable = Airtable(airtable_details['app_id'], airtable_details['answers_table'], api_key=airtable_details['api_key'])

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
    "Leon Edwards vs Colby Covington": {
        "image": "https://cdn.vox-cdn.com/thumbor/dD02U2Q-ICHoFJZfcJ8C7G02LYg=/0x0:4482x3135/1200x800/filters:focal(1722x0:2438x716)/cdn.vox-cdn.com/uploads/chorus_image/image/72968836/1858548737.0.jpg",
        "Winner of Main Event": ["Leon Edwards", "Colby Covington", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    "Alexandre Pantoja vs Brandon Royval": {
        "image": "https://www.bjpenn.com/wp-content/uploads/2023/12/Alexandre-Pantoja-Brandon-Royval-1.jpg",
        "Winner of Co-Main Event": ["Alexandre Pantoja", "Brandon Royval", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    "Shavkat Rakhmonov vs Stephen Thompson": {
        "image": "https://mmajunkie.usatoday.com/wp-content/uploads/sites/91/2023/12/ufc-296-Shavkat-vs-Wonderboy.jpg?w=1000&h=600&crop=1",
        "Winner": ["Shavkat Rakhmonov", "Stephen Thompson", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    "Tony Ferguson vs Paddy Pimblett": {
        "image": "https://talksport.com/wp-content/uploads/sites/5/2023/03/l-r-opponents-tony-ferguson-866363622.jpg",
        "Winner": ["Tony Ferguson", "Paddy Pimblett", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    "Josh Emmett vs Bryce Mitchell": {
        "image": "https://static.wixstatic.com/media/668b59_8bd46ad49b17409db7f3a755f015abe2~mv2.jpg/v1/fill/w_640,h_360,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/668b59_8bd46ad49b17409db7f3a755f015abe2~mv2.jpg",
        "Winner": ["Josh Emmett", "Bryce Mitchell", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
}

st.title('UFC 296 Live Competition Dashboard')

# Toggle for Live Mode
live_mode = st.checkbox('Live Mode')

# Explanation of the points system
st.markdown("""
#### Points System
- **Winner Prediction**: Correctly predicting the winner of a fight earns you **1 point**.
- **Method of Victory Prediction**: Correctly predicting the method of victory earns you **2 points**.
- **Round Prediction**: Correctly predicting the round earns you **2 points** for 3-round fights. For 5-round fights, this prediction will earn you **3 points** if correct.
""")

if live_mode: 
    # Fetch data and sort
    columns = ['Name', 'Points'] 
    data = fetch_data(data_airtable, columns)
    players_points = get_player_points(data)
    players_points_sorted = players_points.sort_values(by='Points', ascending=False)

    # Create a bar chart using plotly with improved aesthetics
    fig = px.bar(players_points_sorted, x='Name', y='Points',
                 title='Player Rankings',
                 labels={'Points': 'Total Points'},
                 color='Points',
                 color_continuous_scale=px.colors.sequential.Plasma) # Updated color scheme

    # Enhance layout
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)', # Transparent background
        xaxis_title="",
        yaxis_title="Total Points",
        showlegend=False
    )
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(autosize=True, height=600)  # Larger chart for live mode
    fig.update_traces(hoverinfo='all', hoverlabel=dict(bgcolor="white", font_size=16, font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=True)


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

if not live_mode:
    
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
                # Fetch and display betting odds
                odds = fetch_betting_odds(fight_title)
                st.markdown(f"**Betting Odds:** {odds}")
                answers = []
                for title, options in questions.items():
                    key = f"{fight_title}: {title}"
                    if title == 'Method of Victory':
                        method = st.selectbox(title, options, key=key)
                        answers.append((fight_title, title, method))
                        # Automatically assign "Decision" round if method of victory is "Decision"
                        if method == 'Decision':
                            answers.append((fight_title, 'Round Prediction', 'Decision'))
                        else:
                            round_prediction = st.selectbox('Round Prediction', questions['Round Prediction'], key=key+'_round')
                            answers.append((fight_title, 'Round Prediction', round_prediction))
                    elif title != 'Round Prediction':  # Skip round prediction if already handled
                        answer = st.selectbox(title, options, key=key)
                        answers.append((fight_title, title, answer))
                return answers
    
            # Collect user predictions for each fight
            all_answers = []
    
            # Fight 1
            fight1_questions = {
                "Winner of Main Event": ["Leon Edwards", "Colby Covington", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
            }
            all_answers.extend(questions_form("Leon Edwards vs Colby Covington", fight1_questions, fights_questions["Leon Edwards vs Colby Covington"]['image']))
    
            # Fight 2
            fight2_questions = {
                "Winner of Co-Main Event": ["Alexandre Pantoja", "Brandon Royval", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
            }
            all_answers.extend(questions_form("Alexandre Pantoja vs Brandon Royval", fight2_questions, fights_questions["Alexandre Pantoja vs Brandon Royval"]['image']))
    
            # Fight 3
            fight3_questions = {
                "Winner": ["Shavkat Rakhmonov", "Stephen Thompson", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Shavkat Rakhmonov vs Stephen Thompson", fight3_questions, fights_questions["Shavkat Rakhmonov vs Stephen Thompson"]['image']))
    
            # Fight 4
            fight4_questions = {
                "Winner": ["Tony Ferguson", "Paddy Pimblett", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Tony Ferguson vs Paddy Pimblett", fight4_questions, fights_questions["Tony Ferguson vs Paddy Pimblett"]['image']))
    
            # Fight 5
            fight5_questions = {
                "Winner": ["Josh Emmett", "Bryce Mitchell", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Josh Emmett vs Bryce Mitchell", fight5_questions, fights_questions["Josh Emmett vs Bryce Mitchell"]['image']))
    
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
