import ast

# 从命令行接收输入
input_str = input("请输入列表数据（格式：nums=[1,2,3,4,5]）: ").strip()

# 提取等号后面的部分
if '=' in input_str:
    # 分割变量名和列表字符串
    var_name, list_str = input_str.split('=', 1)
    var_name = var_name.strip()
    
    # 验证变量名
    if var_name != "nums":
        print(f"错误：输入应以 'nums=' 开头，检测到 '{var_name}='")
        nums = []
    else:
        try:
            # 安全解析列表
            nums = ast.literal_eval(list_str.strip())
            
            # 验证结果类型
            if not isinstance(nums, list):
                print(f"错误：解析结果不是列表，而是 {type(nums).__name__}")
                nums = []
        except (SyntaxError, ValueError) as e:
            print(f"解析错误: {e}")
            nums = []
else:
    print("错误：输入格式不正确，缺少等号")
    nums = []

Length = len(nums) - 1
temp = 0
L = -1
#L是递减的下标
for i in range(len(nums)-1):
    if nums[Length-i-1] < nums[Length-i]:
        L = Length-i-1
        break
#如果没有找到 整个倒序一下就好了
if L < 0:
    nums = nums.reverse()
    print(nums)
    
#如果找到了 找到这个数右侧比这个数大的小值的index
Min = nums[L+1]
index = L+1
for i in range(L+1,len(nums)):
    if nums[i] < Min and nums[i] > nums[L]:
        index = i
        Min = nums[i]

temp = nums[index]
nums[index] = nums[L]
nums[L] = temp
A = nums[L+1:]
A.sort(reverse=False)
nums[L+1:] = A
print(nums)
