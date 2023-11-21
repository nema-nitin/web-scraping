import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
import time

options = ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome()
location = []
URL = "https://www.livabl.com"
driver.get(URL)
element = driver.find_element(By.ID, "CanCities")
element_html = element.get_attribute('outerHTML')
soup = BeautifulSoup(element_html, "html.parser")
res = soup.find_all("a")
for r in res:
    obj = {
        "location": r.text.strip(),
        "link": f"{URL}{r["href"]}"
    }
    location.append(obj)

def get_project_list(link):
    projects = []
    driver.get(link)
    time.sleep(2)
    element = driver.find_element(By.CSS_SELECTOR, "div.results")
    element_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(element_html, "html.parser")
    data1 = soup.find('ul')
    for li in data1.find_all("li"):
        result = li.select_one(".card")
        summary_element = li.find('div', class_='summaryline')
        summary_text = summary_element.get_text(strip=True)
        area = ''
        if summary_text != 'NULLNULL':
            summary_text1 = summary_text.split("bd")
            bed = summary_text1[0].strip() + " bd"
            if len(summary_text1) > 1: 
                area = summary_text.split("bd")[1].strip()
        address = result.select_one(".address").text.strip()
        if address != 'NULL':
            address = address.split(",")
        
        build = result.select_one(".build").text.strip()
        if build != 'NULL':
            build = build.split("by")
        
        movein = li.find_all('div', {'class': 'movein'})[1].text.strip()
        if movein != 'NULL':
            movein = movein.split(" ")
        devObj = {
            'Street Name': address[0].strip() if address != 'NULL' else '',
            'Project': result.select_one(".name").text.strip(),
            'Developers': build[1].strip() if len(build) > 1 else '',
            'City': address[1].strip() if address != 'NULL' else '',
            'Province': address[2].strip() if address != 'NULL' and len(address) > 2 else '',
            'Country': 'Canada',
            'Postal Code': '',
            'Completion': movein[2].strip() if movein != 'NULL' and len(movein) > 2 else '',
            'Building Type': build[0].strip(),
            'Num Floors': '',
            'Status': movein[2].strip() if movein != 'NULL' and len(movein) > 2 else '',
            'Brochure URL': '',
            'Photos': f"{URL}{result["href"]}",
            'Price': result.select_one(".price").text.strip(),
            'Bed': bed,
            'Area': area,
            'Unit Url': f"{URL}{result["href"]}"
        }
        projects.append(devObj)
    return projects
units = []
for i in range(len(location)):
    projects = get_project_list(location[i]['link'])
    # nextBtn = driver.find_element(By.CSS_SELECTOR, "a.next-button")
    # button_html = nextBtn.get_attribute("outerHTML")
    # print(button_html, 'asasasaassasasasasasaassasasasaasasasa')
    # nextBtn.click()
    # time.sleep(20)
    # url = driver.current_url
    # moreProjects = []
    # if url is not None and url != "":
    #     moreProjects = get_project_list(url)
    
    # projects.extend(moreProjects)
    units.extend(projects)
    
print(units)

csv_columns = ['Street Name','Project','Developers', 'City', 'Province', 'Country', 'Postal Code', 'Completion', 
               'Building Type', 'Num Floors', 'Status', 'Brochure URL', 'Photos', 'Price', 'Bed', 'Area', 'Unit Url']
csv_file = "Units.csv"
try:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in units:
            writer.writerow(data)
except IOError:
    print("I/O error")

driver.quit()

