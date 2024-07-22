from xinference.client import RESTfulClient

class TestCaseGenerator:
    def __init__(self):
        self.client = RESTfulClient("http://10.12.3.31:9997")
        self.model = self.client.get_model("Qwen2-72B-Instruct-GPTQ-Int4")

    async def qwen_generate_test_cases(self, requirement_info, prompts_case, recall_content, complement, module):
        response1 = self.model.chat(
            prompt=f'''我是一名网页端软件测试工程师，下面这份需求信息帮我输出一份测试点：
    需求信息：{requirement_info}
    RAG召回内容：{recall_content}
    用户prompt：{prompts_case}
    补充要求：{complement}
    输出要求：将测试点分为{module}，并且新增一列，表明所属的模块。若对应模块无合适的测试点，则无需生成该模块。
    输出格式：表格，分为序号、所属模块、需求名称、测试点，总共四列。''',
            system_prompt="你是一个专业的测试工程师导师",
            chat_history=[],
            generate_config={
                "max_tokens": 16000,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|im_end|>", "<|im_start|>"]
            }
        )

        test_point = response1['choices'][0]['message']['content'] if 'choices' in response1 else str(response1)

        complement_text = f"输出要求：{complement}。" if complement else ""

        response2 = self.model.chat(
            prompt=f'''请根据上述的测试点，帮我输出一份测试用例，针对每条测试点用一条以上用例验证 ：
    功能流程：写一条正向的流程
    {complement_text}需要包含所属模块、所属版本、相关需求、用例标题、前置条件、步骤、预期、关键词、优先级、用例类型、适用阶段、用例状态。共12列，注意步骤和预期两列分点阐述，如：1. 2. 等。注意运用等价类划分测试方法。
    输出格式：表格。
    输出格式样例：
    | 所属模块           | 所属版本 | 相关需求 | 用例标题                       | 前置条件                     | 步骤                                                     | 预期                                                         | 关键词             | 优先级 | 用例类型 | 适用阶段 | 用例状态 |
| :----------------- | :------- | :------- | :----------------------------- | :--------------------------- | :------------------------------------------------------- | :----------------------------------------------------------- | :----------------- | :----- | :------- | :------- | :------- |
| 航空云智能运维平台 | V1.0     | 产品目标 | 验证系统功能要求描述的正确展示 | 系统已部署并运行，用户已登录 | 1. 用户访问系统主页。2. 检查主页上是否包含功能要求描述。 | 1. 用户能够成功访问系统主页。2. 主页上正确展示了功能要求描述。 | 功能要求描述、主页 | 高     | 功能测试 | 系统测试 | 设计中   |
| 航空云智能运维平台 | V1.0     | 目标用户 | 验证管理人员角色的权限         | 系统已部署并运行，用户已登录 | 1. 以管理人员角色登录系统。2. 访问监控概览页面。         | 1. 管理人员能够成功登录系统。2. 管理人员能够查看监控概览数据。 | 管理人员、监控概览 | 高     | 功能测试 | 系统测试 | 设计中   |
    注意：输出请勿含有无法转化为freemind格式的节点的内容
    ''',
            system_prompt="你是一个专业的测试工程师",
            chat_history=[
                {"role": "user", "content": f'''我是一名网页端软件测试工程师，下面这份需求信息帮我输出一份测试点：
    需求信息：{requirement_info}
    RAG召回内容：{recall_content}
    用户prompt：{prompts_case}
    补充要求：{complement}
    输出要求：将测试点分为{module}，并且新增一列，表明所属的模块。若对应模块无合适的测试点，则无需生成该模块。
    输出格式：表格，分为序号、所属模块、需求名称、测试点，总共四列。'''},
                {"role": "assistant", "content": test_point}
            ],
            generate_config={
                "max_tokens": 16000,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|im_end|>", "<|im_start|>"]
            }
        )

        return response2['choices'][0]['message']['content'] if 'choices' in response2 else str(response2)