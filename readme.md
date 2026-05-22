# vehicle-parking-app
Vehicle Parking App using Flask,SQLite and bootstrap

# Vehicle Parking App – V1
A simple and user-friendly web application to manage vehicle parking using Flask, SQLite, and Bootstrap. 

### User
- Register and Login
- Reserve a parking spot from available lots
- Vacate your spot and get charged based on time
- View history of your parking reservations

### Admin
- Login as pre-defined admin
- Create and manage parking lots (auto-creates spots)
- View users and their reservations
- Monitor overall parking activity and revenue

## Running the Application
### Prerequisites
- Python installed (check with python --version)
- Internet access to install required packages

###  Setup (For Linux/MacOS/Windows - Unified)
bash
# Clone or download this repo
cd vehicle_parking_app

# Create virtual environment
python -m venv venv

# Activate environment
# For Linux/MacOS:
source venv/bin/activate
# For Windows:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

> App runs at: http://127.0.0.1:5000/

##  Technologies Used
- Python (Flask Framework)
- SQLite (Database)
- SQLAlchemy (ORM)
- Bootstrap 5
- Jinja2 (Templates)
- HTML + CSS

## Admin Default Credentials
- **Email**: admin1051@gmail.com 
- **Password**: admin@1051