import json
import os
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_PREFIX, SYNTHETIC_FEW_SHOT_SUFFIX
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"

model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 生成一些结构化的数据： 5个步骤
# 1、定义数据模型
class MedicalBilling(BaseModel):
    patient_id: int  # 患者ID，整数类型
    patient_name: str  # 患者姓名，字符串类型
    diagnosis_code: str  # 诊断代码，字符串类型
    procedure_code: str  # 程序代码，字符串类型
    total_charge: float  # 总费用，浮点数类型
    insurance_claim_amount: float  # 保险索赔金额，浮点数类型

# 2. 提供一些样例数据
examples = [
    {
        "example": "Patient ID: 123456, Patient Name: 张娜, Diagnosis Code: J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350, address: 山东省"
    },
    {
        "example": "Patient ID: 789012, Patient Name: 王兴鹏, Diagnosis Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120, address: 河北省"
    },
    {
        "example": "Patient ID: 345678, Patient Name: 刘晓辉, Diagnosis Code: E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250, address: 江西省"
    },
]

# 3. 创建 DeepSeek 兼容的模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 4. 创建提示模板（手动构造 prompt）
prompt_template = PromptTemplate(
    input_variables=['subject', 'extra'],
    template=(
        "请根据以下示例数据生成 {subject}：\n"
        "{examples}\n"
        "请生成 10 组数据，额外信息：{extra}。\n"
        "patient_name生成的复杂一点\n"
        "请确保输出为 JSON 格式，每条数据结构如下：\n"
        "{{'patient_id': int, 'patient_name': str, 'diagnosis_code': str, "
        "'procedure_code': str, 'total_charge': float, 'insurance_claim_amount': float, 'address': str}}\n}}"
    )
)

# 5. 手动创建数据生成器（避免 `LangChain` 的 `function_call`）
class DataGenerator:
    def __init__(self, model):
        self.model = model

    def generate(self, subject, extra, runs=10):
        # 格式化样例数据
        formatted_examples = "\n".join([ex["example"] for ex in examples])
        formatted_prompt = prompt_template.format(
            subject=subject,
            examples=formatted_examples,
            extra=extra
        )

        # 调用 DeepSeek API
        response = self.model.invoke(formatted_prompt)

        # 解析 JSON 结果
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            print("解析失败，原始返回:", response.content)
            return None

# 6. 调用生成器
generator = DataGenerator(model)
result = generator.generate(
    subject="医疗账单",
    extra="医疗总费用呈现正态分布，最小的总费用为1000",
    runs=10
)

print(result)