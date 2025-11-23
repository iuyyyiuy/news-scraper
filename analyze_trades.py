import pandas as pd
import datetime
import os  # 用於檔案系統操作
import re  # 引入正規表達式模組


def analyze_single_excel_file(file_path):
    """
    從單個 Excel 檔案分析交易數據，計算平均持倉時間、淨虧損交易比率、
    總交易對數、總交易日數、總已實現盈虧、總手續費，以及盈虧/手續費比率。
    並計算所有單筆交易持倉時間總和 (分鐘)。

    Args:
        file_path (str): Excel 檔案的路徑 (.xlsx)。

    Returns:
        dict: 包含分析結果的字典，如果數據無效則返回錯誤訊息。
    """
    file_name = os.path.basename(file_path)
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        return {"檔案名稱": file_name, "錯誤": f"找不到檔案: {file_path}"}
    except Exception as e:
        return {"檔案名稱": file_name, "錯誤": f"讀取 Excel 檔案時發生錯誤: {e}"}

    # 統一使用簡體中文欄位名，因為錯誤信息表明 Excel 檔案中可能使用這些名稱
    required_columns = ['开仓时间', '平仓时间', '已实现盈亏', '手续费', '合约']
    for col in required_columns:
        if col not in df.columns:
            # 如果缺少欄位，返回錯誤信息，並明確指出缺少的欄位
            return {"檔案名稱": file_name, "錯誤": f"Excel 檔案中缺少必要欄位: '{col}'。請檢查欄位名稱是否正確。"}

    # 確保時間欄位是 datetime 格式
    try:
        df['開倉時間'] = pd.to_datetime(df['开仓时间'], errors='coerce')
        df['平倉時間'] = pd.to_datetime(df['平仓时间'], errors='coerce')
    except Exception as e:
        return {"檔案名稱": file_name, "錯誤": f"轉換時間格式時發生錯誤，請檢查 '开仓时间' 和 '平仓时间' 欄位: {e}"}

    # 過濾掉無效的行（例如時間轉換失敗的行，或缺失盈虧/手續費的行）
    # 這裡也使用簡體中文欄位名，與 required_columns 保持一致
    df = df.dropna(subset=['開倉時間', '平倉時間', '已实现盈亏', '手续费', '合约'])

    if df.empty:
        return {"檔案名稱": file_name, "錯誤": "沒有有效的交易數據可供分析。請檢查文件內容和格式。"}

    total_trades = len(df)

    # 1. 計算平均持倉時間 和 所有單筆交易持倉時間總和 (分鐘)
    df['持倉時間'] = (df['平倉時間'] - df['開倉時間']).dt.total_seconds()
    total_holding_seconds = df['持倉時間'].sum()
    avg_holding_time_minutes = (total_holding_seconds / total_trades) / 60 if total_trades > 0 else 0.0

    # 修改：所有單筆交易持倉時間總和 (分鐘)
    total_individual_holding_minutes = total_holding_seconds / 60

    # 2. 計算淨虧損交易比率
    df['淨盈虧'] = df['已实现盈亏'] - df['手续费']  # 這裡也使用簡體中文欄位名
    net_losing_trades_count = (df['淨盈虧'] < 0).sum()
    net_losing_trades_ratio = net_losing_trades_count / total_trades if total_trades > 0 else 0.0

    # 3. 計算總交易對數 (使用 '合约' 欄位)
    total_trading_pairs = df['合约'].nunique()  # 這裡也使用簡體中文欄位名

    # 4. 計算總交易日數
    total_trading_days = df['開倉時間'].dt.date.nunique()  # 這裡也使用簡體中文欄位名

    # 5. 計算總已實現盈虧
    total_realized_pnl = df['已实现盈亏'].sum()  # 這裡也使用簡體中文欄位名

    # 6. 計算總手續費
    total_fees = df['手续费'].sum()

    # 7. 計算盈虧/手續費比率
    pnl_fees_ratio = pd.NA  # 預設為 NA (Not Available)
    if total_fees != 0:
        pnl_fees_ratio = total_realized_pnl / total_fees
    elif total_realized_pnl == 0:  # 如果盈虧和手續費都為 0，比率為 0
        pnl_fees_ratio = 0.0
    # 如果手續費為 0 但盈虧不為 0，則比率為無限大，保持為 pd.NA 也是一種處理方式，或可以顯示為 "無限大"

    results = {
        "檔案名稱": file_name,
        "總交易筆數": total_trades,
        "總交易日數": total_trading_days,
        "總交易對數": total_trading_pairs,
        "所有單筆交易持倉時間總和 (分鐘)": round(total_individual_holding_minutes, 2),  # 單位改為分鐘
        "平均持倉時間 (分鐘)": round(avg_holding_time_minutes, 2),  # 這裡已經是分鐘
        "淨虧損交易筆數": net_losing_trades_count,
        "淨虧損交易比率": f"{net_losing_trades_ratio:.2%}",
        "總已實現盈虧": round(total_realized_pnl, 2),
        "總手续费": round(total_fees, 2),
        "盈虧/手續費比率": round(pnl_fees_ratio, 2) if pd.notna(pnl_fees_ratio) else pnl_fees_ratio
    }

    return results


