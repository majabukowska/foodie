# Foodie 

## Introduction

This Flask application offers a comprehensive diet plan management system. It allows users to generate, save, download, and manage personalized diet plans. With user authentication features, the app ensures a secure and personalized experience.

## Features

### User Authentication
- **Sign Up**: New users can register by providing their details.
- **Login**: Existing users can log in to access their personalized dashboard.
- **Logout**: Secure logout functionality for ending user sessions.

### Diet Plan Generation
- **Custom Plans**: Users can generate diet plans based on specific criteria like ingredients, calorie count, and dietary requirements.
- **AI Integration**: Utilizes OpenAI's GPT model to generate creative and varied diet plans.
- **Interactive UI**: Easy-to-use interface for inputting diet plan requirements.

### Diet Plan Management
- **Save Plans**: Users can save the generated diet plans for future reference.
- **View Plans**: Users can view their saved diet plans in a user-friendly format.
- **Download Plans**: The application allows downloading of diet plans in a text format for offline use.
- **Delete Plans**: Users have the option to delete their saved plans.

### Account Management
- **Profile Customization**: Users can update their profile information, including name and email.
- **Password Management**: Features for updating and resetting passwords.
- **Secure Authentication**: Enhanced security measures for user data protection.

### Recipe Management
- **View Recipes**: Users can browse through their generated diet plans and view detailed recipes.
- **Recipe Customization**: Options to customize recipes according to user preferences.

## Installation

### Prerequisites

- Python 3.6+
- Pip (Python package manager)
- Firebase account and Firestore database

### Setup

1. **Clone the Repository**:

    `git clone [repository-url]`

    `cd [repository-directory]`


2. **Virtual Environment (Recommended)**:

    `python -m venv venv`

    For Linux: source `venv/bin/activate`
    
    For Windows: `venv\Scripts\activate`

 3. **Install Dependencies**:

    `pip install -r requirements.txt`


4. **Environment Variables**:
Set up the following variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `FIREBASE_CREDENTIALS_BASE64`: Base64 encoded Firebase credentials (if you are using linux you can encode your credentials using this command: base64 -w 0 /app/yourfirebasefile.json)
- `SECRET_KEY`: A secret key for the Flask application

5. **Firebase Setup**:
Ensure your Firebase project and Firestore database are set up.

6. **Initialize Database**:
Configure Firestore collections as required by the application.

## Running the Application

Execute the following command:

    flask run --port=5001


Access the application at `http://localhost:5001`.

## Usage

- **Registration and Authentication**: Signup at `/signup`, login at `/login`, logout at `/logout`.
- **Diet Plan Generation**: Authenticated users can generate diet plans at `/generate`.
- **Diet Plan Management**: View at `/recipes`, download at `/download-diet-plan/<name>`, save at `/save-diet-plan`, delete at `/delete-recipe/<recipe_id>`.
- **Account Management**: Update account details at `/update-account`.

## Dependencies

- Flask
- Flask-Login
- Werkzeug
- Firebase Admin
- OpenAI




   


