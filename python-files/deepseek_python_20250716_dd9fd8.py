import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

# Thiết lập chung
st.set_page_config(page_title="Phân Tích Giá & Lợi Nhuận", page_icon="📊", layout="wide")
st.title("📊 Phân Tích Giá & Lợi Nhuận Thiết Bị Nhập Khẩu")

# Hàm định dạng số
def format_currency(x):
    if abs(x) >= 1e9:
        return f"{x/1e9:,.2f} tỷ"
    elif abs(x) >= 1e6:
        return f"{x/1e6:,.2f} triệu"
    return f"{x:,.0f}"

def format_percent(x):
    return f"{x*100:.2f}%"

# Hàm tính toán
def calculate_pricing(unit_price, quantity, profit_rate, commission_rate, 
                     import_tax_rate, accessories_cost, exchange_rate=28500, 
                     corporate_tax_rate=0.2, vat_rate=0.1):
    # Tính toán cơ bản
    ex_value = unit_price * quantity
    cif_value = ex_value + accessories_cost
    
    # Tính thuế nhập khẩu
    import_tax = cif_value * import_tax_rate
    
    # Tính giá trị VND
    ex_value_vnd = ex_value * exchange_rate
    cif_value_vnd = cif_value * exchange_rate
    import_tax_vnd = import_tax * exchange_rate
    
    # Tính hoa hồng
    commission = cif_value * commission_rate
    commission_vnd = commission * exchange_rate
    
    # Tính tổng chi phí trước lợi nhuận
    total_cost = cif_value + import_tax + commission
    total_cost_vnd = total_cost * exchange_rate
    
    # Tính giá bán mong muốn
    desired_profit = total_cost * profit_rate
    selling_price = total_cost + desired_profit
    selling_price_vnd = selling_price * exchange_rate
    
    # Tính VAT
    vat_amount = selling_price * vat_rate
    vat_amount_vnd = vat_amount * exchange_rate
    
    # Tính giá bán bao gồm VAT
    selling_price_inc_vat = selling_price + vat_amount
    selling_price_inc_vat_vnd = selling_price_inc_vat * exchange_rate
    
    # Tính thuế TNDN
    corporate_tax = (selling_price - total_cost) * corporate_tax_rate
    corporate_tax_vnd = corporate_tax * exchange_rate
    
    # Tính lợi nhuận sau thuế
    net_profit = (selling_price - total_cost) - corporate_tax
    net_profit_vnd = net_profit * exchange_rate
    
    # Tính giá cạnh tranh
    min_selling_price = total_cost * 1.05  # Giá bán tối thiểu (lợi nhuận 5%)
    max_selling_price = total_cost * 1.25  # Giá bán tối đa (lợi nhuận 25%)
    
    return {
        "ex_value": ex_value,
        "ex_value_vnd": ex_value_vnd,
        "cif_value": cif_value,
        "cif_value_vnd": cif_value_vnd,
        "import_tax": import_tax,
        "import_tax_vnd": import_tax_vnd,
        "commission": commission,
        "commission_vnd": commission_vnd,
        "total_cost": total_cost,
        "total_cost_vnd": total_cost_vnd,
        "desired_profit": desired_profit,
        "desired_profit_vnd": desired_profit * exchange_rate,
        "selling_price": selling_price,
        "selling_price_vnd": selling_price_vnd,
        "vat_amount": vat_amount,
        "vat_amount_vnd": vat_amount_vnd,
        "selling_price_inc_vat": selling_price_inc_vat,
        "selling_price_inc_vat_vnd": selling_price_inc_vat_vnd,
        "corporate_tax": corporate_tax,
        "corporate_tax_vnd": corporate_tax_vnd,
        "net_profit": net_profit,
        "net_profit_vnd": net_profit_vnd,
        "min_selling_price": min_selling_price,
        "min_selling_price_vnd": min_selling_price * exchange_rate,
        "max_selling_price": max_selling_price,
        "max_selling_price_vnd": max_selling_price * exchange_rate,
        "exchange_rate": exchange_rate
    }

