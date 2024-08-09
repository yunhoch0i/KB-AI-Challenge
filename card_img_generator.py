import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import urllib.request
import json
import openai

#이전에 생성했던 이미지 제거
pre_file_path = "./design_img.jpg"
if os.path.isfile(pre_file_path):
    os.remove(pre_file_path)

OPENAI_API_KEY = ("sk-proj-exvyGtjq5SUu2Vt3nUwcDmM-iLdEMYPHTYSTmL714cSrebkzxL7qO_T66w"
                  "T3BlbkFJ9tjQ2KPMvjHHnrvs-Dh3kYYbDm3vXh55AYJWZROTLTWsYj_99MUiQlz3cA")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

customer_name = "최윤호"
customer_consume_list = []
customer_age = 0

with open("User_DataSet.json", "r") as f:
    data_set = json.load(f)

customer_info = 0
for cur_customer_info in data_set:
    if cur_customer_info["name"] == customer_name:
        customer_info = cur_customer_info
        break

customer_age = customer_info["age"]
customer_gender = customer_info["gender"]
if customer_gender == 'M':
    customer_gender = "남성"
else:
    customer_gender = "여성"

for cur_withdrawal in customer_info["transactions_Withdrawal"]:
    if cur_withdrawal[3] not in customer_consume_list and cur_withdrawal[3] != "None":
        customer_consume_list.append(cur_withdrawal[3])

print(customer_consume_list)
query= str(customer_age) + ("세이고 성별은 " + customer_gender + "이며 " + json.dumps(customer_consume_list) + "등에 관심이 있는"
                            " 사람에게 어울리는 일러스트를 그려줘")
print(query)

response = client.images.generate(
    model="dall-e-3",
    prompt=query,
    size="1792x1024",
    quality="standard",
    n=1
)

url = response.data[0].url
img_dst = "./"
urllib.request.urlretrieve(url, img_dst+"design_img.jpg")

foreground_img = cv2.imread("card_background.png", cv2.IMREAD_UNCHANGED)
foreground_w_img = cv2.imread("card_background_w.png", cv2.IMREAD_UNCHANGED)
design_img = cv2.imread("design_img.jpg", cv2.IMREAD_UNCHANGED)

design_img = cv2.cvtColor(design_img, cv2.COLOR_BGR2RGB)
design_img = cv2.resize(design_img, dsize=(1140, 720))
foreground_img = cv2.resize(foreground_img, dsize=(1140, 720))
foreground_w_img = cv2.resize(foreground_w_img, dsize=(1140, 720))

foreground_alpha = foreground_img[:, :, 3]
foreground_rgb = foreground_img[:, :, :3]
foreground_w_alpha = foreground_w_img[:, :, 3]
foreground_w_rgb = foreground_w_img[:, :, :3]

foreground_alpha_expanded = np.expand_dims(foreground_alpha, axis=2)
foreground_alpha_expanded = np.repeat(foreground_alpha_expanded, 3, axis=2)
foreground_w_alpha_expanded = np.expand_dims(foreground_w_alpha, axis=2)
foreground_w_alpha_expanded = np.repeat(foreground_w_alpha_expanded, 3, axis=2)

result = cv2.multiply(design_img[:].astype(float), (1 - (foreground_alpha_expanded / 255)))
result += cv2.multiply(foreground_rgb.astype(float), (foreground_alpha_expanded / 255))
result = result.astype(np.uint8)

result_w = cv2.multiply(design_img.astype(float), (1 - (foreground_w_alpha_expanded / 255)))
result_w += cv2.multiply(foreground_w_rgb.astype(float), (foreground_w_alpha_expanded / 255))
result_w = result_w.astype(np.uint8)

fig = plt.figure()

ax1 = fig.add_subplot(1, 2, 1)
ax1.imshow(result)
ax1.axis("off")

ax2 = fig.add_subplot(1, 2, 2)
ax2.imshow(result_w)
ax2.axis("off")

plt.show()
