import json
import os

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate
from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_PREFIX, SYNTHETIC_FEW_SHOT_SUFFIX
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo3"
os.environ["TAVILY_API_KEY"] = "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"

# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat",
    temperature=0 # 温度,情感分类不应该有多样性
)


# 定义 Classification 类
class Classification(BaseModel):
    sentiment: str = Field(..., description="文本的情感（happy, neutral, sad, anger）")
    aggressiveness: int = Field(..., description="攻击性等级（1-5）")
    language: str = Field(..., description="语言（spanish, english, french, 中文, italian）")

# 动态生成提示模板
def generate_prompt_template(model_class):
    fields = model_class.model_fields  # 使用 model_fields 替代 __fields__
    prompt_template = """
    请从以下文本中提取信息，并按 JSON 格式输出：
    """
    for field_name, field in fields.items():
        prompt_template += f"- `{field_name}`: {field.description}\n"  # 直接访问字段的 description 属性
    prompt_template += """
    文本：
    "{input}"

    直接返回 JSON 格式的结果，不要添加多余的文本。
    """
    return prompt_template

# 使用 Classification 类动态生成提示模板
tagging_prompt_template = generate_prompt_template(Classification)

# 创建 ChatPromptTemplate
tagging_prompt = ChatPromptTemplate.from_template(tagging_prompt_template)

# 组合模型 DeepSeek API 可能不支持with_structured_output
"""
with_structured_output(Classification) 这个方法会告诉 LLM 直接返回符合 Classification 这个 Pydantic 模型的 JSON 结构
DeepSeek 的 API 可能默认返回的是 纯文本格式，导致解析 JSON 失败
chain = tagging_prompt | model.with_structured_output(Classification)
"""
chain = tagging_prompt | model

# 输入文本
input_text = "Yin Xinyu is the best person in the world. She is extremely outstanding and very nice!!!!!"

# 运行
response = chain.invoke({'input': input_text})
print(response.content)