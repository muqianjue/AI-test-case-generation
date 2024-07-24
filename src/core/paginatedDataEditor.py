import streamlit as st
import pandas as pd
import math


class PaginatedDataEditor:
    def __init__(self, page_size=10):
        self.page_size = page_size
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        self.editor_key_counter = 0

    def paginated_data_editor(self, df, key_prefix=''):
        self.editor_key_counter += 1
        total_pages = self._calculate_total_pages(df)

        st.session_state.current_page = min(max(1, st.session_state.current_page), total_pages)

        start_idx, end_idx = self._get_page_indices(df)
        page_df = df.iloc[start_idx:end_idx].copy()

        unique_key = f"{key_prefix}_data_editor_{self.editor_key_counter}_{st.session_state.current_page}"

        edited_df = st.data_editor(
            page_df,
            hide_index=True,
            num_rows="dynamic",
            key=unique_key,
            use_container_width=True,
            column_config={col: st.column_config.Column(required=False) for col in df.columns}
        )

        df = self._update_dataframe(df, edited_df, start_idx, end_idx)

        total_pages = self._calculate_total_pages(df)
        st.session_state.current_page = min(st.session_state.current_page, total_pages)

        self._create_pagination_controls(total_pages, key_prefix)

        return df

    def _calculate_total_pages(self, df):
        return max(1, math.ceil(len(df) / self.page_size))

    def _get_page_indices(self, df):
        start_idx = (st.session_state.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(df))
        return start_idx, end_idx

    def _create_pagination_controls(self, total_pages, key_prefix):
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        with col1:
            if st.button("首页", key=f"{key_prefix}_first_page_{self.editor_key_counter}"):
                st.session_state.current_page = 1
                st.experimental_rerun()

        with col2:
            if st.button("上一页", key=f"{key_prefix}_prev_page_{self.editor_key_counter}"):
                st.session_state.current_page = max(1, st.session_state.current_page - 1)
                st.experimental_rerun()

        with col3:
            new_page = st.number_input(
                "页码",  # 添加一个标签
                min_value=1,
                max_value=total_pages,
                value=st.session_state.current_page,
                key=f"{key_prefix}_page_input_{self.editor_key_counter}",
                label_visibility="collapsed"  # 保持标签隐藏
            )
            if new_page != st.session_state.current_page:
                st.session_state.current_page = new_page
                st.experimental_rerun()

        with col4:
            if st.button("下一页", key=f"{key_prefix}_next_page_{self.editor_key_counter}"):
                st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
                st.experimental_rerun()

        with col5:
            if st.button("末页", key=f"{key_prefix}_last_page_{self.editor_key_counter}"):
                st.session_state.current_page = total_pages
                st.experimental_rerun()

        st.write(f"共 {total_pages} 页")

    def _update_dataframe(self, df, edited_df, start_idx, end_idx):
        if len(edited_df) > end_idx - start_idx:
            new_rows = edited_df.iloc[end_idx - start_idx:]
            df = pd.concat([df, new_rows], ignore_index=True)
        elif len(edited_df) < end_idx - start_idx:
            df = pd.concat([df.iloc[:start_idx], edited_df, df.iloc[end_idx:]], ignore_index=True)
        else:
            df.iloc[start_idx:end_idx] = edited_df
        return df