# Hàm tạo PDF
def create_pdf(results, unit_price, quantity, profit_rate, commission_rate, 
              import_tax_rate, accessories_cost, exchange_rate):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Tiêu đề
    title = Paragraph("Báo Cáo Phân Tích Giá & Lợi Nhuận", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Thông số đầu vào
    input_data = [
        ["Thông số", "Giá trị"],
        ["Đơn giá thiết bị (EUR)", f"{unit_price:,.2f}"],
        ["Số lượng", f"{quantity}"],
        ["Tỷ lệ lợi nhuận mong muốn", f"{profit_rate*100:.2f}%"],
        ["Tỷ lệ hoa hồng", f"{commission_rate*100:.2f}%"],
        ["Thuế nhập khẩu", f"{import_tax_rate*100:.2f}%"],
        ["Giá phụ tùng (EUR)", f"{accessories_cost:,.2f}"],
        ["Tỷ giá EUR/VND", f"{exchange_rate:,.0f}"]
    ]
    
    input_table = Table(input_data)
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Thông Số Đầu Vào", styles['Heading2']))
    elements.append(input_table)
    elements.append(Spacer(1, 12))
    
    # Kết quả tính toán (EUR)
    eur_data = [
        ["Hạng mục", "Giá trị (EUR)"],
        ["Giá EX", f"{results['ex_value']:,.2f}"],
        ["Giá CIF", f"{results['cif_value']:,.2f}"],
        ["Thuế nhập khẩu", f"{results['import_tax']:,.2f}"],
        ["Hoa hồng", f"{results['commission']:,.2f}"],
        ["Tổng chi phí", f"{results['total_cost']:,.2f}"],
        ["Giá bán dự kiến", f"{results['selling_price']:,.2f}"],
        ["VAT", f"{results['vat_amount']:,.2f}"],
        ["Giá bán bao gồm VAT", f"{results['selling_price_inc_vat']:,.2f}"],
        ["Thuế TNDN", f"{results['corporate_tax']:,.2f}"],
        ["Lợi nhuận sau thuế", f"{results['net_profit']:,.2f}"]
    ]
    
    eur_table = Table(eur_data)
    eur_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Kết Quả Tính Toán (EUR)", styles['Heading2']))
    elements.append(eur_table)
    elements.append(Spacer(1, 12))
    
    # Kết quả tính toán (VND)
    vnd_data = [
        ["Hạng mục", "Giá trị (VND)"],
        ["Giá EX", format_currency(results['ex_value_vnd'])],
        ["Giá CIF", format_currency(results['cif_value_vnd'])],
        ["Thuế nhập khẩu", format_currency(results['import_tax_vnd'])],
        ["Hoa hồng", format_currency(results['commission_vnd'])],
        ["Tổng chi phí", format_currency(results['total_cost_vnd'])],
        ["Giá bán dự kiến", format_currency(results['selling_price_vnd'])],
        ["VAT", format_currency(results['vat_amount_vnd'])],
        ["Giá bán bao gồm VAT", format_currency(results['selling_price_inc_vat_vnd'])],
        ["Thuế TNDN", format_currency(results['corporate_tax_vnd'])],
        ["Lợi nhuận sau thuế", format_currency(results['net_profit_vnd'])]
    ]
    
    vnd_table = Table(vnd_data)
    vnd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Kết Quả Tính Toán (VND)", styles['Heading2']))
    elements.append(vnd_table)
    elements.append(Spacer(1, 12))
    
    # Giá cạnh tranh
    comp_data = [
        ["Loại giá", "EUR", "VND"],
        ["Giá tối thiểu", 
         f"{results['min_selling_price']:,.2f}", 
         format_currency(results['min_selling_price_vnd'])],
        ["Giá đề xuất", 
         f"{results['selling_price']:,.2f}", 
         format_currency(results['selling_price_vnd'])],
        ["Giá tối đa", 
         f"{results['max_selling_price']:,.2f}", 
         format_currency(results['max_selling_price_vnd'])]
    ]
    
    comp_table = Table(comp_data)
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(Paragraph("Phạm Vi Giá Cạnh Tranh", styles['Heading2']))
    elements.append(comp_table)
    
    # Tạo PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Sidebar - Nhập thông số
with st.sidebar:
    st.header("Thông Số Đầu Vào")
    
    unit_price = st.number_input("Đơn giá thiết bị (EUR)", min_value=0.0, value=10000.0, step=100.0)
    quantity = st.number_input("Số lượng", min_value=1, value=1, step=1)
    profit_rate = st.slider("Lợi nhuận mong muốn (%)", min_value=5, max_value=50, value=18, step=1) / 100
    commission_rate = st.slider("Tỷ lệ hoa hồng (%)", min_value=0, max_value=20, value=5, step=1) / 100
    import_tax_rate = st.slider("Thuế nhập khẩu (%)", min_value=0, max_value=50, value=10, step=1) / 100
    accessories_cost = st.number_input("Giá phụ tùng (EUR)", min_value=0.0, value=500.0, step=50.0)
    exchange_rate = st.number_input("Tỷ giá EUR/VND", min_value=10000, max_value=50000, value=28500, step=100)
    
    st.divider()
    st.caption("Tính toán dựa trên thuế TNDN 20% và VAT 10%")

# Tính toán kết quả
results = calculate_pricing(
    unit_price, quantity, profit_rate, commission_rate, 
    import_tax_rate, accessories_cost, exchange_rate
)

# Hiển thị kết quả
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tổng chi phí", format_currency(results['total_cost_vnd']))
with col2:
    st.metric("Giá bán đề xuất", format_currency(results['selling_price_inc_vat_vnd']))
with col3:
    profit_percent = (results['net_profit'] / results['total_cost']) * 100
    st.metric("Lợi nhuận sau thuế", format_currency(results['net_profit_vnd']), f"{profit_percent:.2f}%")

# Tab hiển thị kết quả
tab1, tab2, tab3, tab4 = st.tabs(["Phân Tích Chi Tiết", "Biểu Đồ Phân Bổ", "Giá Cạnh Tranh", "Xuất Báo Cáo"])

with tab1:
    st.subheader("Phân Tích Chi Tiết")
    
    # Tạo DataFrame cho kết quả
    data = {
        "Hạng mục": [
            "Giá EX (EUR)", "Giá EX (VND)",
            "Giá CIF (EUR)", "Giá CIF (VND)",
            "Thuế nhập khẩu (EUR)", "Thuế nhập khẩu (VND)",
            "Hoa hồng (EUR)", "Hoa hồng (VND)",
            "Tổng chi phí (EUR)", "Tổng chi phí (VND)",
            "Giá bán dự kiến (EUR)", "Giá bán dự kiến (VND)",
            "VAT (EUR)", "VAT (VND)",
            "Giá bán bao gồm VAT (EUR)", "Giá bán bao gồm VAT (VND)",
            "Thuế TNDN (EUR)", "Thuế TNDN (VND)",
            "Lợi nhuận sau thuế (EUR)", "Lợi nhuận sau thuế (VND)"
        ],
        "Giá trị": [
            results['ex_value'], results['ex_value_vnd'],
            results['cif_value'], results['cif_value_vnd'],
            results['import_tax'], results['import_tax_vnd'],
            results['commission'], results['commission_vnd'],
            results['total_cost'], results['total_cost_vnd'],
            results['selling_price'], results['selling_price_vnd'],
            results['vat_amount'], results['vat_amount_vnd'],
            results['selling_price_inc_vat'], results['selling_price_inc_vat_vnd'],
            results['corporate_tax'], results['corporate_tax_vnd'],
            results['net_profit'], results['net_profit_vnd']
        ]
    }
    
    df = pd.DataFrame(data)
    df['Giá trị'] = df['Giá trị'].apply(format_currency)
    st.dataframe(df, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Phân Bổ Chi Phí & Lợi Nhuận")
    
    # Dữ liệu cho biểu đồ
    cost_components = {
        "Giá EX": results['ex_value'],
        "Phụ tùng": accessories_cost,
        "Thuế nhập khẩu": results['import_tax'],
        "Hoa hồng": results['commission']
    }
    
    revenue_components = {
        "Tổng chi phí": results['total_cost'],
        "Thuế TNDN": results['corporate_tax'],
        "Lợi nhuận sau thuế": results['net_profit']
    }
    
    # Vẽ biểu đồ
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Biểu đồ phân bổ chi phí
    ax1.pie(cost_components.values(), labels=cost_components.keys(), autopct='%1.1f%%',
            colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    ax1.set_title('Phân Bổ Chi Phí (EUR)')
    
    # Biểu đồ phân bổ doanh thu
    ax2.pie(revenue_components.values(), labels=revenue_components.keys(), autopct='%1.1f%%',
            colors=['#66b3ff','#99ff99','#ffcc99'])
    ax2.set_title('Phân Bổ Doanh Thu (EUR)')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Biểu đồ giá cạnh tranh
    st.subheader("Phạm Vi Giá Cạnh Tranh")
    
    price_range = {
        "Giá tối thiểu": results['min_selling_price_vnd'],
        "Giá đề xuất": results['selling_price_vnd'],
        "Giá tối đa": results['max_selling_price_vnd']
    }
    
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.barh(list(price_range.keys()), list(price_range.values()), color=['#ff9999', '#66b3ff', '#99ff99'])
    
    # Định dạng trục x
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: format_currency(x)))
    
    # Thêm giá trị trên mỗi cột
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                format_currency(width), 
                ha='left', va='center')
    
    plt.title('Phạm Vi Giá Cạnh Tranh (VND)')
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    st.subheader("Chiến Lược Giá Cạnh Tranh")
    
    # Bảng so sánh giá
    comp_data = {
        "Loại giá": ["Giá tối thiểu", "Giá đề xuất", "Giá tối đa"],
        "EUR": [
            results['min_selling_price'], 
            results['selling_price'], 
            results['max_selling_price']
        ],
        "VND": [
            results['min_selling_price_vnd'], 
            results['selling_price_vnd'], 
            results['max_selling_price_vnd']
        ],
        "Lợi nhuận sau thuế (VND)": [
            (results['min_selling_price'] - results['total_cost']) * 0.8 * exchange_rate,
            results['net_profit_vnd'],
            (results['max_selling_price'] - results['total_cost']) * 0.8 * exchange_rate
        ],
        "Tỷ suất lợi nhuận": [
            f"{((results['min_selling_price'] - results['total_cost']) * 0.8 / results['min_selling_price'])*100:.2f}%",
            f"{(results['net_profit'] / results['selling_price'])*100:.2f}%",
            f"{((results['max_selling_price'] - results['total_cost']) * 0.8 / results['max_selling_price'])*100:.2f}%"
        ]
    }
    
    df_comp = pd.DataFrame(comp_data)
    df_comp['EUR'] = df_comp['EUR'].apply(lambda x: f"{x:,.2f}")
    df_comp['VND'] = df_comp['VND'].apply(format_currency)
    df_comp['Lợi nhuận sau thuế (VND)'] = df_comp['Lợi nhuận sau thuế (VND)'].apply(format_currency)
    
    st.dataframe(df_comp, hide_index=True, use_container_width=True)
    
    # Phân tích chiến lược
    st.subheader("Phân Tích Chiến Lược")
    
    st.markdown(f"""
    **Giá tối thiểu ({format_currency(results['min_selling_price_vnd'])})**:
    - Tỷ suất lợi nhuận: {df_comp.loc[0, 'Tỷ suất lợi nhuận']}
    - Lợi nhuận sau thuế: {format_currency(comp_data['Lợi nhuận sau thuế (VND)'][0])}
    - **Chiến lược**: Giới thiệu sản phẩm, cạnh tranh giá, thị trường nhạy cảm về giá
    """)
    
    st.markdown(f"""
    **Giá đề xuất ({format_currency(results['selling_price_vnd'])})**:
    - Tỷ suất lợi nhuận: {df_comp.loc[1, 'Tỷ suất lợi nhuận']}
    - Lợi nhuận sau thuế: {format_currency(comp_data['Lợi nhuận sau thuế (VND)'][1])}
    - **Chiến lược**: Cân bằng giữa cạnh tranh và lợi nhuận, phù hợp cho hầu hết thị trường
    """)
    
    st.markdown(f"""
    **Giá tối đa ({format_currency(results['max_selling_price_vnd'])})**:
    - Tỷ suất lợi nhuận: {df_comp.loc[2, 'Tỷ suất lợi nhuận']}
    - Lợi nhuận sau thuế: {format_currency(comp_data['Lợi nhuận sau thuế (VND)'][2])}
    - **Chiến lược**: Sản phẩm cao cấp, thị trường ít nhạy cảm về giá, khách hàng doanh nghiệp
    """)

