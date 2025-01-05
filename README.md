# intelliresume-fastapi


# Resume Generator with Gemini API

This project allows users to generate a personalized resume by leveraging the Gemini API to dynamically create job summaries, skills, and project descriptions based on the job description (JD) provided by the user. The project is built using Python with the FastAPI framework, and it integrates the Google Gemini API for advanced text generation.

## Features

- **Generate Resume Sections:** Automatically generates and updates key sections of the resume like Skills, Job Summary, and Project Descriptions based on user input.
- **Streaming API Integration:** Uses the Gemini API's `stream=True` feature for faster text generation and real-time interaction.
- **User Authentication:** Users can register, login, and store their resumes.
- **Customizable Resume Data:** Users can input personal details, work experience, skills, education, and more to create a tailored resume.
- **Error Handling:** The application gracefully handles errors and API issues.

## Requirements

- Python 3.8 or higher
- FastAPI
- Uvicorn (for serving the app)
- Google Gemini API key
- A database (used in this example: a simple key-value store)
