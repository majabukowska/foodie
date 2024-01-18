python -m venv C:\path_to_your_repo\venv   
venv\Scripts\activate         
pip install -r requirements.txt   
$env:OPENAI_API_KEY="your-api-key"
echo $env:OPENAI_API_KEY
cd app
flask run 
