# ---------------------------------------------
# Name: Prince
# Date: 4 November 2025
# Project: Daily Calorie Tracker
# ---------------------------------------------

# This small python program helps to keep track of
# how many calories you eat in a day. It will ask for
# your meals and calories, then tell if you crossed your limit.

print("Welcome to Daily Calorie Tracker!")
print("Let's check how many calories you had today.\n")

# ---------- Taking inputs ----------
meals = []
calories = []

num = int(input("How many meals did you have today? "))

for i in range(num):
    print(f"\nMeal {i+1}:")
    meal = input("Enter meal name: ")
    cal = float(input("Enter calories: "))
    meals.append(meal)
    calories.append(cal)

# ---------- Doing some calculations ----------
total = sum(calories)
average = total / len(calories)

limit = float(input("\nEnter your daily calorie limit: "))

# ---------- Checking the limit ----------
if total > limit:
    msg = "Oh no! You have crossed your calorie limit 😥"
else:
    msg = "Good job! You are within your calorie goal 😄"

# ---------- Showing results ----------
print("\n--------------------------------")
print("Meal Name\tCalories")
print("--------------------------------")

for i in range(len(meals)):
    print(meals[i], "\t", calories[i])

print("--------------------------------")
print("Total:\t\t", total)
print("Average:\t", round(average, 2))
print("--------------------------------")
print(msg)

# ---------- Saving report (optional) ----------
save = input("\nDo you want to save this report? (yes/no): ")

if save.lower() == "yes":
    file = open("my_calorie_report.txt", "w")
    file.write("My Daily Calorie Report\n")
    file.write("--------------------------\n")
    for i in range(len(meals)):
        file.write(meals[i] + " - " + str(calories[i]) + " calories\n")
    file.write("--------------------------\n")
    file.write("Total: " + str(total) + "\n")
    file.write("Average: " + str(round(average, 2)) + "\n")
    file.write(msg + "\n")
    file.close()
    print("Report saved successfully in 'my_calorie_report.txt'")
else:
    print("Okay, report not saved. Stay healthy! 🍎")
