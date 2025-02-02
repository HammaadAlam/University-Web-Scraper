from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chromedriver_path = '/Users/usman/Downloads/chromedriver-mac-x64 3/chromedriver'
directory_url = 'https://identity.umd.edu/search'

driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path))
wait = WebDriverWait(driver, 10)

# Function to process professors from a file and store emails in another file
def process_professors(professor_file, email_file):
    with open(professor_file, 'r') as file, open(email_file, 'w') as email_out_file:
        for line in file:
            try:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                # Parse professor name and department from the line
                parts = line.split(":")
                professor_name = parts[0].strip()
                course_department = parts[1].strip() if len(parts) > 1 else ""

                # Navigate to the directory search page
                driver.get(directory_url)

                # Find search input and enter the professor's name
                search_input = wait.until(EC.presence_of_element_located((By.ID, 'basicSearchInput')))
                search_input.clear()
                search_input.send_keys(professor_name)

                # Locate Search button and click it
                search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="basicSearch"][value="Search"]')))
                search_button.click()

                # Check department and email
                department_name = driver.find_element(By.CSS_SELECTOR, '.deptName').text.strip()

                if course_department in department_name:
                    email = driver.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]').text.strip()
                    # Write to file in the format: Name, Email, Department Name
                    email_out_file.write(f"{professor_name}, {email}, {department_name}\n")
                else:
                    email_out_file.write(f"{professor_name}, Department mismatch or not found\n")

            except Exception as e:
                print(f"Failed to find email for {professor_name}: {e}")
                email_out_file.write(f"{professor_name}, Failed to find email, Failed to find department\n")

# Process undergraduate professors
process_professors('undergraduate_professors_list2.txt', 'undergraduate_emails_no_matching.txt')

# Process graduate professors
process_professors('graduate_professors_list2.txt', 'graduate_emails_no_matching.txt')

# Close the browser after processing all professors
driver.quit()