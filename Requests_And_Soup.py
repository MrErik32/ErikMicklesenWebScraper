import requests
from bs4 import BeautifulSoup

#Get page data from Weather Forecast Page

page = requests.get("https://forecast.weather.gov/MapClick.php?lat=37.7772&lon=-122.4168")
soup = BeautifulSoup(page.content, 'html.parser')

#Find seven day forecast
seven_day = soup.find(id="seven-day-forecast")
forecast_items = seven_day.find_all(class_= "tombstone-container")
first_forecast = forecast_items[0]
print(first_forecast.prettify())
print("\n")

#Extract information from page
period = first_forecast.find(class_="period-name").get_text()
short_desc = first_forecast.find(class_="short-desc").get_text()
temp = first_forecast.find(class_="temp").get_text()

print(period)
print(short_desc)
print(temp)

#Extract title of forecast image
img = first_forecast.find("img")
desc = img['title']
print(desc)
print("\n")

period_tags = seven_day.select(".tombstone-container .period-name")
periods = [pt.get_text() for pt in period_tags]
print(periods)