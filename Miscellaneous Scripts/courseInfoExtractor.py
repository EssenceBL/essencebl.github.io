'''
This is an UNSAFE web scraping script that collects information about the courses offered by the HKU Math Department

@author : Shaheer Ziya
@version : 1.0
@date : 12 Aug, 2023
'''

import requests                     # Manage HTTP requests
from bs4 import BeautifulSoup       # Parse HTML
import re                           # Regular Expressions
import csv                          # Read and write CSV files
from tqdm import tqdm               # Progress Bar
import urllib3                      # Disable SSL Warnings
import time                         # Sleep


# This unfortunately needs to be done, since the HKU Math Department website uses expired certificates
urllib3.disable_warnings()


def getAvailableCourses() -> list[tuple[str, bool]]:
    '''
    Return a list of tuples containing the course code and whether it is offered in the year
    '''
    
    # The page containing the list of all HKU Math courses 
    URL = r"https://hkumath.hku.hk/MathWWW/ucourse.php"

    soup = BeautifulSoup(requests.get(URL).content, "html.parser")

    courseTable = soup.find("div", class_="rte-img-content").find("table")

    # A list storing the course code and whether it is offered in the year
    courseList = []
    
    for currCourse in courseTable.getText().split("\n")[2:-1]:
        
        if currCourse == "": continue
        elif "Not offered" in currCourse: isOffered = False
        else: isOffered = True

        courseList.append((currCourse[:8], isOffered))

    return courseList


def getCourseInfo(courseCodeTag: str) -> dict:
    
    URL = rf"https://webapp.science.hku.hk/sr4/servlet/enquiry?Type=Course&course_code={courseCodeTag}"
    page = requests.get(URL, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")

    # The Table Heading containing the course Code and Title
    courseTH = soup.find("th", class_="th_header").get_text().split(" ")
        # The last two elements are (6 Credits)
    courseCode, courseTitle = courseTH[0].strip(), " ".join(courseTH[1:-2])

    courseCo_OrdinatorInfo = soup.find(
        "th", string=re.compile("Course Co-ordinator")
    ).find_next_sibling("td").get_text().split(",")

    courseCo_OrdinatorName = courseCo_OrdinatorInfo[0].strip()
    courseCo_OrdinatorEmail = courseCo_OrdinatorInfo[1].split("< ")[-1].strip().replace(" >", "")
    courseObjectives = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(5) > td").get_text().strip()
    courseContents = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(6) > td").get_text().strip().split("- ")[1:]
    coursePrereqs = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(8) > td").get_text().strip()
    courseReadings = soup.find("table", class_="courseDetails").select_one("tr:nth-of-type(18) > td").get_text().strip()

    courseDict = {
        "Course Code": courseCode, "Course Title": courseTitle,
        "Course Co-Ordinator Name": courseCo_OrdinatorName, "Course Co-Ordinator Email": courseCo_OrdinatorEmail,
        "Course Objectives": courseObjectives,
        "Course Prerequisites": coursePrereqs, "Course Readings": courseReadings,
        "Course Contents": courseContents
    }

    return courseDict


def main():
    
    courses = getAvailableCourses()

    with open("courseInfo.csv", "w") as csvFile:
        field_names = [
            "Course Code", "Course Title", "Course Co-Ordinator Name", "Course Co-Ordinator Email",
            "Course Objectives", "Course Prerequisites", "Course Readings", "Course Contents"
        ]

        csvWriter = csv.DictWriter(csvFile, fieldnames=field_names)

        csvWriter.writeheader()        
        for i in tqdm(range(len(courses)), desc="Progress"):

            # Skip CC courses
            if "CC" in courses[i][0]: continue
            # Skip courses not offered in the year
            if courses[i][1]:
                csvWriter.writerow(getCourseInfo(courses[i][0]))
            else:
                time.sleep(0.1)

        csvFile.close()


main()
