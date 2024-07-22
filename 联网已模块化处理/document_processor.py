#需求提取，提取
from word_extractor import WordExtractor
from xinference.client import RESTfulClient

class DocumentProcessor:
    def __init__(self):
        self.client = RESTfulClient("http://10.12.3.31:9997")
        self.model = self.client.get_model("Qwen2-72B-Instruct-GPTQ-Int4")

    def extract_text_table_img(self, file_path):
        extractor = WordExtractor(file_path)
        extracted_content = extractor.extract()
        return extracted_content["text_content"], extracted_content["image_content"], extracted_content["table_content"]

    async def qwen_extract_requirements(self, text, table, img):
        response = self.model.chat(
            prompt=f"提取以下需求文档内容中的需求信息："
                   f"文本内容：{text}"
                   f"表格内容：{table}"
                   f"图片内容：{img}\n"
                   f"输出格式：表格，分为序号、所属模块、所属版本、相关需求、需求说明，总共五列。",
            system_prompt="你是一个专业的需求文档信息提取助手。",
            chat_history=[],
            generate_config={
                "max_tokens": 15000,
                "temperature": 0.5,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|im_end|>", "<|im_start|>"]
            }
        )
        if isinstance(response, dict) and 'choices' in response:
            return response['choices'][0]['message']['content'].strip()
        else:
            return str(response)