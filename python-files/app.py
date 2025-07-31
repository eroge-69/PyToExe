import subprocess

# Base username
base_username = "user"

# Loop to create 10 users
for i in range(1, 11):
    username = "{0}{1}".format(base_username, i)
    command = "net user {0} /add".format(username)

    try:
        subprocess.check_call(command, shell=True)
        print("User {0} added successfully.".format(username))
    except subprocess.CalledProcessError as e:
        print("Failed to add user {0}: {1}".format(username, e))

print("All users have been added.")
