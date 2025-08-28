# BrokenBasket – Meal Plan Helper

## Live Deployment
[BrokenBasket is live here](https://broken-basket.vercel.app)

## Project Overview
BrokenBasket is a full-stack meal planning application that uses AI to assist users in generating customized meal plans. The frontend is built with React and the backend uses Python.
# Features
- Personalized Meal Plan Generation : 
Dynamically creates tailored meal plans based on individual user needs and input preferences.

- Dietary Preference Handling :
Supports a wide range of dietary restrictions and preferences, including vegetarian, vegan, gluten-free, and more.

- Calorie-Aware Recipe Tracking :
Provides accurate calorie counts for all generated recipes, helping users stay aligned with nutritional goals.

- AI-Driven Recipe Creation :
Generates custom recipes using LLMs, ensuring variety, adaptability, and alignment with user-specified constraints.

# Architecture

This application utilizes a LangGraph-based workflow architecture to orchestrate the meal planning logic:

### Frontend
Built with Next.js, the frontend serves as the user interface for meal plan interaction, dietary input, and recipe viewing.

### Backend
A Python backend powered by LangChain and LangGraph coordinates the generation process. It handles user prompts, meal plan logic, API interactions, and stateful graph traversal.

### Graph-based Orchestration
LangGraph models the end-to-end generation pipeline as a stateful graph, allowing for modular, multi-step reasoning across meal plan generation, recipe validation, and calorie estimation.

### Database
- MongoDB stores user preferences and plan hitstory

- AstraDb stores the vector information about all the recipes

- Calories per item dataset stored locally

### LLM Integration
OpenAI’s language models are leveraged to generate meal plans, recipes, and rationales based on user input and nutritional targets.

### Installation

First, clone the repository and install dependencies:

```bash
git clone https://github.com/ashraja941/BrokenBasket.git

cd BrokenBasket
```

Install dependencies in the `frontend` and `backend` directories:

```bash
cd ./frontend

yarn install
```

```bash
cd ../backend

poetry install
```
If there are issues importing the correct versions of each library, the versions that worked for me are listed in the requirements.txt under the backend folder. Be sure to create a virtual environment for this project. 



## MongoDB Database

Create a .env.local file in the frontend folder.
Then copy paste this to the file:

```bash
MONGODB_URI=mongodb+srv://medhamajumdar1:jPfNtpxB6KMmVKl0@cluster0.prcmuvv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

It should show while running yarn dev that the GET and POST was 200. Otherwise you are facing errors.

## Database Setup
The code to populate the astradb Database is [here](./Testing/Create_database.ipynb)

## Environment & Secrets
Copy the [`.env.example`](./backend/.env.example) file to `.env` inside the `backend` directory.

LangSmith keys are optional, but highly recommended if you plan on developing this application further.

The `OPENAI_API_KEY` is required. Get your OpenAI API key from the [OpenAI dashboard](https://platform.openai.com/login?launch).

[Sign up/in to LangSmith](https://smith.langchain.com/) and get your API key.

Free LLM use through groq is available [here](https://console.groq.com/landing/try-groq?gad_source=1&gbraid=0AAAAAoNZBHGuiiTKZDLxPDG8uF-3IkhoH&gclid=Cj0KCQjwh_i_BhCzARIsANimeoFq5hQtFXp1kMHRrs4x8RGffADRhNoXnWkc6_mCC2R3CXWInmsRjUUaAiZoEALw_wcB)

Create a database using astraDB [here](https://www.datastax.com/resources/datasheet/datastax-astra?journey=cassandra)


## Running the App

```bash
cd ./frontend

yarn dev
```

This will start a development server on [`http://localhost:3000`](http://localhost:3000).

Then, in a new terminal window:

```bash
cd ../backend

poetry run start
```

