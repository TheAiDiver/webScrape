import re 
import pandas as pd

def single_to_dataframe(single_result,
                        normalize_columns=True):
    """
    将单个网站的抓取结果转换为pandas DataFrame
    
    Args:
        single_result (dict/list): 单个网站的抓取结果
        normalize_columns (bool): 是否规范化列名
        
    Returns:
        pandas.DataFrame: 包含抓取数据的DataFrame
    """
    # 处理空结果
    if not single_result:
        return pd.DataFrame()
    
    # 从不同的嵌套结构中提取数据
    data = None
    
    # 处理列表结构
    if isinstance(single_result, list):
        if len(single_result) > 0:
            if isinstance(single_result[0], dict) and 'json' in single_result[0]:
                # 匹配示例中的结构
                if 'result' in single_result[0]['json']:
                    if 'data' in single_result[0]['json']['result']:
                        data = single_result[0]['json']['result']['data']
                    else:
                        data = single_result[0]['json']['result']
            else:
                # 简单列表
                data = single_result
        else:
            # 空列表
            return pd.DataFrame()
            
    # 处理字典结构
    elif isinstance(single_result, dict):
        # 尝试不同的路径
        paths = [
            ['json', 'result', 'data'],
            ['json', 'result'],
            ['result', 'data'],
            ['data'],
            []  # 字典本身
        ]
        
        for path in paths:
            current = single_result
            valid_path = True
            
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    valid_path = False
                    break
            
            if valid_path:
                data = current
                break
    
    # 如果找不到有效的数据结构，返回空DataFrame
    if data is None:
        return pd.DataFrame()
    
    # 转换非列表数据为列表
    if not isinstance(data, list):
        data = [data]
    
    # 如果列表为空，返回空DataFrame
    if not data:
        return pd.DataFrame()
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 规范化列名（如果需要）
    if normalize_columns and not df.empty:
        # 简单规范化：转小写，去除特殊字符，替换空格为下划线
        normalized_cols = {}
        for col in df.columns:
            # 转小写并规范化名称
            norm_col = re.sub(r'[^\w\s]', '', col.lower()).replace(' ', '_')
            normalized_cols[col] = norm_col
        
        df = df.rename(columns=normalized_cols)
    
    return df