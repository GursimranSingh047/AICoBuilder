 AI Co-Builder (ProjectPilot)

 Overview

AI Co-Builder (ProjectPilot) is an AI-powered platform that generates complete project code based on user prompts. It integrates backend APIs with AI models to automate software development tasks and improve productivity.

Features

*  AI-based code generation using Gemini API
*  Chat-based interaction with context handling
*  Automatic project structure generation
*  Fast backend processing using FastAPI
*  REST API integration
*  Intelligent suggestions and responses

⸻

🛠️ Tech Stack

* Backend: Python, FastAPI
* Frontend: React
* Database: PostgreSQL
* AI Integration: Gemini API
* Version Control: Git & GitHub


 Installation & Setup
 
1️⃣ Clone the repository
git clone https://github.com/GursimranSingh047/AICoBuilder.git
cd AICoBuilder

2️⃣ Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Setup environment variables
Create a .env file and add:
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=your_database_url

5️⃣ Run the backend server
uvicorn main:app --reload

For running frontend server
npm run dev





 
