import pandas as pd
import markdown2
from io import StringIO
import re
import xml.etree.ElementTree as ET
import io
import streamlit as st
import html
import os
import uuid
import xmind
from markupsafe import Markup

class DataFormatter:
    @staticmethod
    def formatting(text):
        try:
            # 使用 markdown2 转换文本为 HTML
            html_content = markdown2.markdown(text, extras=['tables'])

            # 查找表格内容
            table_content = re.search(r'<table>(.*?)</table>', html_content, re.DOTALL)

            if table_content:
                table_html = f"<table>{table_content.group(1)}</table>"

                # 清理 HTML 内容
                cleaned_html = html.unescape(table_html)
                cleaned_html = re.sub(r'<br\s*/?>', ' ', cleaned_html)  # 替换 <br> 标签为空格

                try:
                    # 使用 pandas 读取 HTML 表格
                    dfs = pd.read_html(StringIO(cleaned_html), flavor='bs4')

                    if dfs:
                        df = dfs[0]
                        # 清理 DataFrame 中的数据
                        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                        df = df.replace(r'^\s*$', pd.NA, regex=True)  # 将空白字符串替换为 NA
                        return df
                    else:
                        st.warning("未能从HTML中提取出表格数据。")
                        return pd.DataFrame()
                except ValueError as ve:
                    st.warning(f"无法解析HTML表格 - {str(ve)}")
                    return pd.DataFrame()
            else:
                st.warning("在Markdown文本中未找到表格。")
                return pd.DataFrame()

        except Exception as e:
            st.error(f"处理文本时发生异常 - {str(e)}")
            return pd.DataFrame()

    @staticmethod
    # 格式化为Markdown
    def formatting_md(text):
        return Markup(markdown2.markdown(text, extras=['tables']))

    @staticmethod
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

    @staticmethod
    def df_to_freemind(df, save_dir):

        # 创建根节点
        root = ET.Element("map")
        root.set("version", "1.0.1")

        # 创建主节点
        main_node = ET.SubElement(root, "node")
        main_node.set("TEXT", df.iloc[1, 0])

        # 按照相关需求和用例标题组织数据
        for requirement, req_group in df.groupby(['所属版本', '相关需求']):
            version_node = ET.SubElement(main_node, "node")
            version_node.set("TEXT", requirement[0])

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

    # dataframe to xmind
    @staticmethod
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