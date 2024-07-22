import asyncio
import base64
import json
import os
import re
import tempfile
import uuid
import xml.etree.ElementTree as ET
from io import StringIO

import httpx
import markdown2
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import xmind
from markupsafe import Markup

from word_extractor import WordExtractor

# 初始化会话状态
if 'requirement_info' not in st.session_state:
    st.session_state.requirement_info = ""
if 'prompts_case' not in st.session_state:
    st.session_state.prompts_case = ""
if 'additional_notes' not in st.session_state:
    st.session_state.additional_notes = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'module' not in st.session_state:
    st.session_state.module = ""
if 'result_df' not in st.session_state:
    st.session_state.result_df = pd.DataFrame()

# 自定义CSS样式
st.markdown(
    """
    <style>
    .centered-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .centered-text {
        text-align: center;
    }
    .centered-input {
        margin: 0 auto;
        width: 50%;
    }
    .centered-button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='centered-content'>", unsafe_allow_html=True)
st.title("🤖 根据需求文档生成测试用例")

uploaded_file = st.file_uploader("选择需求文档", type=["docx", "pdf"])


# TODO:
# Formatting text to DataFrame
def formatting(text):
    html = markdown2.markdown(text, extras=['tables'])
    table_content = re.search(r'<table>(.*?)</table>', html, re.DOTALL)
    if table_content:
        table_html = f"<table>{table_content.group(1)}</table>"
        html_io = StringIO(table_html)
        df = pd.read_html(html_io)[0]
        return df
    else:
        return pd.DataFrame()


# 格式化为Markdown
def formatting_md(text):
    return Markup(markdown2.markdown(text, extras=['tables']))


# DataFrame to Markdown
def df_to_markdown(df, save_dir):
    # 将 DataFrame 转换为 Markdown 格式的字符串
    markdown = df.to_markdown(index=False)

    # 生成唯一的文件名
    filename = f"test_cases_{uuid.uuid4()}.md"
    full_path = os.path.join(save_dir, filename)

    # 将 Markdown 字符串写入文件
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return full_path


def df_to_freemind(df,save_dir):

    # 创建根节点
    root = ET.Element("map")
    root.set("version", "1.0.1")

    # 创建主节点
    main_node = ET.SubElement(root, "node")
    main_node.set("TEXT", df.iloc[1, 0])

    # 按照相关需求和用例标题组织数据
    for requirement, req_group in df.groupby(['所属版本','相关需求']):
        version_node = ET.SubElement(main_node,"node")
        version_node.set("TEXT",requirement[0])

        requirement_node = ET.SubElement(version_node, "node")
        requirement_node.set("TEXT", requirement[1])

        for _, row in req_group.iterrows():
            case_node = ET.SubElement(requirement_node, "node")
            case_node.set("TEXT", row['用例标题'])

            # 添加用例详情
            details = [
                f"前置条件: {row['前置条件']}",
                f"步骤: {row['步骤']}",
                f"预期: {row['预期']}",
                f"关键词: {row['关键词']}",
                f"优先级: {row['优先级']}",
                f"用例类型: {row['用例类型']}",
                f"适用阶段: {row['适用阶段']}",
                f"用例状态: {row['用例状态']}"
            ]
            for detail in details:
                detail_node = ET.SubElement(case_node, "node")
                detail_node.set("TEXT", detail)

    # 创建 XML 树
    tree = ET.ElementTree(root)
    # 生成唯一的文件名
    filename = f"test_cases_{uuid.uuid4()}.mm"
    full_path = os.path.join(save_dir, filename)
    tree.write(full_path, encoding="UTF-8", xml_declaration=True)
    return full_path
#
# dataframe to xmind
def df_to_xmind(df, save_dir):
    # 生成唯一的文件名
    filename = f"test_cases_{uuid.uuid4()}.xmind"
    full_path = os.path.join(save_dir, filename)

    # 创建新的XMind工作簿
    workbook = xmind.load(full_path)

    # 获取第一个画布（sheet）
    sheet = workbook.getPrimarySheet()

    # 创建主节点
    root_topic = sheet.getRootTopic()
    root_topic.setTitle(df.iloc[1, 0])

    # 按照所属版本和相关需求组织数据
    for (version, requirement), req_group in df.groupby(['所属版本', '相关需求']):
        # 创建版本节点
        version_topic = root_topic.addSubTopic()
        version_topic.setTitle(version)

        # 创建需求节点
        requirement_topic = version_topic.addSubTopic()
        requirement_topic.setTitle(requirement)

        for _, row in req_group.iterrows():
            # 创建用例节点
            case_topic = requirement_topic.addSubTopic()
            case_topic.setTitle(row['用例标题'])

            # 添加用例详情
            details = [
                f"前置条件: {row['前置条件']}",
                f"步骤: {row['步骤']}",
                f"预期: {row['预期']}",
                f"关键词: {row['关键词']}",
                f"优先级: {row['优先级']}",
                f"用例类型: {row['用例类型']}",
                f"适用阶段: {row['适用阶段']}",
                f"用例状态: {row['用例状态']}"
            ]
            for detail in details:
                detail_topic = case_topic.addSubTopic()
                detail_topic.setTitle(detail)

    # 保存文件
    xmind.save(workbook, full_path)

    return full_path

def export(base64 , path):
    content = f"""
                    <style>
                        .download-button {{
                            display: inline-flex;
                            -webkit-box-align: center;
                            align-items: center;
                            -webkit-box-pack: center;
                            justify-content: center;
                            font-weight: 400;
                            font-size: 1rem
                            padding: 0px;
                            border-radius: 0.5rem;
                            min-height: 2.5rem;
                            margin: -5px;
                            line-height: 1.6;
                            color: inherit;
                            width: auto;
                            user-select: none;
                            background-color: rgb(255, 255, 255);
                            border: 1px solid rgba(49, 51, 63, 0.2);

                    }}
                    .download-button:hover {{
                        background-color: #45a049;
                    }}
                    </style>

                        <div data-testid="column" class="st-emotion-cache-keje6w e1f1d6gn3" style="display: flex; justify-content: center; align-items: center; height: 100%;">
                          <div data-testid="stVerticalBlockBorderWrapper" data-test-scroll-behavior="normal" class="st-emotion-cache-0 e1f1d6gn0">
                            <div class="st-emotion-cache-1wmy9hl e1f1d6gn1">
                              <div width="344" data-testid="stVerticalBlock" class="st-emotion-cache-1njjmvq e1f1d6gn2">
                                <div data-stale="false" width="344" class="element-container st-emotion-cache-lj8h43 e1f1d6gn4" data-testid="element-container">
                                  <div class="row-widget stDownloadButton" data-testid="stDownloadButton" style="width: 344px;">
                                    <button id="downloadButton" kind="secondary" data-testid="baseButton-secondary" class="download-button" style="width: 100%;">
                                      <div data-testid="stMarkdownContainer" class="st-emotion-cache-187vdiz e1nzilvr4">
                                        <p>
                                          <font style="vertical-align: inherit;">
                                            <font style="vertical-align: inherit;">下载 Freemind 格式文件</font>
                                          </font>
                                        </p>
                                      </div>
                                    </button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        <script>
                        var fileBase64 = "{base64}";
                        var fileName = "{os.path.basename(path)}";

                        document.getElementById("downloadButton").addEventListener("click", function() {{
                            var link = document.createElement("a");
                            link.href = "data:application/octet-stream;base64," + fileBase64;
                            link.download = fileName;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }});
                        </script>
                        """
    return content


async def rag(requirement_info):
    # API URL
    api_url = "http://10.12.3.94/v1/chat-messages"
    # API Key
    api_key = "app-L1cDMG3wA4EYG5B13Qezu2CY"

    # Request headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    # Request payload
    data = {
        "inputs": {},
        "query": f"{requirement_info}",
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "abc-123"
    }
    # 发送 POST request
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    answer = response_json.get('answer', 'No answer found')
    return answer

# Call external API and generate test cases
async def qwen_predict(requirement_info, prompts_case, Recall_Content, complement, module):
    json1 = {
        "model": "Qwen/Qwen2-72B-Instruct",
        "max_tokens": 16000,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": [
            "<|im_end|>",
            "<|im_start|>"
        ],
        "messages": [
            {
                "content": f'''我是一名网页端软件测试工程师，下面这份需求信息帮我输出一份测试点：
    需求信息：{requirement_info}
    RAG召回内容：{Recall_Content}
    用户prompt：{prompts_case}
    补充要求：{complement}
    输出要求：将测试点分为{module}，并且新增一列，表明所属的模块。若对应模块无合适的测试点，则无需生成该模块。
    输出格式：表格，分为序号、所属模块、需求名称、测试点，总共四列。''',
                "role": "user"
            }
        ],
        "repetitive_penalty": 1
    }

    headers = {'Authorization': 'Bearer c9bd37061c2a92ea4d524aab6fd94d36aa108701f95811d3d2bbb8e41d0ff8d9'}
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.together.xyz/v1/chat/completions", json=json1, headers=headers,
                                     timeout=300)
        response.raise_for_status()
        test_point = response.json()["choices"][0]["message"]["content"]

        complement_text = f"输出要求：{complement}。" if complement else ""

        json2 = {
            "model": "Qwen/Qwen2-72B-Instruct",
            "max_tokens": 16000,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": [
                "<|im_end|>",
                "<|im_start|>"
            ],
            "messages": [
                json1["messages"][0],
                {
                    "content": f"{test_point}",
                    "role": "assistant"
                },
                {
                    "content": f'''请根据上述的测试点，帮我输出一份测试用例，针对每条测试点用一条以上用例验证 ：
                    功能流程：写一条正向的流程
                    {complement_text}需要包含所属模块、所属版本、相关需求、用例标题、前置条件、步骤、预期、关键词、优先级、用例类型、适用阶段、用例状态。共12列，注意步骤和预期两列分点阐述，如：1. 2. 等。注意运用等价类划分测试方法。
                    输出格式：表格。
                    输出限制：输出的表格中请勿包含序号列
                        ''',
                    "role": "user"
                },
            ],
            "repetitive_penalty": 1
        }

        response2 = await client.post("https://api.together.xyz/v1/chat/completions", json=json2, headers=headers,
                                      timeout=300)
        response2.raise_for_status()
        return formatting(response2.json()["choices"][0]["message"]["content"])


# 提取文档中的内容
def extract_text_table_img(file):
    extractor = WordExtractor(file)
    extracted_content = extractor.extract()
    text = extracted_content["text_content"]
    img = extracted_content["image_content"]
    table = extracted_content["table_content"]
    return text, img, table


# 使用大模型总结需求信息
async def qwen_extract_requirements(text, table, img):
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
                           f"文本内容：{text}"
                           f"表格内容：{table}"
                           f"图片内容：{img}\n"
                           f"输出格式：表格，分为序号、所属模块、所属版本、相关需求、需求说明，总共五列。",
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
        return requirement_info

#RAG召回调用
async def run_rag():
    return await rag(requirement_info)

def get_file_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    st.write(file_details)
    try:
        # TODO：优化这部分的代码
        # 如果直接传入uploaded_file.name 出现错误：不是有效的文件或网址
        text_info, table_info, img_info = extract_text_table_img("D:\TestCases\航空云监控管理_需求规格说明书20240223.docx")

        async def run_extraction():
            return await qwen_extract_requirements(text_info, table_info, img_info)
        requirement_info = asyncio.run(run_extraction())
        st.session_state.requirement_info = requirement_info
        st.write(requirement_info)
        st.write("需求信息提取完成！~~~~~~~~~~~~~~~~~~~~~~~~~~")
        st.session_state.requirement_info = requirement_info  # 更新需求说明
        rag_info = asyncio.run(run_rag())
        st.session_state.rag_info = rag_info
    except Exception as e:
        st.error(f"上传文件时出现错误：{e}")



# TODO:部署RAG应用
# api_key = st.text_input("请输入您的API key")
# if api_key:
#     st.write(f"你的API key是: {api_key}")

# prompts_case = st.text_input("请输入您的prompt以帮助生成更符合要求的测试用例")

additional_notes = st.text_input("请输入补充说明：（可选）")



st.text("测试模块")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    fun_test = st.checkbox('功能测试', value=True)
with col2:
    ab_test = st.checkbox('性能测试', value=True)
with col3:
    boundary_test = st.checkbox('边界值分析测试', value=True)
with col4:
    error_test = st.checkbox('错误猜测测试', value=True)
with col5:
    com_test = st.checkbox('兼容性测试', value=True)

selected_tests = []
if fun_test:
    selected_tests.append('功能测试')
if ab_test:
    selected_tests.append('性能测试')
if boundary_test:
    selected_tests.append('边界值分析测试')
if error_test:
    selected_tests.append('错误猜测测试')
if com_test:
    selected_tests.append('兼容性测试')

selected_table = []

# st.write('已选测试模块: ', ', '.join(selected_tests))
st.session_state.module = selected_tests

if st.button("生成测试用例"):
    if st.session_state.requirement_info and st.session_state.module:
        with st.spinner("正在生成测试用例..."):
            try:
                async def run_async():
                    return await qwen_predict(st.session_state.requirement_info, st.session_state.prompts_case, st.session_state.rag_info, st.session_state.additional_notes,
                                              st.session_state.module)
                result_df = asyncio.run(run_async())
                if result_df.empty:
                    st.write("生成结果为空，请检查输入和API调用。")
                else:
                    st.session_state.result_df = result_df
                    st.write("测试用例已生成")
            except Exception as e:
                st.error(f"生成测试用例时出错: {e}")
    else:
        st.error("请上传需求文档并选择测试模块")

if not st.session_state.result_df.empty:
    st.subheader("生成的测试用例表格（您可根据实际需要进行编辑）")
    edited_df = st.data_editor(st.session_state.result_df, num_rows="dynamic")

    if st.button("保存修改"):
        st.session_state.result_df = edited_df
        st.success("修改已保存！")


    with tempfile.TemporaryDirectory() as save_dir:
        # 生成path文件
        xmind_path = df_to_xmind(st.session_state.result_df, save_dir)
        freemind_path = df_to_freemind(st.session_state.result_df, save_dir)
        markdown_path = df_to_markdown(st.session_state.result_df, save_dir)
        # 获取文件的base64编码
        xmind_file_base64 = get_file_base64(xmind_path)
        freemind_file_base64 = get_file_base64(freemind_path)
        markdown_file_base64 = get_file_base64(markdown_path)
        # 创建自定义HTML和JavaScript
        xmind_html_content = export(xmind_file_base64 , xmind_path)
        freemind_html_content = export(freemind_file_base64 , freemind_path)
        markdown_html_content = export(markdown_file_base64 , markdown_path)
        # 使用 components.html 来渲染 HTML 和执行 JavaScript
        # 生成xmind文件
        components.html(xmind_html_content)
        # 生成freemind文件
        components.html(freemind_html_content)
        # 生成Markdown文件
        components.html(markdown_html_content)

st.markdown("</div>", unsafe_allow_html=True)
