Meal Plan helper

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


### Running the Application

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

### To use the MongoDB Database:

Create a .env.local file in the frontend folder.
Then copy paste this to the file:

```bash
MONGODB_URI=mongodb+srv://medhamajumdar1:jPfNtpxB6KMmVKl0@cluster0.prcmuvv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

It should show while running yarn dev that the GET and POST was 200. Otherwise you are facing errors.

### Dataset
The code to populate the astradb Database is [here](./Testing/Create_database.ipynb)

### Secrets

Copy the [`.env.example`](./backend/.env.example) file to `.env` inside the `backend` directory.

LangSmith keys are optional, but highly recommended if you plan on developing this application further.

The `OPENAI_API_KEY` is required. Get your OpenAI API key from the [OpenAI dashboard](https://platform.openai.com/login?launch).

[Sign up/in to LangSmith](https://smith.langchain.com/) and get your API key.

Free LLM use through groq is available [here](https://console.groq.com/landing/try-groq?gad_source=1&gbraid=0AAAAAoNZBHGuiiTKZDLxPDG8uF-3IkhoH&gclid=Cj0KCQjwh_i_BhCzARIsANimeoFq5hQtFXp1kMHRrs4x8RGffADRhNoXnWkc6_mCC2R3CXWInmsRjUUaAiZoEALw_wcB)

Create a database using astraDB [here](https://www.datastax.com/resources/datasheet/datastax-astra?journey=cassandra)
