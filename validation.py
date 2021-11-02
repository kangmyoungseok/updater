from pandas.core.frame import DataFrame
import pandas as pd
from decimal import Decimal

datas = pd.read_csv('원본.csv').to_dict('records')

result_datas = []

for data in datas:
    print(data['createdAtTimestamp'])
    swap_count = Decimal(data['swap_count'])
    burn_count = Decimal(data['burn_count'])
    initial_Liquidity_Eth = Decimal(data['initial_Liquidity_Eth'])
    current_Eth = Decimal(data['current_Eth'])

    #TxCount < 2 인 경우 데이터셋에서 제거
    if((swap_count + burn_count < 2) or(swap_count == 0)):
        continue

    #초기/현재 유동성 이더가 너무 작으면 제거
    if((initial_Liquidity_Eth < 0.001)  and (current_Eth < 0.001)):
        continue

    is_rugpull2 = False
    #기존 러그풀 플래그에서 초기/현재 유동성 풀 비율을 보는 로직을 추가
    if (data['is_rugpull']):
        if ((current_Eth / initial_Liquidity_Eth) < 0.2):
            is_rugpull2 = True
    data['is_rugpull2'] = is_rugpull2


    result_datas.append(data)
DataFrame(result_datas).to_csv('result_v1.1.csv',encoding='utf-8-sig',index=False)