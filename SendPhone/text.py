import requests

API_ID = 'C74785358'
API_KEY = '0cf58fd6c94c17690113387e21f908d1'

def send_sms(phone: str, code: str):
    url = "http://106.ihuyi.com/webservice/sms.php?method=Submit"
    payload = {
        "account": API_ID,
        "password": API_KEY,
        "mobile": phone,
        "content": f"您的验证码是：{code}。请不要把验证码泄露给其他人。"
    }

    response = requests.post(url, data=payload)
    print(response.text)

# 示例
send_sms("15763375706", "123456")
