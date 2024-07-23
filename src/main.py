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
    st.session_state.requirement_info = None
if 'rag_info' not in st.session_state:
    st.session_state.rag_info = None
if 'result_df' not in st.session_state:
    st.session_state.result_df = pd.DataFrame()
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'initial_df' not in st.session_state:
    st.session_state.initial_df = pd.DataFrame()
if 'demand_edited_df' not in st.session_state:
    st.session_state.demand_edited_df = pd.DataFrame()
if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []
if 'prev_requirement_info' not in st.session_state:
    st.session_state.prev_requirement_info = None
if 'test_case_input_hash' not in st.session_state:
    st.session_state.test_case_input_hash = None

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

    if st.session_state.processed_file != uploaded_file.name:
        st.session_state.processed_file = uploaded_file.name
        try:
            bytes_data = uploaded_file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(bytes_data)
                temp_file_path = temp_file.name

            title, extract_content = doc_processor.extract_text_table_img(temp_file_path)
            os.unlink(temp_file_path)  # 删除临时文件


            async def run_extraction():
                return await doc_processor.qwen_extract_requirements(title, extract_content)


            requirement_info = asyncio.run(run_extraction())
            table_data = data_formatter.formatting(requirement_info)
            st.session_state.initial_df = pd.DataFrame(table_data)
        except Exception as e:
            st.error(f"上传文件时出现错误：{e}")

    df = st.session_state.initial_df

    st.subheader("生成的需求信息表格（您可根据实际需要进行选择）:")
    edited_df = editor.paginated_data_editor(df, key_prefix='requirements')

    if not st.session_state.demand_edited_df.equals(edited_df):
        st.session_state.demand_edited_df = edited_df

    if st.checkbox("显示完整数据"):
        st.subheader("完整数据")
        st.dataframe(
            st.session_state.demand_edited_df,
            use_container_width=True,
            hide_index=True,
            column_config={col: st.column_config.Column(width="flex") for col in
                           st.session_state.demand_edited_df.columns}
        )

    selected_rows = st.multiselect("选择需求：", df.index,
                                   format_func=lambda x: f"{st.session_state.demand_edited_df.at[x, '需求名称']}")
    if st.session_state.selected_rows != selected_rows:
        st.session_state.selected_rows = selected_rows
        selected_rows_content = df.iloc[selected_rows]
        st.write("选中的需求内容：")
        st.dataframe(selected_rows_content)
        selected_rows_dict = selected_rows_content.to_dict('records')
        st.session_state.requirement_info = selected_rows_dict

    if st.session_state.requirement_info != st.session_state.prev_requirement_info:
        st.session_state.prev_requirement_info = st.session_state.requirement_info


        async def run_rag():
            return await rag.rag_recall(st.session_state.requirement_info)


        rag_info = asyncio.run(run_rag())
        st.session_state.rag_info = rag_info

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

st.session_state.module = selected_tests

if st.button("生成测试用例"):
    if st.session_state.requirement_info and st.session_state.module:
        with st.spinner("正在生成测试用例..."):
            try:
                input_hash = hash((str(st.session_state.requirement_info),
                                   str(st.session_state.rag_info),
                                   additional_notes,
                                   str(st.session_state.module)))
                if st.session_state.test_case_input_hash != input_hash:
                    st.session_state.test_case_input_hash = input_hash


                    async def run_async():
                        return await test_case_generator.qwen_generate_test_cases(
                            st.session_state.requirement_info,
                            st.session_state.rag_info,
                            additional_notes,
                            st.session_state.module
                        )


                    result = asyncio.run(run_async())
                    result_df = data_formatter.formatting(result)
                    if result_df.empty:
                        st.write("生成结果为空，请检查输入和API调用。")
                    else:
                        st.session_state.result_df = result_df
                        st.write("测试用例已生成")
                else:
                    st.write("使用缓存的测试用例结果")
            except Exception as e:
                st.error(f"生成测试用例时出错: {e}")
    else:
        st.error("请上传需求文档并选择测试模块")

# 显示和编辑生成的测试用例
if not st.session_state.result_df.empty:
    st.subheader("生成的测试用例表格（您可根据实际需要进行编辑）")
    st.session_state.result_edited_df = editor.paginated_data_editor(st.session_state.result_df,
                                                                     key_prefix='test_cases')

    if st.checkbox("显示完整测试数据"):
        st.subheader("完整测试数据")
        st.dataframe(
            st.session_state.result_edited_df,
            use_container_width=True,
            hide_index=True,
            column_config={col: st.column_config.Column(width="flex") for col in
                           st.session_state.result_edited_df.columns}
        )

    # 文件导出部分
    with tempfile.TemporaryDirectory() as save_dir:
        xmind_path = data_formatter.df_to_xmind(st.session_state.result_df, save_dir)
        freemind_path = data_formatter.df_to_freemind(st.session_state.result_df, save_dir)
        markdown_path = data_formatter.df_to_markdown(st.session_state.result_df, save_dir)

        for file_path, file_type in [(xmind_path, 'XMind'), (freemind_path, 'FreeMind'), (markdown_path, 'Markdown')]:
            file_base64 = download_link.get_file_base64(file_path)
            html_content = export.file_export(file_base64, file_path)
            components.html(html_content, height=50)

st.markdown("</div>", unsafe_allow_html=True)