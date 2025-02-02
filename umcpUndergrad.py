from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

chromedriver_path = '/Users/usman/Downloads/chromedriver-mac-x64 3/chromedriver'
driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path))
driver.get('https://app.testudo.umd.edu/soc/search?courseId=&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on')

wait = WebDriverWait(driver, 15)

# Open text files for storing scraped data
with open('undergraduate_courses2.txt', 'w') as ugrad_course_file, open('undergraduate_professors_list2.txt', 'w') as ugrad_professor_file:
    professors_set = set()

    # Function to select Fall 2024 term and Undergraduate level
    def select_fall_2024_and_undergrad_level():
        try:
            # Select Fall 2024 term
            term_select = wait.until(EC.presence_of_element_located((By.ID, "term-id-input")))
            term_options = term_select.find_elements(By.TAG_NAME, "option")
            for option in term_options:
                if option.get_attribute("value") == "202408":  # Fall 2024 value
                    option.click()
                    print("Fall 2024 term selected.")
                    break

            # Select Undergraduate level
            ugrad_radio = wait.until(EC.element_to_be_clickable((By.ID, "ugrad-level-radio-button")))
            ugrad_radio.click()
            print("Undergraduate level selected.")

            # Submit the form by pressing Enter
            ugrad_radio.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"Error selecting Fall 2024 or Undergraduate level: {e}")

    # Function to check for the "No Courses" message
    def check_no_courses_message():
        try:
            no_courses_message = driver.find_element(By.CSS_SELECTOR, '.no-courses-message')
            if no_courses_message.is_displayed():
                print("No courses found for this department, skipping to next.")
                return True
        except Exception:
            pass
        return False

    # Function to scrape undergraduate courses and professors
    def scrape_courses_and_professors():
        # Extract undergraduate course codes, titles, and professors
        courses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.course')))
        for course in courses:
            try:
                # Split course code and add space between prefix and number
                course_code = course.find_element(By.CSS_SELECTOR, '.course-id').text.strip()
                course_prefix, course_number = course_code[:4], course_code[4:]  # Assumes course prefix is 4 characters
                formatted_course_code = f"{course_prefix} {course_number}"

                course_title = course.find_element(By.CSS_SELECTOR, '.course-title').text.strip()
                ugrad_course_file.write(f"{formatted_course_code} {course_title}\n")
                print(f"Scraped course: {formatted_course_code} - {course_title}")

                # Extract professor information
                professors_found = False
                try:
                    # Find and click "Show Sections" if available
                    show_sections_button = course.find_element(By.CSS_SELECTOR, '.toggle-sections-link-text')
                    driver.execute_script("arguments[0].scrollIntoView(true);", show_sections_button)
                    show_sections_button.click()

                    # Extract professor names
                    for professor in course.find_elements(By.CSS_SELECTOR, '.section-instructor'):
                        professor_name = professor.text.strip()
                        if professor_name and professor_name not in professors_set:
                            professors_set.add(professor_name)
                            ugrad_professor_file.write(f"{professor_name}\n")
                            print(f"Scraped professor: {professor_name}")
                            professors_found = True
                except Exception:
                    print(f"No sections found for {course_code}, skipping professor extraction.")

                # Log if no professors were found
                if not professors_found:
                    print(f"No professor found for {course_code}.")

            except Exception as e:
                print(f"Error scraping course: {e}")

    # Function to iterate through all departments
    def iterate_departments():
        try:
            departments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.course-prefix.row a')))
        except Exception as e:
            print(f"Error fetching department links: {e}")
            return

        for index, department in enumerate(departments):
            retries = 3
            while retries > 0:
                try:
                    print(f"Navigating to department {index + 1}/{len(departments)}")
                    departments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.course-prefix.row a')))
                    department_url = departments[index].get_attribute('href')
                    driver.get(department_url)

                    # Select Fall 2024 term and Undergraduate level
                    select_fall_2024_and_undergrad_level()

                    # Check if no courses are found for Undergraduate level
                    if check_no_courses_message():
                        driver.get('https://app.testudo.umd.edu/soc/search?courseId=&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on')  # Return to department list
                        time.sleep(1)
                        break  # Skip to next department

                    # Scrape undergraduate courses and professors
                    scrape_courses_and_professors()
                    break  # Proceed with next department after scraping
                except Exception as e:
                    print(f"Retrying... Error navigating to department: {e}")
                    retries -= 1
                    if retries == 0:
                        print(f"Failed to navigate to department {index + 1}, skipping...")
                        continue

            # Navigate back to the department list (home page)
            try:
                driver.get('https://app.testudo.umd.edu/soc/search?courseId=&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on')
                time.sleep(1)  # Wait for page reload
            except Exception as e:
                print(f"Error navigating back to department page: {e}")

    # Start iterating through departments
    iterate_departments()

# Close the browser after scraping
driver.quit()