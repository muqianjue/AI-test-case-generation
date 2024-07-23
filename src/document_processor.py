#需求提取，提取
import httpx

from DocumentExtractor import DocumentExtractor
from xinference.client import RESTfulClient


class DocumentProcessor:
    def __init__(self):
        self.client = RESTfulClient("http://10.12.3.31:9997")
        self.model = self.client.get_model("Qwen2-72B-Instruct-GPTQ-Int4")
        self.extract_image = False

    def extract_text_table_img(self, file_path):
        extractor = DocumentExtractor(file_path)
        extractor.extract_image = self.extract_image
        extract_title, extracted_content = extractor.extract_document()
        return extract_title, extracted_content

    async def qwen_extract_requirements(self,title, extract_content):
        json = {
            "model": "Qwen/Qwen2-72B-Instruct",
            "max_tokens": 15000,
            "temperature": 0.5,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": [
                "<|im_end|>",
                "<|im_start|>"
            ],
            "messages": [
                {
                    "content": f"提取以下需求文档内容中的需求信息："
                               f"需求名称列表：{title}\n"
                               f"需求名称列表中各个需求对应的文本、图像、和表格信息{extract_content}\n"
                               f"输出格式：表格，分为需求名称、需求说明，总共两列。",
                    "role": "user"
                }
            ],
            "repetitive_penalty": 1
        }
        headers = {'Authorization': 'Bearer c9bd37061c2a92ea4d524aab6fd94d36aa108701f95811d3d2bbb8e41d0ff8d9'}
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.together.xyz/v1/chat/completions", json=json, headers=headers,
                                         timeout=300)
            response.raise_for_status()
            requirement_info = response.json()["choices"][0]["message"]["content"].strip()
            print(json)
            print('第一次大模型的生成', requirement_info)
            return requirement_info