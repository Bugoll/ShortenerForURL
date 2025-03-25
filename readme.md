Description:

This project is a URL shortener that allows users to shorten long URLs and generate QR codes for them. It includes user authentication and a personal dashboard for managing shortened links.



Installation:

Prerequisites:

Before running the code, ensure you have the following installed:

- Python 3.x
- pip (Python package manager)



Clone this repository to your local machine:

1. Open the command line or terminal on your computer.
2. Navigate to the directory where you want to clone the repository.
3. Run the git clone command followed by the URL of the GitHub repository:
git clone https://github.com/Bugoll/ShortenerForURL.git


Install the required dependencies:

    $make setup

Install the required dependencies for development:

    $make setup-dev


Create the Database:

1. Initialize the database migrations folder (if not already initialized):

        
        $export FLASK_APP=main.py
        $flask db init

2. Generate the migration script for the database schema:

        $flask db migrate -m "Initial migration"

3. Apply the migration to create the database:

        $flask db upgrade

This will create the shortener.sqlite database in the instance folder.

Run the Application

Start the application using the following command:

    $make run

The application will be available at http://127.0.0.1:5000.

Additional Commands
Run Linting
To check the code for style issues:

    $make lint



Auto-Fix Code Style Issues
If issues are found, you can fix them using black and isort:

    $black main.py
    $isort main.py

Clean the Virtual Environment
To remove all installed dependencies and reset the virtual environment:

    $make clean  



Troubleshooting
If you encounter any issues:

1. Ensure you have activated the virtual environment.
2. Verify that all dependencies are installed using:

        $pip install -r requirements.txt

3. Check the Flask-Migrate commands to ensure the database is created correctly.