with tab4:
    st.subheader("Xuất Báo Cáo")
    
    # Xuất Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # Tạo sheet kết quả
        result_data = {
            "Hạng mục": [
                "Đơn giá thiết bị (EUR)", "Số lượng", "Tỷ lệ lợi nhuận", "Tỷ lệ hoa hồng",
                "Thuế nhập khẩu", "Giá phụ tùng (EUR)", "Tỷ giá EUR/VND",
                "Giá EX (EUR)", "Giá EX (VND)",
                "Giá CIF (EUR)", "Giá CIF (VND)",
                "Thuế nhập khẩu (EUR)", "Thuế nhập khẩu (VND)",
                "Hoa hồng (EUR)", "Hoa hồng (VND)",
                "Tổng chi phí (EUR)", "Tổng chi phí (VND)",
                "Giá bán dự kiến (EUR)", "Giá bán dự kiến (VND)",
                "VAT (EUR)", "VAT (VND)",
                "Giá bán bao gồm VAT (EUR)", "Giá bán bao gồm VAT (VND)",
                "Thuế TNDN (EUR)", "Thuế TNDN (VND)",
                "Lợi nhuận sau thuế (EUR)", "Lợi nhuận sau thuế (VND)",
                "Giá tối thiểu (EUR)", "Giá tối thiểu (VND)",
                "Giá tối đa (EUR)", "Giá tối đa (VND)"
            ],
            "Giá trị": [
                unit_price, quantity, profit_rate, commission_rate,
                import_tax_rate, accessories_cost, exchange_rate,
                results['ex_value'], results['ex_value_vnd'],
                results['cif_value'], results['cif_value_vnd'],
                results['import_tax'], results['import_tax_vnd'],
                results['commission'], results['commission_vnd'],
                results['total_cost'], results['total_cost_vnd'],
                results['selling_price'], results['selling_price_vnd'],
                results['vat_amount'], results['vat_amount_vnd'],
                results['selling_price_inc_vat'], results['selling_price_inc_vat_vnd'],
                results['corporate_tax'], results['corporate_tax_vnd'],
                results['net_profit'], results['net_profit_vnd'],
                results['min_selling_price'], results['min_selling_price_vnd'],
                results['max_selling_price'], results['max_selling_price_vnd']
            ]
        }
        df_result = pd.DataFrame(result_data)
        df_result.to_excel(writer, sheet_name='Kết Quả Tính Toán', index=False)
        
        # Tạo sheet phân tích
        analysis_data = {
            "Loại giá": ["Giá tối thiểu", "Giá đề xuất", "Giá tối đa"],
            "EUR": [
                results['min_selling_price'], 
                results['selling_price'], 
                results['max_selling_price']
            ],
            "VND": [
                results['min_selling_price_vnd'], 
                results['selling_price_vnd'], 
                results['max_selling_price_vnd']
            ],
            "Lợi nhuận sau thuế (VND)": [
                (results['min_selling_price'] - results['total_cost']) * 0.8 * exchange_rate,
                results['net_profit_vnd'],
                (results['max_selling_price'] - results['total_cost']) * 0.8 * exchange_rate
            ],
            "Tỷ suất lợi nhuận": [
                ((results['min_selling_price'] - results['total_cost']) * 0.8 / results['min_selling_price'])*100,
                (results['net_profit'] / results['selling_price'])*100,
                ((results['max_selling_price'] - results['total_cost']) * 0.8 / results['max_selling_price'])*100
            ]
        }
        df_analysis = pd.DataFrame(analysis_data)
        df_analysis.to_excel(writer, sheet_name='Phân Tích Giá Cạnh Tranh', index=False)
    
    excel_buffer.seek(0)
    
    # Xuất PDF
    pdf_buffer = create_pdf(
        results, unit_price, quantity, profit_rate, commission_rate, 
        import_tax_rate, accessories_cost, exchange_rate
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Tải Xuống Excel",
            data=excel_buffer,
            file_name="phan_tich_gia_loi_nhuan.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    with col2:
        st.download_button(
            label="📥 Tải Xuống PDF",
            data=pdf_buffer,
            file_name="bao_cao_phan_tich_gia.pdf",
            mime="application/pdf"
        )
    
    st.success("Nhấn nút phía trên để tải báo cáo đầy đủ")

# Footer
st.divider()
st.caption("Công cụ Phân Tích Giá & Lợi Nhuận - © 2024 | Phiên bản 1.0")