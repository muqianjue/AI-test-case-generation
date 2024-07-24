import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import math


class PaginatedAgGrid:
    def __init__(self, page_size=10):
        self.page_size = page_size
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        if 'edited_df' not in st.session_state:
            st.session_state.edited_df = None
        self.grid_key_counter = 0

    def paginated_ag_grid(self, df, key_prefix=''):
        self.grid_key_counter += 1

        if st.session_state.edited_df is None:
            st.session_state.edited_df = df.copy()

        total_pages = self._calculate_total_pages(st.session_state.edited_df)
        st.session_state.current_page = min(max(1, st.session_state.current_page), total_pages)

        start_idx, end_idx = self._get_page_indices(st.session_state.edited_df)
        page_df = st.session_state.edited_df.iloc[start_idx:end_idx].copy()

        gb = GridOptionsBuilder.from_dataframe(page_df)
        gb.configure_selection('multiple', use_checkbox=True)
        gb.configure_default_column(editable=True)
        grid_options = gb.build()

        unique_key = f"{key_prefix}_ag_grid_{self.grid_key_counter}_{st.session_state.current_page}"

        response = AgGrid(
            page_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=True,
            key=unique_key
        )

        # 更新编辑后的数据
        if response['data'] is not None:
            st.session_state.edited_df.iloc[start_idx:end_idx] = response['data']

        selected_rows = response['selected_rows']

        self._create_pagination_controls(total_pages, key_prefix)

        return response, selected_rows, st.session_state.edited_df

    def _calculate_total_pages(self, df):
        return max(1, math.ceil(len(df) / self.page_size))

    def _get_page_indices(self, df):
        start_idx = (st.session_state.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(df))
        return start_idx, end_idx

    def _create_pagination_controls(self, total_pages, key_prefix):
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        with col1:
            if st.button("首页", key=f"{key_prefix}_first_page_{self.grid_key_counter}"):
                st.session_state.current_page = 1
                st.experimental_rerun()

        with col2:
            if st.button("上一页", key=f"{key_prefix}_prev_page_{self.grid_key_counter}"):
                st.session_state.current_page = max(1, st.session_state.current_page - 1)
                st.experimental_rerun()

        with col3:
            new_page = st.number_input(
                "页码",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.current_page,
                key=f"{key_prefix}_page_input_{self.grid_key_counter}",
                label_visibility="collapsed"
            )
            if new_page != st.session_state.current_page:
                st.session_state.current_page = new_page
                st.experimental_rerun()

        with col4:
            if st.button("下一页", key=f"{key_prefix}_next_page_{self.grid_key_counter}"):
                st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
                st.experimental_rerun()

        with col5:
            if st.button("末页", key=f"{key_prefix}_last_page_{self.grid_key_counter}"):
                st.session_state.current_page = total_pages
                st.experimental_rerun()

        st.write(f"共 {total_pages} 页")