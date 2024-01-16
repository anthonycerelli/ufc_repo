import os
import streamlit as st
import pandas as pd
import plotly.express as px
from airtable import Airtable
import bcrypt

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
        "Sean Strickland vs Dricus Du Plessis": "Sean Strickland (-130) favourite",
        "Raquel Pennington vs Mayra Bueno Silva": "Mayra Bueno Silva (-166) favourite",
        "Neil Magny vs Mike Malott": "Mike Malott (-250) favourite",
        "Chris Curtis vs Marc-André Barriault": "Chris Curtis (-166) favourite",
        "Arnold Allen vs Movsar Evloev": "Movsar Evloev (-166) favourite"
    }
    return odds.get(fight_title, "Odds not available")

# Get airtable parameters
airtable_details = {
    'app_id': os.environ.get('AIRTABLE_APP_ID'),
    'api_key': os.environ.get('AIRTABLE_API_KEY'),
    'data_table': 'data',
    'answers_table': 'answers',
    'login_table': 'login_credentials',
    'historical_data_table':'historical_data'
}

# Connect to Airtable
data_airtable = Airtable(airtable_details['app_id'], airtable_details['data_table'], api_key=airtable_details['api_key'])
answers_airtable = Airtable(airtable_details['app_id'], airtable_details['answers_table'], api_key=airtable_details['api_key'])
historical_data_airtable = Airtable(airtable_details['app_id'], airtable_details['historical_data_table'], api_key=airtable_details['api_key'])
login_airtable = Airtable(airtable_details['app_id'], airtable_details['login_table'], api_key=airtable_details['api_key'])

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
    "Sean Strickland vs Dricus Du Plessis": {
        "image": "https://cdn.vox-cdn.com/thumbor/dD02U2Q-ICHoFJZfcJ8C7G02LYg=/0x0:4482x3135/1200x800/filters:focal(1722x0:2438x716)/cdn.vox-cdn.com/uploads/chorus_image/image/72968836/1858548737.0.jpg",
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-09/STRICKLAND_SEAN_L_BELTMOCK.png?itok=QLnBsSSa",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-07/DU_PLESSUS_DRICUS_L_07-08.png?itok=o3g5Swus",
        "Winner of Main Event": ["Sean Strickland", "Dricus Du Plessis", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    "Raquel Pennington vs Mayra Bueno Silva": {
        "image": "https://www.bjpenn.com/wp-content/uploads/2023/12/Alexandre-Pantoja-Brandon-Royval-1.jpg",
        "fighter_1_image": "",
        "fighter_2_image": "",
        "Winner of Co-Main Event": ["Raquel Pennington", "Mayra Bueno Silva", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    "Neil Magny vs Mike Malott": {
        "image": "https://mmajunkie.usatoday.com/wp-content/uploads/sites/91/2023/12/ufc-296-Shavkat-vs-Wonderboy.jpg?w=1000&h=600&crop=1",
        "fighter_1_image": "",
        "fighter_2_image": "",
        "Winner": ["Neil Magny", "Mike Malott", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    "Chris Curtis vs Marc-André Barriault": {
        "image": "https://talksport.com/wp-content/uploads/sites/5/2023/03/l-r-opponents-tony-ferguson-866363622.jpg",
        "fighter_1_image": "",
        "fighter_2_image": "",
        "Winner": ["Chris Curtis", "Marc-André Barriault", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    "Arnold Allen vs Movsar Evloev": {
        "image": "https://static.wixstatic.com/media/668b59_8bd46ad49b17409db7f3a755f015abe2~mv2.jpg/v1/fill/w_640,h_360,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/668b59_8bd46ad49b17409db7f3a755f015abe2~mv2.jpg",
        "fighter_1_image": "",
        "fighter_2_image": "",
        "Winner": ["Arnold Allen", "Movsar Evloev", "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
}

# Initialize session state for user login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Function to verify login credentials
def check_credentials(username, password, airtable=login_airtable):
    # Example credentials, replace with your actual user data
    users = airtable.get_all()
    hashed_password = bcrypt.hashpw("password".encode('utf-8'), os.environ.get('SALT_VALUE'))

    for user in users:
        if user['fields'].get('username') == username and user['fields'].get('password') == hashed_password:
            return True
    return False

st.set_page_config(layout="wide") 

# # Admin interface for updating correct answers
# if st.checkbox('Admin Interface'):
#     password = st.text_input("Enter Password", type='password')
#     if password == 'tony':
#         st.subheader('Update Correct Answers')
#         if not answers.empty:
#             selected_fight = st.selectbox('Select Fight', answers['Fight'].unique())
#             fight_questions = answers[answers['Fight'] == selected_fight]
#             selected_question = st.selectbox('Select Question', fight_questions['Question'].unique())
    
#             # Getting options for the selected fight and question
#             options = fights_questions[selected_fight][selected_question]
#             correct_answer = st.selectbox('Correct Answer', options)
    
#             points = st.number_input('Points', value=0)
    
#             if st.button('Update Answer'):
#                 # Update the correct answer in the answers Airtable
#                 answer_records = answers_airtable.search('Fight', selected_fight)
                
#                 for record in answer_records:
#                     if record['fields']['Question'] == selected_question:
#                         answers_airtable.update(record['id'], {'Correct Answer': correct_answer, 'Points': points})
#                         break
    
#                 # Update points for users who got the correct answer in the data Airtable
#                 prediction_records = data_airtable.search('Fight', selected_fight)
                
#                 for record in prediction_records:
#                     if record['fields']['Question'] == selected_question and record['fields']['Answer'] == correct_answer:
#                         data_airtable.update(record['id'], {'Points': points})
    
#                 st.success(f'Correct answer updated for {selected_fight} - {selected_question}.')
    
#         else:
#             st.warning('Please add fights and questions to the answers.csv file.')
#     else:
#         st.error('Wrong password')

def main_app():
    st.title('UFC 297 -- "Fantasy" Championship')
    # Explanation of the points system
    st.markdown("""
    #### Points System
    - **Winner Prediction**: Correctly predicting the winner of a fight earns you **1 point**.
    - **Method of Victory Prediction**: Correctly predicting the method of victory earns you **2 points**.
    - **Round Prediction**: Correctly predicting the round earns you **2 points** for 3-round fights. For 5-round fights, this prediction will earn you **3 points** if correct.
    """)
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
                "Winner of Main Event": ["Sean Strickland", "Dricus Du Plessis", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
            }
            all_answers.extend(questions_form("Sean Strickland vs Dricus Du Plessis", fight1_questions, fights_questions["Sean Strickland vs Dricus Du Plessis"]['image']))
    
            # Fight 2
            fight2_questions = {
                "Winner of Co-Main Event": ["Raquel Pennington", "Mayra Bueno Silva", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
            }
            all_answers.extend(questions_form("Raquel Pennington vs Mayra Bueno Silva", fight2_questions, fights_questions["Raquel Pennington vs Mayra Bueno Silva"]['image']))
    
            # Fight 3
            fight3_questions = {
                "Winner": ["Neil Magny", "Mike Malott", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Neil Magny vs Mike Malott", fight3_questions, fights_questions["Neil Magny vs Mike Malott"]['image']))
    
            # Fight 4
            fight4_questions = {
                "Winner": ["Chris Curtis", "Marc-André Barriault", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Chris Curtis vs Marc-André Barriault", fight4_questions, fights_questions["Chris Curtis vs Marc-André Barriault"]['image']))
    
            # Fight 5
            fight5_questions = {
                "Winner": ["Arnold Allen", "Movsar Evloev", "Draw"],
                "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
                "Round Prediction": ["Round 1", "Round 2", "Round 3"],
            }
            all_answers.extend(questions_form("Arnold Allen vs Movsar Evloev", fight5_questions, fights_questions["Arnold Allen vs Movsar Evloev"]['image']))
    
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
    
    # Update the section where you render the chart
    if st.checkbox('Show all players and their total points'):
        st.write('Players Points:')
        
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
    
        # Toggle for Live Mode
        live_mode = st.checkbox('Live Mode')
        if live_mode:
            fig.update_layout(autosize=True, height=600)  # Larger chart for live mode
            fig.update_traces(hoverinfo='all', hoverlabel=dict(bgcolor="white", font_size=16, font_family="Rockwell"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.plotly_chart(fig, use_container_width=True)

# Function to hash password
def hash_password(password):
    salt = os.environ.get('SALT_VALUE').encode()
    return bcrypt.hashpw(password.encode(), salt)

# Function to add new user to Airtable
def add_user(username, hashed_password, airtable):
    airtable.insert({'username': username, 'password': hashed_password.decode()})

def login_page(login_airtable=login_airtable):
    st.title("Login / Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button('Login'):
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

    if st.button('Sign Up'):
        # Hash the password
        hashed_password = hash_password(password)
        
        # Add the new user to Airtable
        add_user(username, hashed_password, login_airtable)
        
        # Log the user in after signing up
        st.session_state['logged_in'] = True
        st.experimental_rerun()

# Main script execution
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
