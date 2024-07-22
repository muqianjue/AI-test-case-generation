import streamlit as st
import asyncio
import pandas as pd
import tempfile
import os
import html
from document_processor import DocumentProcessor
from test_case_generator import TestCaseGenerator
from data_formatter import DataFormatter
from xmind_download_link import DownloadLink
from streamlit import components

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

# 初始化处理器
doc_processor = DocumentProcessor()
test_case_generator = TestCaseGenerator()
data_formatter = DataFormatter()
download_link = DownloadLink()

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

# Streamlit UI
st.markdown("<div class='centered-content'>", unsafe_allow_html=True)
st.title("🤖 根据需求文档生成测试用例")

uploaded_file = st.file_uploader("选择需求文档", type=["docx", "pdf"])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    st.write(file_details)
    try:
        # TODO：优化这部分的代码，暂时使用固定文件路径才可以正常使用
        text_info, img_info, table_info = doc_processor.extract_text_table_img(
            "D:\TestCases\航空云监控需求.docx")

        async def run_extraction():
            return await doc_processor.qwen_extract_requirements(text_info, table_info, img_info)

        requirement_info = asyncio.run(run_extraction())

        st.session_state.requirement_info = requirement_info
        st.write(requirement_info)
        st.write("需求信息提取完成！~~~~~~~~~~~~~~~~~~~~~~~~~~")
    except Exception as e:
        st.error(f"上传文件时出现错误：{e}")

# TODO:部署RAG应用
api_key = st.text_input("请输入您的API key")
prompts_case = st.text_input("请输入您的prompt以帮助生成更符合要求的测试用例")
additional_notes = st.text_input("请输入补充说明：（可选）")

# 测试模块选择选项
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

#输出已选选项
# st.write('已选测试模块: ', ', '.join(selected_tests))
st.session_state.module = selected_tests

if st.button("生成测试用例"):
    if st.session_state.requirement_info and st.session_state.module:
        with st.spinner("正在生成测试用例..."):
            try:
                async def run_async():
                    return await test_case_generator.qwen_generate_test_cases(
                        st.session_state.requirement_info,
                        st.session_state.prompts_case,
                        '',
                        st.session_state.additional_notes,
                        st.session_state.module
                    )
                result = asyncio.run(run_async())
                result_df = data_formatter.formatting(result)

                if result_df.empty:
                    st.write("生成结果为空，请检查输入和API调用。")
                else:
                    st.session_state.result_df = result_df
                    st.write("测试用例已生成")
            except Exception as e:
                st.error(f"生成测试用例时出错: {e}")
    else:
        st.error("请上传需求文档并选择测试模块")

# 显示和编辑生成的测试用例
if not st.session_state.result_df.empty:
    st.subheader("生成的测试用例表格（您可根据实际需要进行编辑）")
    edited_df = st.data_editor(st.session_state.result_df, num_rows="dynamic")

    if st.button("保存修改"):
        st.session_state.result_df = edited_df
        st.success("修改已保存！")

    with tempfile.TemporaryDirectory() as save_dir:
        # 生成XMind文件
        xmind_path = data_formatter.df_to_xmind(st.session_state.result_df, save_dir)

        # 获取文件的base64编码
        xmind_file_base64 = download_link.get_file_base64(xmind_path)

        # 创建自定义HTML和JavaScript
        xmind_html_content = f"""
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
                margin: 0px;
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
                                <font style="vertical-align: inherit;">下载 XMind 文件</font>
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
            var fileBase64 = "{xmind_file_base64}";
            var fileName = "{os.path.basename(xmind_path)}";
    
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

        # 使用 components.html 来渲染 HTML 和执行 JavaScript
        components.html(xmind_html_content)

        # 生成freemind文件
        freemind_path = data_formatter.df_to_freemind(st.session_state.result_df, save_dir)

        freemind_file_base64 = download_link.get_file_base64(freemind_path)

        freemind_html_content = f"""
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
                        margin: 0px;
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
                    var fileBase64 = "{freemind_file_base64}";
                    var fileName = "{os.path.basename(freemind_path)}";
    
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

        # 使用 components.html 来渲染 HTML 和执行 JavaScript
        components.html(freemind_html_content)

        # 生成Markdown文件
        markdown_path = data_formatter.df_to_markdown(st.session_state.result_df, save_dir)

        markdown_file_base64 = download_link.get_file_base64(markdown_path)

        markdown_html_content = f"""
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
                                margin: 0px;
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
                                                <font style="vertical-align: inherit;">下载 Markdown 格式文件</font>
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
                            var fileBase64 = "{markdown_file_base64}";
                            var fileName = "{os.path.basename(markdown_path)}";
    
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

        # 使用 components.html 来渲染 HTML 和执行 JavaScript
        components.html(markdown_html_content)