def analyze_all_excel_in_directory_recursive(directory_path):
    """
    遞迴分析指定資料夾及其所有子資料夾中所有 Excel 檔案的交易數據，
    並將結果彙整成一個列表。

    Args:
        directory_path (str): 包含 Excel 檔案的資料夾路徑。

    Returns:
        list: 包含所有檔案分析結果的字典列表。
    """
    all_directory_results = []
    if not os.path.isdir(directory_path):
        print(f"錯誤: 指定的路徑不是一個有效的資料夾: {directory_path}")
        return all_directory_results  # 返回空列表

    print(f"正在掃描資料夾 (包含子資料夾): {directory_path}")

    # 使用 os.walk 遞迴遍歷所有子資料夾和檔案
    for dirpath, dirnames, filenames in os.walk(directory_path):
        # 獲取當前子資料夾的名稱
        full_folder_name = os.path.basename(dirpath)

        # 這裡不進行數字提取，因為用戶希望在 DataFrame 階段處理
        short_folder_name = full_folder_name

        for filename in filenames:
            if filename.endswith('.xlsx') and not filename.startswith('~'):  # 排除臨時檔案
                file_path = os.path.join(dirpath, filename)
                print(f"  正在分析檔案: {os.path.relpath(file_path, directory_path)}")  # 顯示相對路徑

                results = analyze_single_excel_file(file_path)

                # 在結果中添加所屬資料夾的簡稱
                results["所屬資料夾 (簡稱)"] = short_folder_name

                all_directory_results.append(results)

    if not all_directory_results:
        print(f"在資料夾 '{directory_path}' 及其子資料夾中沒有找到任何 .xlsx 檔案。")

    return all_directory_results


