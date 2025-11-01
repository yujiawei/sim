#!/usr/bin/env python3
import subprocess
import json
import pandas as pd
import sys

def fetch_data_and_generate_excel():
    """使用curl获取JSON数据并生成Excel文件"""

    # curl命令
    curl_command = [
        'curl',
        'https://vibe.deepminer.ai/key/list?team_id=77d06d92-fe40-4d52-a350-88b6c7eda209&page=1&size=25&sort_by=spend&sort_order=desc&return_full_object=true&include_team_keys=true&include_created_by_keys=true',
        '-H', 'accept: */*',
        '-H', 'accept-language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        '-H', 'authorization: Bearer sk-oxg3-0s7ktRAjBqwJiYfpA',
        '-H', 'content-type: application/json',
        '-b', 'token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjZiM2M3NzAtOTNkZC00MWQ4LTgyMWMtZmIwNDQ0YjcwMzA4Iiwia2V5Ijoic2stb3hnMy0wczdrdFJBakJxd0ppWWZwQSIsInVzZXJfZW1haWwiOiJ5dWppYXdlaUBtaWFvemhlbi5jb20iLCJ1c2VyX3JvbGUiOiJwcm94eV9hZG1pbiIsImxvZ2luX21ldGhvZCI6InVzZXJuYW1lX3Bhc3N3b3JkIiwicHJlbWl1bV91c2VyIjpmYWxzZSwiYXV0aF9oZWFkZXJfbmFtZSI6IkF1dGhvcml6YXRpb24iLCJkaXNhYmxlZF9ub25fYWRtaW5fcGVyc29uYWxfa2V5X2NyZWF0aW9uIjpmYWxzZSwic2VydmVyX3Jvb3RfcGF0aCI6Ii8ifQ.oUe59Mh9EEOartgPukBQcCqvRZWNSTqgP4XJOMq6s-Q',
        '-H', 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        '-s'  # silent模式，不显示进度
    ]

    try:
        # 执行curl命令
        print("正在获取数据...")
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)

        # 解析JSON响应
        data = json.loads(result.stdout)

        # 提取keys数组中的key_alias和spend字段
        if 'keys' not in data:
            print("错误：JSON响应中没有'keys'字段")
            sys.exit(1)

        # 创建列表存储提取的数据
        extracted_data = []
        for item in data['keys']:
            extracted_data.append({
                'key_alias': item.get('key_alias', ''),
                'spend': item.get('spend', 0)
            })

        print(f"成功提取 {len(extracted_data)} 条记录")

        # 创建DataFrame
        df = pd.DataFrame(extracted_data)

        # 生成Excel文件
        output_file = 'key_spend_report.xlsx'
        df.to_excel(output_file, index=False, engine='openpyxl')

        print(f"✓ Excel文件已生成: {output_file}")
        print(f"  - 总记录数: {len(extracted_data)}")
        print(f"  - 总花费: {df['spend'].sum():.2f}")

        return output_file

    except subprocess.CalledProcessError as e:
        print(f"错误：curl命令执行失败")
        print(f"错误信息: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败")
        print(f"错误信息: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_data_and_generate_excel()
