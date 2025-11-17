<h1>WorldLink AI Chatbot</h1>

<h2>Prerequisites</h2>
<ul>
  <li>Python 3.11+</li>
  <li>"Desktop development with C++" Wordload in VSCode</li>
</ul>

<h2>Installation</h2>
<h3>1. Clone the repository:</h3>

```
git clone https://github.com/kvv190001/wl-ai-chatbot.git
cd wl-ai-chatbot
```

<h3>2. Create a virtual environment</h3>

```
python -m venv venv
```

<h3>3. Activate the virtual environment</h3>

```
venv\Scripts\Activate
(or on Mac): source venv/bin/activate
```

<h3>4. Install libraries</h3>

```
pip install -r requirements.txt
```

<h3>5. Add Google Gemini API Key</h3>
Create a .env file
Add your Google Gemini API Key using this format:

```
GOOGLE_API_KEY = "your-key-here"
```

<h2>Executing the scripts</h2>

- Open a terminal in VS Code

- Execute the following command:

```
python ingest_database.py
```
- Test the UI

```
python chatbot.py
```
- Run the FastAPI server

```
uvicorn chatbot_api:app --host 0.0.0.0 --port 8000
```


<h2>Update WL website knowledge</h2>

<h3>Executing the script</h3>

- Delete worldlinklabs_full_text.txt
- Execute the following command: 

```
python scrape_worldlinklabs.py
```
- Ask an AI to help clean up the data scraped, make sure it's cp1252 encoding friendly