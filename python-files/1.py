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


temp = 0
index = 0
for i in nums:
    temp = max(i,temp-1)
    index = index + 1
    if index == len(nums):
        print("true")
        break
    if temp == 0:
        print("false")
        break