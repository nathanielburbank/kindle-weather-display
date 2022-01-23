#!/usr/bin/python3

# Kindle Weather Display
# Matthew Petroff (http://mpetroff.net/)
# September 2012

from xml.dom import minidom
import datetime
import codecs

import datetime
from astral.sun import sun
from astral.geocoder import database, lookup
import os
import sys
import re
import lxml

import subprocess
import urllib.request
from bs4 import BeautifulSoup
import datetime
import textwrap


from urllib.request import urlopen


#
# Geographic location
#

latitude = 38.8840329
longitude = -77.0083273


#
# Download and parse weather data
#

# Fetch data (change lat and lon to desired location)

city = lookup("Washington DC", database())
s = sun(city.observer, date=datetime.date.today(), tzinfo=city.timezone)


url1 = (
    "http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat="
    + str(latitude)
    + "&lon="
    + str(longitude)
    + "&format=24+hourly&numDays=4&Unit=e"
)

url2 = f"https://forecast.weather.gov/MapClick.php?lat=38.895&lon=-77.0373&unit=0&lg=english&FcstType=dwml"

weather_xml = urlopen(url1).read()
weather_xml_forcast = urlopen(url2).read()
dom = minidom.parseString(weather_xml)
dom2 = minidom.parseString(weather_xml_forcast)


xml_current_temperatures = dom2.getElementsByTagName("temperature")
for item in xml_current_temperatures:
    if item.getAttribute("type") == "apparent":
        values = item.getElementsByTagName("value")

current_temp = values[0].firstChild.nodeValue


xml_current_text_forcasts = dom2.getElementsByTagName("wordedForecast")
for item in xml_current_text_forcasts:
    values = item.getElementsByTagName("text")

text_forcasts = [values[i].firstChild.nodeValue.strip() for i in range(len(values))]

xml_timelayouts = dom2.getElementsByTagName("time-layout")
len(xml_timelayouts)

choosen_idx = 0
for item in xml_timelayouts:
    layout_keys = item.getElementsByTagName("layout-key")
    for idx, lk in enumerate(layout_keys):
        if lk.firstChild.nodeValue == "k-p12h-n13-1":
            choosen_idx = idx

timelayout = xml_timelayouts[choosen_idx].getElementsByTagName("start-valid-time")

tp_names = [tl.getAttribute("period-name") for tl in timelayout]

txt_weather = []
for tp_name, fcast in zip(tp_names, text_forcasts):
    txt_weather.append(f"{tp_name}: {fcast}")

txt_weather = txt_weather[:2]


items = dom2.getElementsByTagName("data")
for item in items:
    if item.getAttribute("type") == "current observations":
        current_conds = item
        break

icon_link = current_conds.getElementsByTagName("icon-link")[0].firstChild.nodeValue
icon_link

weather_summary = current_conds.getElementsByTagName("weather-conditions")[
    0
].getAttribute("weather-summary")


# list of NWS icons: https://www.weather.gov/forecast-icons
# Parse temperatures
xml_temperatures = dom.getElementsByTagName("temperature")
highs = [None] * 4
lows = [None] * 4
for item in xml_temperatures:
    if item.getAttribute("type") == "maximum":
        values = item.getElementsByTagName("value")
        for i in range(len(values)):
            highs[i] = int(values[i].firstChild.nodeValue)
    if item.getAttribute("type") == "minimum":
        values = item.getElementsByTagName("value")
        for i in range(len(values)):
            lows[i] = int(values[i].firstChild.nodeValue)

# Parse icons
xml_icons = dom.getElementsByTagName("icon-link")
icons = [None] * 4
for i in range(len(xml_icons)):
    icons[i] = (
        xml_icons[i]
        .firstChild.nodeValue.split("/")[-1]
        .split(".")[0]
        .rstrip("0123456789")
    )

# Parse dates
xml_day_one = dom.getElementsByTagName("start-valid-time")[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, "%Y-%m-%d")


#
# Preprocess SVG
#

# Open SVG to process
output = codecs.open("weather-script-preprocess.svg", "r", encoding="utf-8").read()

# Insert icons and temperatures

one_day = datetime.timedelta(days=1)
days_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

template_vars = {
    "TODAY_DATE": datetime.datetime.now().strftime("%A, %B %d"),
    "SRISE": s["sunrise"].strftime("%-I:%M %p"),
    "SSET": s["sunset"].strftime("%-I:%M %p"),
    "ICON_ONE": icons[0],
    "ICON_TWO": icons[1],
    "ICON_THREE": icons[2],
    "ICON_FOUR": icons[3],
    "C00": str(current_temp),
    "CURR_COND": str(weather_summary),
    "H10": str(highs[0]),
    "H20": str(highs[1]),
    "H30": str(highs[2]),
    "H40": str(highs[3]),
    "L10": str(lows[0]),
    "L20": str(lows[1]),
    "L30": str(lows[2]),
    "L40": str(lows[3]),
    "DAY_THREE": days_of_week[(day_one + 2 * one_day).weekday()],
    "DAY_FOUR": days_of_week[(day_one + 3 * one_day).weekday()],
    "TXT_LINE_1": "",
    "TXT_LINE_2": "",
    "TXT_LINE_3": "",
    "TXT_LINE_4": "",
    "TXT_LINE_5": "",
    "TXT_LINE_6": "",
}


wraped_text = []
for forcast in txt_weather:
    wraped_text += textwrap.wrap(forcast, width=55)

for idx, l in enumerate(wraped_text):
    template_vars[f"TXT_LINE_{str(idx+1)}"] = l

output = output.format(**template_vars)

# Write output
codecs.open("weather-script-output.svg", "w", encoding="utf-8").write(output)
