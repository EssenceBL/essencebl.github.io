import requests
from bs4 import BeautifulSoup
import re

URL = r"https://webapp.science.hku.hk/sr4/servlet/enquiry?Type=Course&course_code=MATH2241"

# This is not the best way to do this, but it works for now
# This ignores the SSL certificate verification, and should be fixed in the future
#! DO NOT SEND SENSITIVE INFORMATION TO THIS WEBSITE
page = requests.get(URL, verify=False)

soup = BeautifulSoup(page.content, "html.parser")

# The Table Heading containing the course Code and Title
courseTH = soup.find("th", class_="th_header").get_text().split(" ")
    # The last two elements are (6 Credits)
courseCode, courseTitle = courseTH[0], " ".join(courseTH[1:-2])

courseCo_OrdinatorInfo = soup.find(
    "th", string=re.compile("Course Co-ordinator")
).find_next_sibling("td").get_text().split(",")

courseCo_OrdinatorName = courseCo_OrdinatorInfo[0].strip()
courseCo_OrdinatorEmail = courseCo_OrdinatorInfo[1].split("< ")[-1].strip().replace(" >", "")

coursePrereqs = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(8) > td").get_text().strip()

courseReadings = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(18) > td").get_text().strip()

print(courseCo_OrdinatorName, courseCo_OrdinatorEmail)
print(courseCode, courseTitle)
print(coursePrereqs)
print(courseReadings)




