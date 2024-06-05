# Parts and Users Management System

This is a management system project developed with Flask, a Python web framework. The system allows the management of parts and users, as well as integration with a Telegram bot for notifications and interactions.

## Features

- Listing of users and their permissions
- Listing of parts and their validation states
- Inspection registration and part validation
- Model parts registration and deletion
- User authentication
- Telegram bot notifications

## Prerequisites

- Python 3.x installed
- MySQL or another compatible database
- Telegram account for bot configuration

## Installation and Configuration

1. Clone the repository to your local machine:

git clone https://github.com/your-username/repository-name.git

2. Create a virtual environment and install dependencies:

cd repository-name
python3 -m venv venv
source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)
pip install -r requirements.txt


3. Configure environment variables:

   Create a `.env` file in the root of the project and add the following variables:

DB_HOST=your-host
DB_USER=your-user
DB_PASSWORD=your-password
DB_NAME=your-database
TELEGRAM_BOT_TOKEN=your-token


4. Start the Flask server:

python main.py


5. Start the Telegram bot:

python telegramapi.py


## Usage

- Access the web application at [http://localhost:5000](http://localhost:5000)
- Use the routes specified in the documentation to interact with the system

## Documentation

The documentation of the routes is available in the Swagger interface of the application. Access [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/) to consult the documentation.

## Contribution

Contributions are welcome! Feel free to send pull requests or report issues.
