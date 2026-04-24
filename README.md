# Air Quality Analysis Dashboard ✨  
Dashboard interaktif untuk menganalisis pola polusi PM2.5 dan faktor meteorologi di Stasiun Aotizhongxin, Beijing (2013-2017).

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir submission
cd submission
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```
