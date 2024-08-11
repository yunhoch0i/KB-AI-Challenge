import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

with open("./DataSet/User_DataSet.json", "r") as f:
    data_set = json.load(f)


def compare(user_name):
    data_set2 = []
    for i in range(len(data_set)):
        cur_data = data_set[i]
        new_data = {}
        new_data['name'] = cur_data['name']
        new_data['age'] = cur_data['age']
        new_data['gender'] = cur_data['gender']
        tot_consume_sum = 0
        for i in range(len(cur_data['transactions_Withdrawal'])):
            tot_consume_sum += int(cur_data['transactions_Withdrawal'][i][2])
        new_data['tot_consume_sum'] = tot_consume_sum
        new_data['income'] = cur_data['incomeLevel']
        data_set2.append(new_data)

# print(data_set2)
    cur_customer_idx = 10
    cur_customer_info = data_set[cur_customer_idx]
# print(json.dumps(data_set))

    model = "gpt-3.5-turbo-0125"
    query = ("너는 지금부터 소비자들의 금융데이터를 보고 질문에 답을 해야해 금융데이터는 "
            "{고객이름, 고객나이, 성별, 고객이 총 소비한 금액, 고객의 소득 수준}으로 이루어진 리스트야"
            f"{user_name}고객과 소득 수준이 비슷한 고객들과 그들의 소비 데이터를 보고해. 데이터는 다음에 오는 데이터를 활용해" + json.dumps(data_set2))

    message = [{
        "role": "system",
        "content": "you are a helpful and kind financial advisor."
    }, {
        "role": "user",
        "content": query
    }]

    response = openai.ChatCompletion.create(model=model, messages=message)
    answer = response.choices[0].message.content
    return answer

