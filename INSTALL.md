# Setup and Installation Procedure

### Step 1: Clone the repository from GitHub
```bash
git clone https://github.com/NCSU-CSC510-Group-BHAKQH/CSC-510-Project2-PopcornPicks
```
### Step 2: Install required packages with pip
```bash
cd CSC-510-Project2-PopcornPicks
pip install -r requirements.txt
```
### Step 3: Get a TMDB API key at their website [here](https://www.themoviedb.org/signup)
- Your API key can be generated under the settings page after you create your account.

### Step 4: Create a `.env` file to place the API key in
```bash
touch app/src/.env
vim .env
...
TMDB_API_KEY=...
```
### Step 5: Setup DB and start server
```bash
python3 app/init_db.py
python3 app/run.py
```
### Step 6: You can now open the website on [localhost](http://127.0.0.1:8000/)
