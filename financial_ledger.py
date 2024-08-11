import openai
import os
import json
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 데이터셋 로드
with open('./DataSet/User_DataSet.json', 'r', encoding='UTF-8') as f:
    data = json.load(f)

# 소비 카테고리 정의 (예: 식비, 문화생활비, 생필품 등)
CATEGORIES = {
    "식비": ["음식점", "카페", "배달"],
    "문화생활비": ["영화", "콘서트", "서적"],
    "생필품": ["마트", "편의점", "약국"],
}

def find_user_data(name, data):
    for user in data:
        if user['name'] == name:
            return user
    return None

def tag_transaction(transaction):
    # 거래 내역에 태그를 추가하는 함수
    description = transaction[1]  # 거래 설명이 두 번째 항목이라고 가정
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in description:
                return category
    return category  # 해당하는 카테고리가 없을 경우 기본값

def analyze_spending(transactions):
    spending = defaultdict(int)
    for transaction in transactions:
        category = tag_transaction(transaction)
        amount = int(transaction[2])  # 금액이 세 번째 항목이라고 가정
        spending[category] += amount
    return spending

# def compare_with_peers(user_data, data):
#     ## 비슷한 소득을 가진 사람들과 소비 및 저축을 비교
#     user_income = user_data['incomeLevel']
#     peer_spending = []
#     peer_savings = []
#
#     for peer in data:
#         if abs(peer['incomeLevel'] - user_income) <= 500000:  # 비슷한 소득 범위 설정
#             peer_spending.append(peer['total_spent'])
#             peer_savings.append(peer['savings'])
#
#     avg_peer_spending = sum(peer_spending) / len(peer_spending) if peer_spending else 0
#     avg_peer_savings = sum(peer_savings) / len(peer_savings) if peer_savings else 0
#
#     return avg_peer_spending, avg_peer_savings

def recommend_card_gpt(spending, user_name):
    spending_summary = "\n".join([f"{category}: {amount}원" for category, amount in spending.items()])
    
    prompt = (
        f"{user_name}의 소비 패턴은 다음과 같습니다:\n"
        f"{spending_summary}\n\n"
        "이 소비 패턴을 기반으로 추천할 만한 신용카드는 무엇인가요?"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who recommends credit cards based on spending patterns."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def monthly_summary(user_data, data):
    ## 사용자의 한 달 소비 내역 요약
    transactions = user_data.get('transactions_Withdrawal', [])
    spending = analyze_spending(transactions)
    # avg_peer_spending, avg_peer_savings = compare_with_peers(user_data, data)

    spending_summary = "\n".join([f"가장 많이 사용한 내역은 {category}: {amount}원" for category, amount in spending.items()])
    
    summary = (
        f"{user_data['name']}님의 이번 달 소비 내역은 다음과 같습니다:\n"
        f"{spending_summary}\n"
       # f"비슷한 소득을 가진 사람들의 평균 소비 금액은 {avg_peer_spending}원이며, 평균 저축 금액은 {avg_peer_savings}원입니다.\n"
    )
    
    return summary

def handle_user_input(user_name, data):
    user_data = find_user_data(user_name, data)
    
    if not user_data:
        return f"{user_name}님의 데이터를 찾을 수 없습니다."
    
    while True:
        user_input = input(f"{user_name}님, 질문을 입력하세요 ('종료' 입력 시 종료): ")
        
        if user_input.lower() == '종료':
            print("대화를 종료합니다.")
            break
        
        if '요약' in user_input or '가계부' in user_input:
            summary = monthly_summary(user_data, data)
            print(summary)
        else:
            # 카드 추천 또는 기타 기능
            spending = analyze_spending(user_data.get('transactions_Withdrawal', []))
            recommendation = recommend_card_gpt(spending, user_name)
            print(recommendation)

# 챗봇 시작
# user_name = input("사용자의 이름을 입력하세요: ")
# handle_user_input(user_name, data)
