import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://en.wikipedia.org/wiki/List_of_largest_sports_contracts"

headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
response.raise_for_status()


soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", class_="wikitable")

df = pd.read_html(str(table))[0]

sports = df
sports.index = range(1, df.shape[0] + 1)
sports["Length in years"] = sports["Length of contract"].str.split('(',expand=True)[0].str.strip()
sports["Length in years"] = sports["Length in years"].str.replace(r'[^0-9\s]','',regex=True)
sports["Contract Period"] = sports["Length of contract"].str.extract(r'\(([^)]*)\)')
sports["Contract Start"] = sports["Contract Period"].str.split(r'[–-]',expand=True)[0].str.strip()
sports["Contract End"] = sports["Contract Period"].str.split(r'[–-]', expand=True)[1].str.strip()
sports.drop(columns=["Length of contract","Ref.","Unnamed: 8"], inplace=True)
sports.rename(columns={"Average per game/event[a] (USD)": "Average per game/event (USD)"},inplace=True)
#Cleaning of the string columns
sports["Name"] = (sports["Name"]
      .str.replace(r'\[[^\]]*\]', '', regex=True)
      .str.replace(r'[^0-9A-Za-zčćČĆ\.\,\+\-\s]', '', regex=True)
      .str.replace(r'\s+', ' ', regex=True)
      .str.strip()
      .str.replace(r'R$','', regex=True)
      .str.replace('Injury', '')
)
sports["Organization"] = (sports["Organization"]
      .str.replace(r'\[[^\]]*\]', '', regex=True)
      .str.replace(r'[^0-9A-Za-z\s]', '', regex=True)
      .str.replace(r'\s+', ' ', regex=True)
      .str.strip()
)
sports["Sport"] = (sports["Sport"]
      .str.replace(r'\[[^\]]*\]', '', regex=True)
      .str.replace(r'[^0-9A-Za-z\s]', '', regex=True)
      .str.replace(r'\s+', ' ', regex=True)
      .str.strip()
)
#cleaning the currency columns
df["Contract value (USD)"] = (
    df["Contract value (USD)"]
      .astype(str)                      
      .str.replace(r"[^0-9.]", "", regex=True)  
      .astype(float)                     
)
df["Average per year (USD)"] = (
    df["Average per year (USD)"]
      .astype(str)                       
      .str.replace(r"[^0-9.]", "", regex=True) 
      .astype(float)                     
)
df["Average per game/event (USD)"] = (
    df["Average per game/event (USD)"]
      .astype(str)                     
      .str.replace(r"[^0-9.]", "", regex=True)
      .astype(float)                    
)
#custom fixes
sports["Sport"].mask(sports["Sport"] == 'American Football', 'American football', inplace=True)
sports["Organization"].mask(sports["Organization"] == 'Paris SaintGermain', 'Paris Saint-Germain',inplace=True)
#import the csv
sports.to_csv("sports_earners.csv")