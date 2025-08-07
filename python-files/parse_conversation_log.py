
import pandas as pd
import json

def parse_conversation_column(cell_data):
    try:
        # 构造 Spark 样式的 Row() 转换函数
        local_env = {
            "Row": lambda **kwargs: kwargs,
            "function": lambda **kwargs: kwargs
        }
        # 执行安全解析
        parsed = eval(cell_data, {"__builtins__": None}, local_env)

        rows = []
        for msg in parsed:
            tool_calls_raw = msg.get("tool_calls")
            tool_calls_str = ""
            if tool_calls_raw:
                calls_cleaned = []
                for call in tool_calls_raw:
                    func = call.get("function", {})
                    calls_cleaned.append({
                        "name": func.get("name", ""),
                        "arguments": func.get("arguments", ""),
                        "id": call.get("id", ""),
                        "type": call.get("type", "")
                    })
                tool_calls_str = json.dumps(calls_cleaned)

            rows.append({
                "content": msg.get("content") or "",
                "name": msg.get("name") or "",
                "role": msg.get("role") or "",
                "tool_calls": tool_calls_str
            })

        return rows
    except Exception as e:
        return [{
            "content": f"[解析失败：{str(e)}]",
            "name": "",
            "role": "",
            "tool_calls": ""
        }]

def parse_file(input_path, output_path, column=0):
    df = pd.read_excel(input_path) if input_path.endswith('.xlsx') else pd.read_csv(input_path)
    all_records = []
    for idx, row in df.iloc[:, column].items():
        all_records.extend(parse_conversation_column(row))
    output_df = pd.DataFrame(all_records)
    output_df.to_excel(output_path, index=False)
    print(f"已完成拆解，结果保存为 {output_path}")

# 示例用法（运行脚本时替换路径）：
# parse_file('df_0805.xlsx', 'parsed_output.xlsx')
