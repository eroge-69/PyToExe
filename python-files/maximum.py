import os

n = int(input("How many number you want to input\n"))
os.system("cls")
list = []
even = []
odd = []
nums = []

for i in range(n):
    num = int(input(f"Enter {i+1} number\n"))
    os.system("cls")
    nums.append(num)
    list.append(num)
    
max = nums[0]
min = nums[0]

for num in nums:
    if num<min:
        min = num
    elif num>max:
        max = num

print(f"lists are: {list}")
print(f"Maximum number is: {max}")
print(f"Minimum number is: {min}")