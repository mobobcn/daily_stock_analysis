# src/scanner.py
import akshare as ak
import pandas as pd
from datetime import datetime

def get_all_a_stocks():
    """获取全 A 股列表"""
    df = ak.stock_zh_a_spot_em()  # 或其他数据源
    return df[['代码', '名称', '最新价', '涨跌幅', '换手率', '市盈率-动态', '总市值']]

def filter_candidate_pool():
    all_stocks = get_all_a_stocks()
    
    candidates = []
    
    for idx, row in all_stocks.iterrows():
        code = row['代码']
        name = row['名称']
        price = row['最新价']
        
        # 获取技术数据（复用您现有的 data_provider）
        technical = get_technical_data(code)  # 假设已有函数，返回 MA5/MA10/MA20, RSI 等
        
        # 过滤条件（基于您的交易理念，适当放宽）
        conditions = [
            # 核心：接近多头或正在形成多头
            technical['ma5'] >= technical['ma10'] * 0.99 and technical['ma10'] >= technical['ma20'] * 0.99,
            # 乖离率不太极端
            abs(technical['bias_ma5']) < 10,
            # 量能有异动（放量或近期换手活跃）
            technical['turnover_rate'] > 1.5 or technical['volume_ratio'] > 1.2,
            # 估值相对合理（成长股可放宽）
            row['市盈率-动态'] < 60 or row['市盈率-动态'] == '--',
            # 排除极端小盘或问题股（可选）
            row['总市值'] > 20 * 1e8
        ]
        
        if sum(conditions) >= 4:  # 至少满足4条
            score = calculate_opportunity_score(technical, row)  # 自定义打分
            candidates.append({
                'code': code,
                'name': name,
                'price': price,
                'score': score,
                'key_reason': generate_reason(technical, row),
                'ma_status': '接近多头' if technical['ma5'] > technical['ma10'] else '缠绕中'
            })
    
    # 按分数排序，取前 20-30
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:30]
