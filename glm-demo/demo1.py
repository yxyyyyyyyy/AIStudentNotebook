from zhipuai import ZhipuAI
import os
# 使用GLM自己的

# api_key = os.getenv('API_KEY')
# print(api_key)
client = ZhipuAI(api_key='0884a4262379e6b9e98d08be606f2192.TOaCwXTLNYo1GlRM')

response = client.chat.completions.create(
    model='glm-4-0520',
    messages=[
        {'role': "user", 'content': '请介绍一下大模型的定义？'}
    ],
    stream=True
)

# 流试的输出
for s in response:
    print(s.choices[0].delta.content)

# print(response)
#
# print(response.choices[0].message.content)