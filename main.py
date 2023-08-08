from twilio.rest import Client
from bs4 import BeautifulSoup
import requests
import re


ACCOUNT_SID = "<account-sid-token>";
AUTH_TOKEN = "<auth-token>";
URL = "https://weather.com/weather/today/l/f890160b83d5f985b270195431638541ad2c9fb5bc40db1428c449078c223b84";
HEADERS = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
}

def convertFahrenheit(fahrenheit):
    return (fahrenheit - 32) * 5/9;


def extractTime(soup):
    FtimeSpanHeader = soup.find('span', class_='CurrentConditions--timestamp--1ybTk');
    FtimeSpan = FtimeSpanHeader.get_text(strip=True);
    FtimeSpan = re.sub(r'As of|EAT', '', FtimeSpan).strip();
    return FtimeSpan;

def extractTemp(soup):
    FparsedTempList = [];
    Fdiv = soup.find('div', {'class': 'Card--content--1GQMr CurrentConditions--content--3w3sk'})
    FtempDiv = Fdiv.find('div', {'class': 'CurrentConditions--tempHiLoValue--3T1DG'})
    FtempList = FtempDiv.find_all('span', {'data-testid': 'TemperatureValue'});

    FparsedTempList.append( round(convertFahrenheit( fahrenheit= float(FtempList[0].text.strip()[:-1]) ) , 2) );
    FparsedTempList.append( round(convertFahrenheit( fahrenheit= float(FtempList[1].text.strip()[:-1]) ) , 2) );
    

    return FparsedTempList;

def extractCondition(soup):
    Fdiv = soup.find('div', {'class': 'Card--content--1GQMr CurrentConditions--content--3w3sk'});  
    FconditionDiv = Fdiv.find('div', {'class': 'CurrentConditions--phraseValue--mZC_p'})
    return FconditionDiv.text.strip();

def extractQuality(soup):
    return soup.find('text', class_='DonutChart--innerValue--3_iFF').text;


response = requests.get(URL, HEADERS);
htmlContent = "";

if response.status_code == 200:
    htmlContent = response.content;
elif response.status_code != 200:
    raise ConnectionError("Error while requesting Web Page");

soup = BeautifulSoup(htmlContent, "html.parser");

timeSpan = extractTime(soup);
dayTemp = extractTemp(soup)[0];
nightTemp = extractTemp(soup)[1];
condition = extractCondition(soup);
qualityIndex = extractQuality(soup);

messageText = f"""
        Estimated as of {timeSpan} EAT.

Day Temperature : {dayTemp}
Night Temperature : {nightTemp}
Current Weather Condition : {condition}
Air Quality index : {qualityIndex}

""";

# Obtain the phone numbers from twilio 

client = Client(ACCOUNT_SID , AUTH_TOKEN);
message = client.messages.create(
    from_="<>",
    body=messageText,
    to="<>",
);
print(message.status)