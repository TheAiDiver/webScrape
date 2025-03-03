
import re
import os
import json
from typing import List
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import (BaseModel,
                      Field)
load_dotenv(override=True)
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_info(text: str,
                 prompt: str):
    """
    Extract all websites/URLs from the provided text using OpenAI parse method.
    
    Args:
        text (str): Input text containing website URLs
        
    Returns:
        The parsed response or refusal message
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant specialized in extracting info from text and return in json format"
            },
            {"role": "user", "content": f""" 
            {prompt}
            ------------
            text:
            {text}

            -------------------------
            * Only return json format
            -------------------------
            """}
        ],
    )
    
    return completion.choices[0].message.content


def enhanced_json_extractor(input_data):
    """
    n8n增强型JSON提取器 - 处理各种JSON格式并提供多种输出选项
    
    Args:
        input_data: 输入数据，可以是JSON字符串、字典、列表或包含JSON的字符串
        
    Returns:
        dict: 包含处理结果的字典，具有以下结构:
            - json:
                - result: 处理结果对象
                    - data: 提取的数据项列表
                    - metadata: 关于提取数据的元信息
                    - error: 如果提取失败则包含错误信息
                - raw_items: 原始提取的数据项
    """
    # 处理函数：尝试多种方式提取JSON
    def extract_json(data):
        # 如果已经是字典或列表，直接返回
        if isinstance(data, (dict, list)):
            return data
        
        # 如果是字符串，尝试解析
        if isinstance(data, str):
            # 尝试直接解析整个字符串
            try:
                return json.loads(data)
            except:
                pass
            
            # 尝试去除代码块标记
            clean_data = re.sub(r'```(?:json)?|```', '', data).strip()
            try:
                return json.loads(clean_data)
            except:
                pass
            
            # 尝试匹配最外层的花括号内容（对象）
            json_match = re.search(r'({[\s\S]*})', data)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
                
            # 尝试匹配最外层的方括号内容（数组）
            array_match = re.search(r'(\[[\s\S]*\])', data)
            if array_match:
                try:
                    return json.loads(array_match.group(1))
                except:
                    pass
        
        # 所有尝试失败
        return None

    # 提取JSON数据
    extracted_data = extract_json(input_data)
    
    # 结果处理
    if extracted_data is None:
        # 提取失败
        result = {
            "error": "无法从输出中提取JSON数据",
            "original": str(input_data)[:200] + "..." if len(str(input_data)) > 200 else str(input_data)
        }
        items = None
    else:
        # 处理各种数据结构
        if isinstance(extracted_data, dict):
            # 检查是否有单一根键（如"distributors"）
            if len(extracted_data) == 1:
                root_key = next(iter(extracted_data))
                root_value = extracted_data[root_key]
                # 如果根值是数组，提取它
                if isinstance(root_value, list):
                    items = root_value
                    root_key_found = root_key
                else:
                    items = [extracted_data]
                    root_key_found = None
            else:
                items = [extracted_data]
                root_key_found = None
        elif isinstance(extracted_data, list):
            items = extracted_data
            root_key_found = None
        else:
            items = [extracted_data]
            root_key_found = None
        
        # 建立结果对象
        result = {
            "data": items,
            "metadata": {
                "count": len(items),
                "root_key": root_key_found,
                "data_type": type(extracted_data).__name__
            }
        }
    
    return [{
        "json": {
            "result": result,
        }
    }]


if __name__ == "__main__":
    text = "company name: 10xgenomics, email: info@10xgenomics.com, Tel: +1-800-123-4567, Fax: +1-800-123-4568"
    result = enhanced_json_extractor(extract_info(text,"帮我抓取company 还有email"))
    print(result)
