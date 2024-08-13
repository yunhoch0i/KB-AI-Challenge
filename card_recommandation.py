import openai
import os
import json
import sys
from collections import defaultdict
from dotenv import load_dotenv
import financial_ledger_mod
import income_compare
import card_img_generator

load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = openai.OpenAI(api_key= OPENAI_API_KEY)

# JSON 파일 로드
with open('./DataSet/User_DataSet.json', 'r', encoding='UTF-8') as f:
    data = json.load(f)

# 사용자 이름으로 데이터를 검색하는 함수
def find_user_data(name, data):
    for user in data:
        if user['name'] == name:
            return user
    return None

# 소비 패턴 분석 함수
def analyze_spending(transactions):
    spending = defaultdict(int)
    for transaction in transactions:
        category = transaction[3]
        amount = int(transaction[2])
        spending[category] += amount
    return spending

# 카드 추천 함수
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

# 카테고리, 소비패턴에 따른 카드 추천
def recommend_card_based_on_input(user_input, user_name, user_data):
    # 소비 패턴 분석
    transactions = user_data.get('transactions_Withdrawal', [])
    spending = analyze_spending(transactions)
    spending_summary = "\n".join([f"{category}: {amount}원" for category, amount in spending.items()])

    prompt = (
        f"{user_name}님이 다음과 같은 질문을 하셨습니다:\n"
        f"{user_input}\n\n"
        "이 질문이 신용카드 추천과 관련이 있다면, "
        "이 소비 패턴을 기반으로 추천할 만한 KB국민카드를 알려주세요.\n"
        f"소비 패턴은 다음과 같습니다:\n"
        f"{spending_summary}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable assistant who provides recommendations based on user input and spending patterns."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# 일반 질문 처리
def gpt_general_response(user_input):
    # 기본 출력 문장 삭제
    prompt = f"{user_input}\nAnswer concisely and directly without any preamble."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 입력에 따른 정보 처리
def handle_user_input(user_name):
    user_data = find_user_data(user_name, data)

    if not user_data:
        return f"{user_name}님의 데이터를 찾을 수 없습니다."

    while True:
        user_input = input(f"{user_name}님, 질문을 입력하세요 ('종료' 입력 시 종료): ")

        if user_input.lower() == '종료':
            print("대화를 종료합니다.")
            break

        # 카테고리 및 카드 추천 처리
        recommendation = recommend_card_based_on_input(user_input, user_name, user_data)


        if "가계부" in user_input or "요약" in user_input:
            summary = financial_ledger_mod.monthly_summary(user_data, data)
            print(summary)
        elif "소득 수준" in user_input or "소득 비교" in user_input:
            answer = income_compare.compare(user_name)
            print(answer)

        elif "디자인" in user_input or "이미지" in user_input:
            card_img_generator.create_card_img(user_name)

        elif "카드" in recommendation:
            print(recommendation)

        else:
            # 일반 질문 처리
            response = gpt_general_response(user_input)
            print(response)

        sys.stdout.flush()

# 사용 시작
user_name = input("사용자의 이름을 입력하세요: ")
handle_user_input(user_name)
