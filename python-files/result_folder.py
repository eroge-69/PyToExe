import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog

def combine_coupang_orders():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="쿠팡 발주서 폴더 선택")

    if not folder_selected:
        print("❌ 폴더가 선택되지 않았습니다.")
        return

    combined_df = pd.DataFrame()

    for file in os.listdir(folder_selected):
        if file.endswith('.xlsx'):
            file_path = os.path.join(folder_selected, file)
            try:
                # F13 셀에서 입고예정일시 추출
                preview = pd.read_excel(file_path, header=None, nrows=20, usecols="F")
                incoming_date = preview.iloc[12, 0]

                # 20행부터 발주 데이터 읽기
                df = pd.read_excel(file_path, skiprows=19)

                # 실제 컬럼명
                item_col = '상품명/옵션/BARCODE'
                expected_columns = ['상품코드', item_col, '발주수량', '입고수량', '공급가']
                for col in expected_columns:
                    if col not in df.columns:
                        raise ValueError(f"[{file}] 컬럼 누락: '{col}'")

                # 불필요한 행 제거
                df = df[~df['상품코드'].isin(['SKU ID', '메시지 카테고리 코드'])]

                # 입고금액 처리
                if '입고금액' not in df.columns:
                    df['입고금액'] = 0
                else:
                    df['입고금액'] = df['입고금액'].fillna(0)

                df['입고예정일시'] = pd.to_datetime(incoming_date).date()
                combined_df = pd.concat([combined_df, df], ignore_index=True)

            except Exception as e:
                print(f"⚠️ {file} 처리 중 오류 발생: {e}")

    if combined_df.empty:
        print("❌ 처리된 데이터가 없습니다.")
        return

    # 그룹화 및 집계
    result = combined_df.groupby(['입고예정일시', '상품코드', item_col], as_index=False).agg({
        '발주수량': 'sum',
        '입고수량': 'sum',
        '공급가': 'first',
        '입고금액': 'sum'
    })

    # 출력용 컬럼명 변경
    result = result.rename(columns={item_col: '상품명'})

    # 저장
    output_path = os.path.join(folder_selected, "쿠팡_발주_정리.xlsx")
    result.to_excel(output_path, index=False)
    print(f"\n✅ 정리된 엑셀 파일이 저장되었습니다:\n{output_path}")

if __name__ == "__main__":
    combine_coupang_orders()
