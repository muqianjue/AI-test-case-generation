import streamlit as st
import pandas as pd
import math


class PaginatedDataEditor:
    def __init__(self, page_size=10):
        self.page_size = page_size
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

    def paginated_data_editor(self, df):
        total_pages = self._calculate_total_pages(df)

        # 确保当前页在有效范围内
        st.session_state.current_page = min(max(1, st.session_state.current_page), total_pages)

        start_idx, end_idx = self._get_page_indices(df)
        page_df = df.iloc[start_idx:end_idx].copy()

        edited_df = st.data_editor(
            page_df,
            hide_index=True,
            num_rows="dynamic",
            key=f"data_editor_{st.session_state.current_page}",
            use_container_width=True,
            column_config={col: st.column_config.Column(required=False) for col in df.columns}
        )

        df = self._update_dataframe(df, edited_df, start_idx, end_idx)

        # 重新计算总页数和当前页
        total_pages = self._calculate_total_pages(df)
        st.session_state.current_page = min(st.session_state.current_page, total_pages)

        self._create_pagination_controls(total_pages)

        return df

    def _calculate_total_pages(self, df):
        return max(1, math.ceil(len(df) / self.page_size))

    def _get_page_indices(self, df):
        start_idx = (st.session_state.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(df))
        return start_idx, end_idx

    def _create_pagination_controls(self, total_pages):
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

        with col1:
            if st.button("首页", key="first_page"):
                st.session_state.current_page = 1
                st.experimental_rerun()

        with col2:
            if st.button("上一页", key="prev_page"):
                st.session_state.current_page = max(1, st.session_state.current_page - 1)
                st.experimental_rerun()

        with col3:
            new_page = st.number_input("页码", min_value=1, max_value=total_pages,
                                       value=st.session_state.current_page, key="page_input")
            if new_page != st.session_state.current_page:
                st.session_state.current_page = new_page
                st.experimental_rerun()

        with col4:
            if st.button("下一页", key="next_page"):
                st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
                st.experimental_rerun()

        with col5:
            if st.button("末页", key="last_page"):
                st.session_state.current_page = total_pages
                st.experimental_rerun()

        st.write(f"第 {st.session_state.current_page} 页，共 {total_pages} 页")

    def _update_dataframe(self, df, edited_df, start_idx, end_idx):
        if len(edited_df) > end_idx - start_idx:
            # 新行被添加
            new_rows = edited_df.iloc[end_idx - start_idx:]
            df = pd.concat([df, new_rows], ignore_index=True)
        elif len(edited_df) < end_idx - start_idx:
            # 行被删除
            df = pd.concat([df.iloc[:start_idx], edited_df, df.iloc[end_idx:]], ignore_index=True)
        else:
            # 更新现有行
            df.iloc[start_idx:end_idx] = edited_df
        return df


