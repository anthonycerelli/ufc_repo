# Package imports
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from airtable import Airtable
import bcrypt
import cloudinary
import cloudinary.uploader

# global variable fight_data -- 5 names of fights
fight_data = ["Sean Strickland vs Dricus Du Plessis", "Raquel Pennington vs Mayra Bueno Silva", "Neil Magny vs Mike Malott", "Chris Curtis vs Marc-André Barriault", "Arnold Allen vs Movsar Evloev"]

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
        fight_data[0]: "Sean Strickland (-130) favourite",
        fight_data[1]: "Mayra Bueno Silva (-166) favourite",
        fight_data[2]: "Mike Malott (-250) favourite",
        fight_data[3]: "Chris Curtis (-166) favourite",
        fight_data[4]: "Movsar Evloev (-166) favourite"
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

# Configuring Cloudinary
cloudinary.config(
  cloud_name = os.environ.get('CLOUD_NAME'),
  api_key = os.environ.get('CLOUD_API_KEY'), 
  api_secret = os.environ.get('CLOUD_SECRET')
)

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
    fight_data[0]: {
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-09/STRICKLAND_SEAN_L_BELTMOCK.png?itok=QLnBsSSa",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-07/DU_PLESSUS_DRICUS_L_07-08.png?itok=o3g5Swus",
        "Winner of Main Event": [fight_data[0].split(' vs ')[0].rstrip(), fight_data[0].split(' vs ')[1].lstrip(), "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    fight_data[1]: {
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-02/PENNINGTON_RAQUEL_L_01-14.png?itok=ygnaP1S3",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-02/BUENO_SILVA_MAYRA_L_02-18.png?itok=w5Uxw6V5",
        "Winner of Co-Main Event": [fight_data[1].split(' vs ')[0].rstrip(), fight_data[1].split(' vs ')[1].lstrip(), "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
    },
    fight_data[2]: {
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-06/MAGNY_NEIL_L_06-24.png?itok=tXrZ7OcK",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-06/MALOTT_MIKE_L_06-10.png?itok=I6d0Jn2U",
        "Winner": [fight_data[2].split(' vs ')[0].rstrip(), fight_data[2].split(' vs ')[1].lstrip(), "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    fight_data[3]: {
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-06/CURTIS_CHRIS_L_06-10.png?itok=1J6fb1lV",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-06/BARRIAULT_MARC-ANDRE_L_06-10.png?itok=A2cIJUsS",
        "Winner": [fight_data[3].split(' vs ')[0].rstrip(), fight_data[3].split(' vs ')[1].lstrip(), "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
    fight_data[4]: {
        "fighter_1_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2022-11/ALLEN_ARNOLD_L_10-29.png?itok=ikJBEURv",
        "fighter_2_image": "https://dmxg5wxfqgb4u.cloudfront.net/styles/athlete_bio_full_body/s3/2023-05/EVLOEV_MOVSAR_L_05-06.png?itok=G5cVdlSj",
        "Winner": [fight_data[4].split(' vs ')[0].rstrip(), fight_data[4].split(' vs ')[1].lstrip(), "Draw"],
        "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
        "Round Prediction": ["Round 1", "Round 2", "Round 3"],
    },
}

# Initialize session state for user login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Function to verify login credentials
def check_credentials(username, password, airtable=login_airtable):
    users = airtable.get_all()

    # Convert the input password to bytes
    password_bytes = password.encode('utf-8')

    for user in users:
        stored_password = user['fields'].get('password')
        if user['fields'].get('username') == username:
            # Convert the stored password to bytes
            stored_password_bytes = stored_password.encode('utf-8')
            # Check if the hashed input password matches the stored hashed password
            if bcrypt.checkpw(password_bytes, stored_password_bytes):
                return True
    return False

st.set_page_config(layout="wide") 

# Upload function for cloudinary
def upload_image_to_cloudinary(uploaded_file):
    try:
        # Convert to bytes
        file_bytes = uploaded_file.getvalue()
        upload_response = cloudinary.uploader.upload(file_bytes, folder="profile_photos")
        return upload_response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def get_cloudinary_image_url(public_id):
    cloud_name = os.environ.get('CLOUD_NAME')
    return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.png"

def update_user_profile(username, image_url):
    # Search for the user in Airtable
    user_records = login_airtable.search('username', username)

    if user_records:
        user_id = user_records[0]['id']
        # Update the record with the new image URL
        login_airtable.update(user_id, {'profile_photo': image_url})
        st.success("Profile updated successfully.")
    else:
        st.error("User not found.")

def main_app(username, data, fight_data):
    st.title('UFC 297 -- "Fantasy" Championship')
    # Tabs
    if username == 'anthony':
        tab1, tab2, tab3 = st.tabs(["Make Predictions", "Game Leaderboard", "Admin"])
    else:
        tab1, tab2 = st.tabs(["Make Predictions", "Game Leaderboard"])
        
    # Tab 1 data
    with tab1:
        # Explanation of the points system
        st.markdown("""
        #### Points System
        - **Winner Prediction**: Correctly predicting the winner of a fight earns you **1 point**.
        - **Method of Victory Prediction**: Correctly predicting the method of victory earns you **2 points**.
        - **Round Prediction**: Correctly predicting the round earns you **2 points** for 3-round fights. For 5-round fights, this prediction will earn you **3 points** if correct.
        """)
        def questions_form(fight_title, questions, image_fighter_1, image_fighter_2, fighter_1, fighter_2):
            st.markdown(f"### {fight_title}")
        
            # Create three columns
            col1, col2, col3 = st.columns([1, 2, 1])
        
            # Display the images in the first and third columns
            with col1:
                st.image(image_fighter_1, caption=fighter_1)
        
            with col3:
                st.image(image_fighter_2, caption=fighter_2)
        
            # Use the second column for the title, betting odds, and questions
            with col2:
                # st.markdown(f"**Betting Odds:** {fetch_betting_odds(fight_title)}")
                answers = []
                for title, options in questions.items():
                    key = f"{fight_title}: {title}"
                    if title == 'Method of Victory':
                        method = st.selectbox(title, options, key=key)
                        answers.append((fight_title, title, method))
                        # Automatically assign "Decision" round if method is "Decision"
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
            "Winner of Main Event": [fight_data[0].split(' vs ')[0].rstrip(), fight_data[0].split(' vs ')[1].lstrip(), "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
        }
        fight_questions_temp = fights_questions[fight_data[0]]
        all_answers.extend(questions_form(fight_data[0], fight1_questions, fight_questions_temp['fighter_1_image'],fight_questions_temp['fighter_2_image'], fight_data[0].split(' vs ')[0].rstrip(), fight_data[0].split(' vs ')[1].lstrip()))

        # Fight 2
        fight2_questions = {
            "Winner of Co-Main Event": [fight_data[1].split(' vs ')[0].rstrip(), fight_data[1].split(' vs ')[1].lstrip(), "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3", "Round 4", "Round 5"],
        }
        fight_questions_temp = fights_questions[fight_data[1]]
        all_answers.extend(questions_form(fight_data[1], fight2_questions, fight_questions_temp['fighter_1_image'],fight_questions_temp['fighter_2_image'], fight_data[1].split(' vs ')[0].rstrip(), fight_data[1].split(' vs ')[1].lstrip()))

        # Fight 3
        fight3_questions = {
            "Winner": [fight_data[2].split(' vs ')[0].rstrip(), fight_data[2].split(' vs ')[1].lstrip(), "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3"],
        }
        fight_questions_temp = fights_questions[fight_data[2]]
        all_answers.extend(questions_form(fight_data[2], fight3_questions, fight_questions_temp['fighter_1_image'],fight_questions_temp['fighter_2_image'], fight_data[2].split(' vs ')[0].rstrip(), fight_data[2].split(' vs ')[1].lstrip()))

        # Fight 4
        fight4_questions = {
            "Winner": [fight_data[3].split(' vs ')[0].rstrip(), fight_data[3].split(' vs ')[1].lstrip(), "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3"],
        }
        fight_questions_temp = fights_questions[fight_data[3]]
        all_answers.extend(questions_form(fight_data[3], fight4_questions, fight_questions_temp['fighter_1_image'],fight_questions_temp['fighter_2_image'], fight_data[3].split(' vs ')[0].rstrip(), fight_data[3].split(' vs ')[1].lstrip()))

        # Fight 5
        fight5_questions = {
            "Winner": [fight_data[4].split(' vs ')[0].rstrip(), fight_data[4].split(' vs ')[1].lstrip(), "Draw"],
            "Method of Victory": ["KO/TKO", "Submission", "Decision", "Other"],
            "Round Prediction": ["Round 1", "Round 2", "Round 3"],
        }
        fight_questions_temp = fights_questions[fight_data[4]]
        all_answers.extend(questions_form(fight_data[4], fight5_questions, fight_questions_temp['fighter_1_image'],fight_questions_temp['fighter_2_image'], fight_data[4].split(' vs ')[0].rstrip(), fight_data[4].split(' vs ')[1].lstrip()))

        if st.button('Submit Predictions'):
            # Save user predictions to the data DataFrame and CSV file
            for fight, question, answer in all_answers:
                record = {'Name': username, 'Fight': fight, 'Question': question, 'Answer': answer, 'Points': 0.0}
                data = data.append(record, ignore_index=True)
                data_airtable.insert(record)
            st.success('Predictions submitted!')

        # Display user's total points
        if username in data['Name'].values:
                total_points = data[data['Name'] == username]['Points'].sum()
                st.write(f"Your total points: {total_points}")
    
    # Update the section where you render the chart
    with tab2:
        st.write('Players Points:')

        # Profile Photo Upload
        uploaded_file = st.file_uploader("Choose a profile picture", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:     
            # Upload to Cloudinary
            upload_response = upload_image_to_cloudinary(uploaded_file)
            if upload_response is not None:
                image_url = upload_response['url']
                # Here you can store the image_url to Airtable
                update_user_profile(username, image_url)
        
        # Fetch data and sort
        columns = ['Name', 'Points'] 
        data = fetch_data(data_airtable, columns)
        players_points = get_player_points(data)
        players_points_sorted = players_points.sort_values(by='Points', ascending=False)
    
        def create_scoreboard():
            # Fetch data and sort
            columns = ['Name', 'Points']
            data = fetch_data(data_airtable, columns)
            players_points = get_player_points(data)
            players_points_sorted = players_points.sort_values(by='Points', ascending=False)
        
            # Create a bar chart using plotly with scoreboard aesthetics
            fig = px.bar(players_points_sorted, x='Name', y='Points',
                         title='Player Rankings',
                         labels={'Points': 'Total Points'},
                         color='Points',
                         text='Points',
                         color_continuous_scale=px.colors.sequential.Viridis) # Aesthetic color scheme
        
            # Customize the layout to make it look like a scoreboard
            fig.update_layout(
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
                xaxis_title="",
                yaxis_title="Total Points",
                showlegend=False,
                font=dict(family="Courier New, monospace", size=14, color="RebeccaPurple"),
                title_font=dict(size=22, color="RebeccaPurple", family="Verdana, sans-serif")
            )
        
            # Updates for live scoreboard
            fig.update_layout(autosize=True, height=600)  # Larger chart for live mode
            fig.update_traces(hoverinfo='all', hoverlabel=dict(bgcolor="white", font_size=16, font_family="Rockwell"))
            st.plotly_chart(fig, use_container_width=True)
           
        
        create_scoreboard()
            
    if username == 'anthony':
        with tab3:
            # Admin interface for updating correct answers
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

# Function to hash password
def hash_password(password):
    # Generate a salt and hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

# Function to add new user to Airtable
def add_user(username, hashed_password, airtable):
    airtable.insert({'username': username, 'password': hashed_password.decode()})

# Function to check if a username already exists in Airtable
def username_exists(username, airtable):
    # Fetch records from Airtable
    records = airtable.get_all()  # Adjust this line according to your Airtable API usage

    # Check if any record matches the username
    for record in records:
        if record['fields'].get('username') == username:
            return True
    return False

def login_page(login_airtable=login_airtable):
    st.title("Login / Sign Up", anchor=None)

    with st.form("Login Form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type='password', placeholder="Enter your password")

        # Function to validate inputs
        def inputs_are_valid(username, password):
            if not username or not password:
                st.error("Username and password cannot be blank.")
                return False
            return True

        # Layout for buttons
        col1, col2 = st.columns(2)
        with col1:
            submit_login = st.form_submit_button('Login')
        with col2:
            submit_signup = st.form_submit_button('Sign Up')

        if submit_login:
            if inputs_are_valid(username, password) and check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            elif not check_credentials(username, password):
                st.error("Incorrect username or password")

        if submit_signup:
            if inputs_are_valid(username, password):
                # Check if username already exists in Airtable
                if username_exists(username, login_airtable):
                    st.error("Username already exists. Please choose a different one.")
                else:
                    # Hash the password
                    hashed_password = hash_password(password)
                    
                    # Add the new user to Airtable
                    add_user(username, hashed_password, login_airtable)
                    
                    # Log the user in after signing up
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.experimental_rerun()

# Main script execution
if st.session_state['logged_in']:
    main_app(st.session_state['username'], data, fight_data)
else:
    login_page()
