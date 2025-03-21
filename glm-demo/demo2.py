from openai import OpenAI
import os
# 使用OpenAI的API

# api_key = os.getenv('API_KEY')
# print(api_key)
client = OpenAI(
    api_key='0884a4262379e6b9e98d08be606f2192.TOaCwXTLNYo1GlRM',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)

response = client.chat.completions.create(
    model='glm-4-0520',
    messages=[
        {'role': "user", 'content': '北京天气怎么样？'}
    ],
    # stream=True
)


print(response)

print(response.choices[0].message.content)