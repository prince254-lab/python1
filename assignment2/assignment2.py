# ------------------------------------------------
# Name: Prince
# Date: 4 Nov 2025
# Project: Gradebook Analyzer
# ------------------------------------------------

# this program helps to store marks of students and
# find average, grades, pass fail etc.
# we can also load data from a csv file

import csv
import statistics

print("Welcome to Gradebook Analyzer!")
print("------------------------------")
print("1. Enter student data manually")
print("2. Load data from CSV file\n")

# --- Task 2 ---
marks = {}

choice = input("Enter your choice (1 or 2): ")

if choice == "1":
    n = int(input("How many students you want to enter? "))
    for i in range(n):
        name = input(f"\nEnter name of student {i+1}: ")
        score = float(input(f"Enter marks for {name}: "))
        marks[name] = score

elif choice == "2":
    file_name = input("Enter csv file name (like marks.csv): ")
    try:
        with open(file_name, "r") as f:
            read = csv.reader(f)
            for row in read:
                if len(row) >= 2:
                    name = row[0]
                    try:
                        score = float(row[1])
                        marks[name] = score
                    except:
                        pass
        print("Data loaded successfully!\n")
    except:
        print("File not found or some error happened.")
        exit()
else:
    print("Invalid choice. please restart the program.")
    exit()

# --- Task 3: functions ---

def calc_avg(m):
    return sum(m.values()) / len(m)

def calc_median(m):
    return statistics.median(m.values())

def max_score(m):
    return max(m.values())

def min_score(m):
    return min(m.values())

avg = calc_avg(marks)
median = calc_median(marks)
highest = max_score(marks)
lowest = min_score(marks)

print("\n--- Analysis Summary ---")
print("Average Marks:", round(avg, 2))
print("Median Marks:", round(median, 2))
print("Highest Score:", highest)
print("Lowest Score:", lowest)

# --- Task 4: Grades ---

grades = {}

for name, score in marks.items():
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    grades[name] = grade

grade_count = {"A":0, "B":0, "C":0, "D":0, "F":0}

for g in grades.values():
    if g in grade_count:
        grade_count[g] += 1

print("\n--- Grade Distribution ---")
for g, c in grade_count.items():
    print(g, ":", c)

# --- Task 5: Pass Fail ---

passed = [name for name, s in marks.items() if s >= 40]
failed = [name for name, s in marks.items() if s < 40]

print("\nPassed Students:", len(passed))
print(passed)
print("Failed Students:", len(failed))
print(failed)

# --- Task 6: Table Output ---
print("\n--------------------------------")
print("Name\t\tMarks\tGrade")
print("--------------------------------")

for name in marks:
    print(f"{name}\t\t{marks[name]}\t{grades[name]}")

print("--------------------------------")

# --- User Loop ---
while True:
    again = input("\nDo you want to run again? (yes/no): ")
    if again.lower() == "yes":
        print("Please run the program again manually.")
        break
    else:
        print("Thanks for using Gradebook Analyzer!")
        break
