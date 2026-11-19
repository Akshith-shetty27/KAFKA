KAFKA 🚀

Your AI-Powered Interview Preparation Companion

<p align="center">
  <strong>Prepare Smarter. Practice Better. Get Interview Ready.</strong>
</p>
<p align="center">
  An intelligent interview preparation platform designed to help students strengthen their technical knowledge, practice problem-solving, and prepare confidently for placement interviews.
</p>

⸻

🌟 Overview

KAFKA is an AI-powered interview preparation platform that brings structured learning, technical practice, progress tracking, and intelligent assistance together in one place.

Built with a modern frontend and a robust backend, KAFKA aims to make interview preparation more organized, interactive, and accessible.

Whether you’re revising Data Structures and Algorithms, practising SQL, strengthening Python fundamentals, or preparing for aptitude assessments, KAFKA provides a centralized environment to support your placement journey.

✨ Key Features

📚 Structured Interview Preparation

* Topic-wise learning and practice.
* Organized question bank.
* Dedicated preparation categories.
* Technical and aptitude-based practice.

🤖 Ask KAFKA – AI Assistant

* AI-powered conversational assistance.
* Get explanations for technical concepts.
* Ask questions and clarify doubts.
* Powered by Large Language Models through Groq.

📊 Progress Tracking

* Track your preparation progress.
* Monitor completed questions.
* Maintain a structured learning journey.

🔐 Authentication & User Management

* Secure user registration and login.
* Token-based authentication.
* Refresh token management.
* User profile management.
* Password management.

🎯 Personalized Preparation

* User profiles with individual learning goals.
* Configurable preferences.
* Organized preparation experience.

🛠️ Tech Stack

Layer	Technologies
Frontend	Vue.js, Vite, Tailwind CSS
Backend	Python, Django
Database	PostgreSQL
AI Integration	Groq API, GPT-OSS
Authentication	Token-based authentication
Version Control	Git & GitHub

🏗️ Architecture

KAFKA follows a frontend-backend architecture.

             USER
               |
               v
       Vue.js Frontend
               |
               v
          API Layer
               |
               v
        Django Backend
          /        \
         /          \
        v            v
   PostgreSQL     Groq API
    Database      AI Assistant

The frontend communicates with the Django backend through APIs.

The backend manages authentication, questions, user profiles, and progress tracking while integrating with the AI provider for conversational assistance.

🚀 Getting Started

Follow these instructions to run KAFKA locally.

Prerequisites

Make sure you have installed:

* Python 3.10+
* Node.js
* PostgreSQL
* Git

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/KAFKA.git
cd KAFKA

2. Setup the Backend

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create your environment configuration using the provided .env.example file.

Configure your database credentials and required API keys.

Run migrations:

python manage.py migrate

Start the backend server:

python manage.py runserver

3. Setup the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

The frontend will be available at the local development URL displayed by Vite.

📁 Project Structure

KAFKA/
│
├── frontend/          # Vue.js application
│
├── backend/           # Django application
│
├── docs/              # Project documentation
│
├── .gitignore
│
└── README.md

🔮 Future Improvements

* Advanced AI-powered mock interviews.
* Personalized learning recommendations.
* Detailed performance analytics.
* More technical interview categories.
* Enhanced question difficulty progression.
* Additional AI-powered learning features.

🎯 Project Goal

The goal of KAFKA is simple:

Make interview preparation more structured, interactive, and intelligent.

Instead of switching between multiple resources, students can use one platform to learn, practise, track their progress, and get AI-powered assistance.

⸻

<p align="center">
  <strong>Built with ❤️ to make interview preparation smarter.</strong>
</p>
