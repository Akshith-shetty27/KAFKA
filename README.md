<div align="center">

KAFKA 🚀

Your Personal AI-Powered Interview Preparation Platform

Prepare Smarter. Practice Better. Crack Interviews.

A centralized platform designed to help students prepare for technical interviews through structured learning, AI-powered assistance, and intelligent progress tracking.

<br/>
<br/>

Features • Preview • Architecture • Installation

</div>

⸻

💡 About KAFKA

Preparing for placements often means switching between multiple platforms, coding websites, learning resources, and preparation materials.

KAFKA brings the interview preparation experience together in one place.

KAFKA is an AI-powered interview preparation platform built to help students strengthen their technical fundamentals, practice interview questions, clarify doubts, and track their preparation journey.

It combines structured learning, an integrated AI assistant, user authentication, and progress tracking into a unified learning environment.

The goal is simple: make interview preparation more organized, interactive, and effective.

⸻

✨ Features

📚 Structured Interview Preparation

* Topic-wise interview preparation.
* Organized technical question bank.
* Dedicated preparation categories.
* Programming, databases, data structures, and aptitude practice.

🤖 Ask KAFKA — AI Assistant

An integrated AI assistant designed to make learning more interactive.

* Ask technical questions.
* Understand complex programming concepts.
* Get explanations and clarify doubts.
* Powered by Groq and GPT-OSS 120B.

📊 Progress Tracking

* Track preparation progress.
* Monitor completed questions.
* Maintain a structured learning journey.
* Keep track of preparation activities.

🔐 Authentication & User Management

* User registration and login.
* Token-based authentication.
* Refresh token rotation.
* User profile management.
* Password management.

🎯 Personalized Experience

* Individual user profiles.
* Learning goals and preferences.
* Organized preparation experience.

⸻

🖥️ Application Preview

Dashboard

The central workspace for managing your interview preparation journey.

Interview Preparation

Practice interview questions through an organized preparation interface.

Practice Interface

An interactive environment for practising technical questions.

Progress Tracking

Monitor your preparation progress and completed activities.

Authentication

A dedicated sign-in experience for KAFKA users.

⸻

🛠️ Technology Stack

KAFKA uses a modern full-stack architecture.

Layer	Technology	Purpose
Frontend	Vue.js	User interface
Build Tool	Vite	Frontend development
Styling	Tailwind CSS	UI styling
Backend	Django	Backend logic and APIs
Database	PostgreSQL	Data persistence
AI Integration	Groq API	AI-powered assistance
AI Model	GPT-OSS 120B	Conversational intelligence
Version Control	Git & GitHub	Source code management

⸻

🏗️ System Architecture

KAFKA follows a frontend-backend architecture with external AI integration.

flowchart TD
    A[User] --> B[Vue.js Frontend]
    B --> C[Django Backend / API Layer]
    C --> D[Authentication]
    C --> E[Question Bank]
    C --> F[Progress Tracking]
    C --> G[User Profiles]
    D --> H[(PostgreSQL)]
    E --> H
    F --> H
    G --> H
    C --> I[Groq API]
    I --> J[GPT-OSS 120B]
    J --> C
    C --> B

Application Workflow

1. Users interact with the Vue.js frontend.
2. API requests are sent to the Django backend.
3. Django handles authentication and application logic.
4. PostgreSQL stores application data.
5. Ask KAFKA integrates with the AI model through Groq.
6. Responses are delivered back to the frontend.

⸻

📁 Project Structure

KAFKA/
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── accounts/
│   ├── questions/
│   ├── progress/
│   ├── manage.py
│   └── requirements.txt
│
├── docs/
│   └── screenshots/
│       ├── dashboard.png
│       ├── practice.png
│       ├── prepare.png
│       ├── progress.png
│       └── sign_in.png
│
├── .gitignore
└── README.md

⸻

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

2. Backend Setup

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Configure your backend environment variables using your environment configuration template.

Set up PostgreSQL and provide the appropriate database credentials.

Run database migrations:

python manage.py migrate

Start the backend server:

python manage.py runserver

3. Frontend Setup

Open another terminal:

cd frontend
npm install
npm run dev

Open the local development URL displayed in your terminal.

⸻

🔐 Environment Configuration

Create your backend .env file using the provided environment configuration template, if available.

Configure the necessary values:

* Django secret key.
* Database credentials.
* Debug settings.
* Groq API key.

Security reminder: Never commit .env files, API keys, database passwords, or authentication secrets to GitHub.

⸻

🗺️ Future Roadmap

KAFKA is an evolving project. Some planned improvements include:

* AI-powered mock interviews.
* Personalized preparation recommendations.
* Advanced performance analytics.
* Adaptive question difficulty.
* Additional technical interview categories.
* Enhanced AI learning assistance.

⸻

🎯 Vision

KAFKA aims to simplify the interview preparation journey by bringing structured learning, intelligent assistance, and progress tracking into a single platform.

Instead of switching between multiple resources, students can use one platform to learn, practise, track progress, and get AI-powered assistance.

<div align="center">

One Platform. Smarter Preparation. Better Opportunities.

Built with ❤️ for the next generation of developers.

KAFKA 🚀

</div>
