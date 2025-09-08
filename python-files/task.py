def to_do_list():
 tasks = []
while True:
   print("1. Add Task.")
   print("2. Remove Task.")
   print("3. Show Tasks.")
   print("4. Quit.")
   choice = input("Enter Your Choice")
   if choice == "1":
     task = input("Enter Task: ")
     tasks.append(task)
   elif choice == "2":
     task = input("Enter Task to remove: ")
     if task in tasks:
     tasks.remove(task)
     else:
       print("Task not found.")
    elif choice == "3":
      print("Tasks: ")
       for task in tasks:
          print("- " + task)
     elif choice == "4":
       break
      else:
       print("Invaild Choice.")
 to_do_list()