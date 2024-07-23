import asyncio
import os
import tempfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from data_formatter import DataFormatter
from document_processor import DocumentProcessor
from test_case_generator import TestCaseGenerator
from xmind_download_link import DownloadLink
from rag import Rag
from fileExport import fileExport
from paginatedDataEditor import PaginatedDataEditor

# 页面布局配置
st.set_page_config(layout='wide')

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
rag = Rag()
export = fileExport()
editor = PaginatedDataEditor(page_size=10)

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

uploaded_file = st.file_uploader("选择需求文档", type=["docx"])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    st.write(file_details)
    try:
        # TODO：优化这部分的代码，利用上传的文档：方法：将二进制数据写入一个新的文档，再把新的文档传递进函数中
        # TODO:多个人一起用呢？
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
        with open("file.docx", 'wb') as f:
            f.write(bytes_data)
        title, extract_content = doc_processor.extract_text_table_img('file.docx')
        if st.button('需要提取图片信息'):
            extract_image = True

        async def run_extraction():
            return await doc_processor.qwen_extract_requirements(title, extract_content)

        requirement_info = asyncio.run(run_extraction())

        table_data = data_formatter.formatting(requirement_info)
        # 将表格数据转换为 DataFrame
        df = pd.DataFrame(table_data)

        # 在 Streamlit 中显示表格
        st.subheader("生成的需求信息表格（您可根据实际需要进行选择）:")
        edited_df = editor.paginated_data_editor(df)
        # TODO:获取勾选的框？
        # 显示用于选择行的多选框
        selected_rows = st.multiselect("选择需求：", df.index, format_func=lambda x: f"{edited_df.at[x, '需求名称']}")
        # 记录选中行的内容
        selected_rows_content = df.iloc[selected_rows]

        st.write("选中的需求内容：")
        st.dataframe(selected_rows_content)
        selected_rows_dict = selected_rows_content.to_dict('records')
        # print("选中的需求信息：", selected_rows_dict)
        st.session_state.requirement_info = selected_rows_dict  # 更新需求说明
        st.write("需求信息提取完成！~~~~~~~~~~~~~~~~~~~~~~~~~~")

        #rag召回信息
        #对选中的需求信息进行召回
        async def run_rag():
            return await rag.rag_recall(st.session_state.requirement_info)
        rag_info = asyncio.run(run_rag())
        st.session_state.rag_info = rag_info

    except Exception as e:
        st.error(f"上传文件时出现错误：{e}")

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

# 输出已选选项
# st.write('已选测试模块: ', ', '.join(selected_tests))
st.session_state.module = selected_tests

if st.button("生成测试用例"):
    if st.session_state.requirement_info and st.session_state.module:
        with st.spinner("正在生成测试用例..."):
            try:
                async def run_async():
                    return await test_case_generator.qwen_generate_test_cases(
                        st.session_state.requirement_info,
                        st.session_state.rag_info,
                        st.session_state.additional_notes,
                        st.session_state.module
                    )
                result = asyncio.run(run_async())
                print('测试用例结果：\n', result)

                result_df = data_formatter.formatting(result)
                # print(result_df)


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
    edited_df = st.data_editor(st.session_state.result_df, num_rows="dynamic",use_container_width=True)

    if st.button("保存修改"):
        st.session_state.result_df = edited_df
        st.success("修改已保存！")

    with tempfile.TemporaryDirectory() as save_dir:
        # 生成path文件
        xmind_path = data_formatter.df_to_xmind(st.session_state.result_df, save_dir)
        freemind_path = data_formatter.df_to_freemind(st.session_state.result_df, save_dir)
        markdown_path = data_formatter.df_to_markdown(st.session_state.result_df, save_dir)
        # 获取文件的base64编码
        xmind_file_base64 = download_link.get_file_base64(xmind_path)
        freemind_file_base64 = download_link.get_file_base64(freemind_path)
        markdown_file_base64 = download_link.get_file_base64(markdown_path)
        # 创建自定义HTML和JavaScript
        xmind_html_content = export.file_export(xmind_file_base64, xmind_path)
        freemind_html_content = export.file_export(freemind_file_base64, freemind_path)
        markdown_html_content = export.file_export(markdown_file_base64, markdown_path)
        # 使用 components.html 来渲染 HTML 和执行 JavaScript
        # 生成xmind文件
        components.html(xmind_html_content)
        # 生成freemind文件
        components.html(freemind_html_content)
        # 生成Markdown文件
        components.html(markdown_html_content)




# TODO:把上传文件清理掉