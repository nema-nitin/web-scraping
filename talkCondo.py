import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
import re

options = ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome()
condos = []
URL = "https://www.talkcondo.com/city/toronto/"
driver.get(URL)
element = driver.find_element(By.CSS_SELECTOR, "div.projects")
element_html = element.get_attribute('outerHTML')
soup = BeautifulSoup(element_html, "html.parser")
projects = soup.find_all("div", {'class': 'project project-card'})
for proj in projects:
    address = proj.select_one(".project-location")
    if address != None:
        address = proj.select_one(".project-location").text.strip().split(",")
    
    projDetail = proj.select_one(".project-title")

    developers = proj.select_one(".project-developers")
    developer = ''
    if developers != None:
        developers = proj.select_one(".project-developers").text.strip()
        dev = re.findall(r'(?<=By )\b[^()]+\b', developers)[0]

    priceFrom = proj.select_one(".project-pricedfrom")
    if priceFrom != None:
        priceFrom = proj.select_one(".project-pricedfrom").text.strip()

    area = proj.select_one(".project-sqfootage")
    if area != None:
        area = proj.select_one(".project-sqfootage").text.strip()

    completionDate = proj.select_one(".project-occupancydate")
    if completionDate != None:
        completionDate = proj.select_one(".project-occupancydate").text.strip()
    
    status = proj.select_one(".floorplans-available")
    if status != None:
        status = proj.select_one(".floorplans-available").text.strip()
        if "." in status:
            projStatus = status.split(".")[0].strip()
        else:
            projStatus = status

    photo = proj.find('img')

    devObj = {
        'Street Name': address[0].strip(),
        'Project': projDetail.text.strip(),
        'Developers': dev,
        'City': address[1].strip(),
        'Province': 'Ontario',
        'Country': 'Canada',
        'Postal Code': '',
        'Completion': completionDate,
        'Building Type': 'Condo',
        'Num Floors': '',
        'Status': projStatus,
        'Brochure URL': '',
        'Photos': photo["src"],
        'Price': priceFrom,
        'Bed':  '',
        'Area': area,
        'Unit Url': projDetail["href"]
    }
    condos.append(devObj)


csv_columns = ['Street Name','Project','Developers', 'City', 'Province', 'Country', 'Postal Code', 'Completion', 
               'Building Type', 'Num Floors', 'Status', 'Brochure URL', 'Photos', 'Price', 'Bed', 'Area', 'Unit Url']
csv_file = "talkCondo_Condos.csv"
try:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in condos:
            writer.writerow(data)
except IOError:
    print("I/O error")

###################################################################################
project_info = []
for condo in condos:
    condo_url = condo["Unit Url"]
    driver.get(condo_url)
    # time.sleep(3)
    proj_desc = driver.find_element(By.CSS_SELECTOR, "div.card__content")
    proj_desc_element= proj_desc.get_attribute('outerHTML')
    proj_desc_soup = BeautifulSoup(proj_desc_element, "html.parser")
    proj_desc = proj_desc_soup.text.strip() 

    proj_overview = driver.find_element(By.CSS_SELECTOR, "div.overview")
    proj_overview_element= proj_overview.get_attribute('outerHTML')
    proj_overview_soup = BeautifulSoup(proj_overview_element, "html.parser")
    proj_data = proj_overview_soup.find_all("div", {"class": "card__subitem"})

    project_status = BeautifulSoup(proj_data[4].prettify(), "html.parser").find('div', class_='card__subitem').get_text(strip=True)[18:]
    project_building_type = BeautifulSoup(proj_data[5].prettify(), "html.parser").find('div', class_='card__subitem').get_text(strip=True)[13:]
    project_parking = BeautifulSoup(proj_data[9].prettify(), "html.parser").find('div', class_='card__subitem').get_text(strip=True)[7:]
    project_locker = BeautifulSoup(proj_data[10].prettify(), "html.parser").find('div', class_='card__subitem').get_text(strip=True)[12:]

    deposit_st = ''
    print(len(proj_data), '---------------------')
    if len(proj_data) > 12:
        proj_deposit = proj_data[12].find_all("span")
        if proj_deposit:
            for i in range(1, len(proj_deposit)):
                deposit_st += proj_deposit[i].text.strip() + " || "

    projInfoObj = {
        'Description': proj_desc,
        'Status': project_status,
        'Parking Included': 'Yes' if project_parking else 'No',
        'Parking Price': project_parking,
        'Locker Included': 'Yes' if project_locker else 'No',
        'Locker Price': project_locker,
        'Building Type': project_building_type,
        'Deposit Structure': deposit_st
    }
    project_info.append(projInfoObj)

print(project_info, '----------------------')

csv_unit_colums = ['Description', 'Status', 'Parking Included', 'Parking Price', 'Locker Included', 'Locker Price', 
                   'Building Type', 'Deposit Structure']
csv_file = "talkCondo_Project_Info.csv"
try:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_unit_colums)
        writer.writeheader()
        for data in project_info:
            writer.writerow(data)
except IOError:
    print("I/O error")


driver.quit()

