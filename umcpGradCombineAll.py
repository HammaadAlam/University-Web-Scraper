# Read the course and professor data from the first file
course_data = {}
with open('graduate_courses_and_professors6.txt', 'r') as f:
    for line in f:
        # Split the line into professor name and courses
        name, courses = line.split(", Courses: ")
        courses = courses.strip()  # Clean up any extra spaces
        course_data[name.strip()] = courses  # Store the courses associated with each professor

# Read the email data from the second file and combine with the course data
combined_data = []
with open('Allgraduate_emails.txt', 'r') as f:
    for line in f:
        # Split the line into name, email, department
        parts = line.split(", ")
        if len(parts) < 2:
            print(f"Skipping malformed line: {line}")
            continue

        name = parts[0].strip()  # First part is the name
        email = parts[1].strip()  # Second part is the email

        # Look up courses for this professor from the course_data dictionary
        courses = course_data.get(name, "Courses not found")

        # Create the combined format
        combined_line = f"{name}, Email: {email}, Courses: {courses}"
        combined_data.append(combined_line)

# Write the combined data to a new file
with open('combined_graduate_all_data.txt', 'w') as f:
    for line in combined_data:
        f.write(line + "\n")

print("Data combined and written to combined_graduate_all_data.txt")