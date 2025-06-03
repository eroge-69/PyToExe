tasks = []

def addTask(task):
  tasks.append(task)
  print("Tasks", tasks)

def deleteTask(taskIndex):
  if len(tasks) == 0:
    print("you have no tasks to be deleted")
  elif len(tasks) > 0:
    tasks.pop(taskIndex)
    print("Tasks", tasks)
  else: print("select an answer")

def showTasks():
  print("your tasks:"+tasks)

def deleteAllTasks():
  tasks.clear()


def main():
  while True:
    print("Hi what do you want to do today")
    print("Enter 1 if you want to see your tasks")
    print("Enter 2 to addTasks")
    print("Enter 3 to delete a task")
    print("Enter 4 to Delete all the tasks")

    print("what is your answer:")
    userInput = input()

    if userInput == "1": 
      print("Tasks", tasks)
    elif userInput == "2": 
      print("what is the task:")
      usersAddedTask = input()
      addTask(usersAddedTask)
    elif userInput == "3":
      print("what is the task number to delete:")
      usersTaskNumber = input()
      deleteTask(int(usersTaskNumber))
    elif userInput == "4":
      print("all tasks will be deleted!")

    else: print("happy day")

if __name__ == "__main__":
  main()
