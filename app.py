import streamlit as st
import pandas as pd
import io

# ページ設定
st.set_page_config(
    page_title="一括利益計算ツール",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 複数商品一括利益計算ツール")
st.write("CSVファイルをアップロードするだけで、複数商品の利益を一気に計算できます！")

st.markdown("---")

# 使い方の説明
with st.expander("📖 使い方"):
    st.markdown("""
    ### CSVファイルの形式
    
    以下の列を含むCSVファイルを用意してください：
    
    | 商品名 | 仕入れ価格 | 販売価格 | 販売先 |
    |--------|------------|----------|--------|
    | 商品A  | 1000       | 2000     | 楽天市場 |
    | 商品B  | 1500       | 3000     | Amazon |
    | 商品C  | 800        | 1500     | Yahoo!ショッピング |
    
    **販売先は以下から選択：**
    - 楽天市場
    - Amazon
    - Yahoo!ショッピング
    - メルカリ
    
    ### 手順
    1. CSVファイルをアップロード
    2. 「計算する」ボタンをクリック
    3. 結果が表示されます
    4. 結果をCSVでダウンロードできます
    """)

# サンプルCSVのダウンロード
st.subheader("📥 サンプルCSVをダウンロード")
st.write("初めての方は、まずサンプルCSVをダウンロードして試してみてください。")

sample_data = pd.DataFrame({
    "商品名": ["ワイヤレスイヤホン", "スマホケース", "モバイルバッテリー", "USB充電器", "スマホスタンド"],
    "仕入れ価格": [1000, 500, 1500, 800, 300],
    "販売価格": [2500, 1200, 3500, 1800, 800],
    "販売先": ["楽天市場", "Amazon", "Yahoo!ショッピング", "メルカリ", "楽天市場"]
})

csv_sample = sample_data.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 サンプルCSVをダウンロード",
    data=csv_sample,
    file_name="sample_products.csv",
    mime="text/csv"
)

st.markdown("---")

# CSVアップロード
st.subheader("📤 CSVファイルをアップロード")

uploaded_file = st.file_uploader(
    "CSVファイルを選択してください",
    type=['csv'],
    help="商品名、仕入れ価格、販売価格、販売先の列を含むCSVファイル"
)

if uploaded_file is not None:
    try:
        # CSVを読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        
        st.success("✅ ファイルを読み込みました！")
        
        # 列名のチェック
        required_columns = ["商品名", "仕入れ価格", "販売価格", "販売先"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ 必要な列が見つかりません: {', '.join(missing_columns)}")
            st.info("CSVファイルに以下の列が必要です: 商品名、仕入れ価格、販売価格、販売先")
        else:
            # データプレビュー
            st.subheader("👀 アップロードされたデータ")
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            
            # 計算ボタン
            if st.button("🎯 利益を一括計算する", type="primary", use_container_width=True):
                
                # 手数料率の定義
                fee_rates = {
                    "楽天市場": 10.0,
                    "Amazon": 15.0,
                    "Yahoo!ショッピング": 8.0,
                    "メルカリ": 10.0
                }
                
                # 計算結果を格納するリスト
                results = []
                
                for idx, row in df.iterrows():
                    try:
                        product_name = row['商品名']
                        cost_price = float(row['仕入れ価格'])
                        selling_price = float(row['販売価格'])
                        platform = row['販売先']
                        
                        # 手数料率を取得（未知の販売先は10%とする）
                        fee_rate = fee_rates.get(platform, 10.0)
                        
                        # 計算
                        fee = selling_price * (fee_rate / 100)
                        profit = selling_price - cost_price - fee
                        
                        if cost_price > 0:
                            profit_rate = (profit / cost_price) * 100
                        else:
                            profit_rate = 0
                        
                        # 判定
                        if profit > 0:
                            if profit_rate >= 30:
                                status = "🔥 高利益"
                            elif profit_rate >= 20:
                                status = "✅ 良好"
                            elif profit_rate >= 10:
                                status = "👍 普通"
                            else:
                                status = "⚠️ 低利益"
                        elif profit < 0:
                            status = "❌ 赤字"
                        else:
                            status = "⚖️ トントン"
                        
                        results.append({
                            "商品名": product_name,
                            "仕入れ価格": int(cost_price),
                            "販売価格": int(selling_price),
                            "販売先": platform,
                            "手数料率": fee_rate,
                            "手数料": int(fee),
                            "利益": int(profit),
                            "利益率": round(profit_rate, 1),
                            "判定": status
                        })
                        
                    except Exception as e:
                        st.warning(f"⚠️ {idx + 1}行目の処理でエラー: {str(e)}")
                        continue
                
                if results:
                    # 結果をDataFrameに変換
                    result_df = pd.DataFrame(results)
                    
                    st.markdown("---")
                    st.subheader("📊 計算結果")
                    
                    # 統計情報
                    total_products = len(result_df)
                    total_cost = result_df['仕入れ価格'].sum()
                    total_selling = result_df['販売価格'].sum()
                    total_profit = result_df['利益'].sum()
                    
                    # メトリクス表示
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📦 商品数", f"{total_products}個")
                    
                    with col2:
                        st.metric("🛒 仕入れ合計", f"{total_cost:,}円")
                    
                    with col3:
                        st.metric("💴 販売合計", f"{total_selling:,}円")
                    
                    with col4:
                        if total_profit > 0:
                            st.metric("💰 利益合計", f"{total_profit:,}円", delta="黒字")
                        elif total_profit < 0:
                            st.metric("💸 損失合計", f"{abs(total_profit):,}円", delta="赤字", delta_color="inverse")
                        else:
                            st.metric("⚖️ 損益", "±0円")
                    
                    st.markdown("---")
                    
                    # タブで表示
                    tab1, tab2, tab3 = st.tabs(["📋 全商品", "✅ 利益商品のみ", "❌ 赤字商品のみ"])
                    
                    with tab1:
                        st.dataframe(result_df, use_container_width=True)
                    
                    with tab2:
                        profit_items = result_df[result_df['利益'] > 0]
                        if len(profit_items) > 0:
                            st.success(f"✅ 利益が出る商品が {len(profit_items)} 個見つかりました！")
                            st.dataframe(profit_items, use_container_width=True)
                        else:
                            st.info("利益が出る商品はありませんでした。")
                    
                    with tab3:
                        loss_items = result_df[result_df['利益'] < 0]
                        if len(loss_items) > 0:
                            st.error(f"❌ 赤字になる商品が {len(loss_items)} 個あります")
                            st.dataframe(loss_items, use_container_width=True)
                        else:
                            st.success("赤字商品はありません！")
                    
                    st.markdown("---")
                    
                    # CSVダウンロード
                    st.subheader("📥 結果をダウンロード")
                    
                    csv_result = result_df.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="📥 計算結果をCSVでダウンロード",
                        data=csv_result,
                        file_name="profit_calculation_result.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                else:
                    st.error("❌ 計算できる商品がありませんでした。")
    
    except Exception as e:
        st.error(f"❌ ファイルの読み込みエラー: {str(e)}")
        st.info("CSVファイルの形式を確認してください。UTF-8エンコーディングを推奨します。")

else:
    st.info("👆 CSVファイルをアップロードしてください。初めての方は上のサンプルCSVをダウンロードして試してみてください。")

# フッター
st.markdown("---")
st.caption("💡 ヒント: Excelで商品リストを作ってCSV形式で保存すると便利です")
st.caption("Created with ❤️ by Streamlit")