def analyze_multiple_root_directories(root_directory_paths):
    """
    遍歷多個根資料夾，分析其中所有 Excel 檔案 (包含子資料夾) 的交易數據，
    並將所有結果彙整成一個表格。

    Args:
        root_directory_paths (list): 包含要分析的根資料夾路徑的列表。

    Returns:
        pandas.DataFrame: 包含所有檔案分析結果的表格，如果沒有檔案則返回 None。
    """
    all_results_list = []
    for path in root_directory_paths:
        all_results_list.extend(analyze_all_excel_in_directory_recursive(path))

    if not all_results_list:
        print("在所有指定的根資料夾中都沒有找到任何可分析的 .xlsx 檔案。")
        return None

    # 將結果列表轉換為 pandas DataFrame
    df_results = pd.DataFrame(all_results_list)

    # --- 新增的數字提取邏輯 ---
    # 提取「所屬資料夾 (簡稱)」欄位中的數字
    # 使用 apply 和正規表達式，如果找不到數字則保留原始值或設為 None
    def extract_numbers(text):
        if pd.isna(text):  # 處理 NaN 值
            return None
        match = re.search(r'\d+', str(text))
        return match.group(0) if match else None  # 如果沒有找到數字，返回 None

    df_results["所屬資料夾 (簡稱)"] = df_results["所屬資料夾 (簡稱)"].apply(extract_numbers)
    df_results["檔案名稱"] = df_results["檔案名稱"].apply(extract_numbers)

    # --- 欄位重命名和順序調整邏輯 ---
    # 1. 定義重命名映射
    rename_mapping = {
        "所屬資料夾 (簡稱)": "商務大使",
        "檔案名稱": "被邀請人UID"
    }
    df_results = df_results.rename(columns=rename_mapping)

    # 2. 定義最終的欄位順序 (使用新的欄位名稱)
    final_column_order = [
        "商務大使",  # 原來的 "所屬資料夾 (簡稱)"
        "被邀請人UID",  # 原來的 "檔案名稱"
        "總交易筆數",
        "總交易日數",
        "總交易對數",
        "所有單筆交易持倉時間總和 (分鐘)",  # 單位改為分鐘
        "平均持倉時間 (分鐘)",
        "淨虧損交易筆數",
        "淨虧損交易比率",
        "總已實現盈虧",
        "總手续费",
        "盈虧/手續費比率"
    ]

    # 處理可能存在的錯誤訊息欄位
    if "錯誤" in df_results.columns:
        final_column_order.append("錯誤")

    # 確保所有預期的欄位都存在於 df_results 中，如果沒有則添加並填充 NaN
    for col in final_column_order:
        if col not in df_results.columns:
            df_results[col] = pd.NA  # 使用 pandas.NA 來表示缺失值

    # 3. 重新排列欄位
    df_results = df_results[final_column_order]

    return df_results


# --- 如何在本地使用這段程式碼 ---

# 1. 安裝 pandas 和 openpyxl (如果尚未安裝)
#    在您的終端機或命令提示字元中執行:
#    pip install pandas openpyxl

# 2. 將這段程式碼儲存為一個 .py 檔案 (例如 analyze_recursive_trades_with_folder_name.py)。

# 3. 指定您要分析的根資料夾路徑列表。
#    請將 'path/to/your/top_level_folder1' 替換為您實際的資料夾路徑。
#    例如，根據您的截圖，您會將 '商務大使09.22' 的完整路徑放入此列表中。
root_directories_to_analyze = [
    '/Users/kabellatsang/PycharmProjects/pythonProject3/商務大使09.22', '/Users/kabellatsang/PycharmProjects/pythonProject3/商務大使09.28' # 替換為您的實際路徑，例如 'C:/Users/YourUser/Desktop/商務大使09.22'
    # 'C:/Users/YourUser/Documents/OtherTradeData', # 範例：另一個需要遞迴分析的根資料夾
]

# 如果您想分析程式碼所在的資料夾及其所有子資料夾，可以使用以下設定：
# root_directories_to_analyze = ['.']

# 4. 執行分析
print("開始分析...")
final_table = analyze_multiple_root_directories(root_directories_to_analyze)

# 5. 打印所有結果表格
print("\n\n=== 所有檔案的分析結果總覽 (表格形式) ===")
if final_table is not None:
    # 為了更好的顯示效果，可以調整 pandas 的顯示選項
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)  # 寬度
    pd.set_option('display.colheader_justify', 'left')  # 表頭對齊

    print(final_table.to_string(index=False))  # to_string() 避免截斷，index=False 不顯示索引

    # --- 新增的 CSV 導出邏輯 ---
    # 獲取當前時間，用於生成唯一的檔案名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"交易分析結果_{timestamp}.csv"

    try:
        final_table.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\n分析結果已成功導出至：{os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"\n導出 CSV 檔案時發生錯誤: {e}")
else:
    print("沒有找到任何可分析的 .xlsx 檔案或發生錯誤。")

