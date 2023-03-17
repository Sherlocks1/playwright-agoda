import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl import Workbook
from explaindata2 import explain_data
from openpyxl.styles import PatternFill

delete_html_files_input = input("是否删除所有 HTML 文件？输入 1 表示是，输入 0 表示否：")


def delete_html_files():
    for filename in os.listdir("."):
        if filename.endswith(".html"):
            os.remove(filename)


def save_data():
    # 指定保存 Excel 文件的路径
    filename = "results.xlsx"
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    xls_path = os.path.join(desktop_path, filename)

    # 如果文件已存在，则加载它
    wb = None
    if os.path.exists(xls_path) and os.path.isfile(xls_path):
        wb = load_workbook(xls_path)

    # 创建新的 Excel 文件
    if not wb:
        wb = Workbook()
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ws = wb.active
    ws.title = f"Sheet1_{current_time}"

    # 写入表头
    ws.cell(row=1, column=1, value="Check-in")
    ws.cell(row=1, column=2, value="Room Name")
    ws.cell(row=1, column=3, value="Price")
    ws.cell(row=1, column=4, value="Status")

    # 解析数据，并按 Check-in 列排序
    new_data = []
    for filename in os.listdir("."):
        if filename.endswith(".html"):
            with open(filename, "r", encoding="utf-8") as f:
                html_content = f.read()
                parsed_data = explain_data(html_content)

                # 将日期字符串转换为 datetime 对象
                for row in parsed_data:
                    date_string = row[0].replace("年", "-").replace("月", "-").replace("日", "")
                    row[0] = datetime.strptime(date_string, '%Y-%m-%d')
                    row[1] = [str(name) for name in row[1]]  # 更改 'Room Name' 列的格式
                new_data.extend(parsed_data)

    new_data = sorted(new_data, key=lambda row: row[0])

    # 如果文件已存在，则读取数据以供比较
    old_data = []
    if wb:
        sheet = wb.active
        for row in sorted(sheet.iter_rows(min_row=2, values_only=True), key=lambda x: x[0]):
            old_row = list(row)
            # 将列表类型转换为字符串类型
            old_row[1] = str(old_row[1])
            old_data.append(old_row)

    for new_row_num, new_row in enumerate(new_data, start=len(old_data) + 2):

        # 将日期格式化为字符串
        new_row[0] = new_row[0].strftime('%Y-%m-%d')

        # 将包含房间名称的列表转换为字符串
        new_room_names = ", ".join(map(str, new_row[1]))

        # 查找旧数据是否包含相同的行，并将新数据覆盖旧数据
        old_row_nums = [i + 1 for i, old_row in enumerate(old_data)
                        if old_row[0] == new_row[0]
                        and ", ".join(map(str, old_row[1])) == new_room_names]

        if old_row_nums:
            # 遍历每个匹配的旧行，并更新单元格值
            for old_row_num in old_row_nums:
                for col_num, col_value in enumerate(new_row, start=1):
                    cell = ws.cell(row=old_row_num, column=col_num)
                    try:
                        cell.value = col_value
                    except ValueError:
                        # 当值无法转换为 Excel 格式时，将其转换为字符串格式
                        if col_num == 2:
                            col_value = ", ".join(map(str, col_value))
                            cell.value = col_value
                        else:
                            print(f"ERROR: row {old_row_num}, column {col_num}, data: {col_value}")

                # 如果新数据的房态与旧行房态不完全匹配，则需要标记单元格
                old_status = ws.cell(row=old_row_num, column=4).value
                new_status = new_row[3]
                if old_status != new_status:
                    cell = ws.cell(row=old_row_num, column=4)
                    cell.fill = PatternFill("solid", fgColor="FFFF00")
                    cell.value = f"{old_status} -> {new_status}"
        else:
            # 如果未找到匹配的旧行，则将新数据添加到末尾
            for col_num, col_value in enumerate(new_row, start=1):
                cell = ws.cell(row=new_row_num, column=col_num)
                try:
                    cell.value = col_value
                except ValueError:
                    # 当值无法转换为 Excel 格式时，将其转换为字符串格式
                    if col_num == 2:
                        col_value = ", ".join(map(str, col_value))
                        cell.value = col_value
                    else:
                        print(f"ERROR: row {new_row_num}, column {col_num}, data: {col_value}")

    # 自动调整列宽
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 打印 Excel 文件路径
    print(f"Excel file path: {xls_path}")

    # 保存 Excel 文件
    wb.save(filename=xls_path)

    while True:
        if delete_html_files_input == "1":
            delete_html_files()
            break
        elif delete_html_files_input == "0":
            break
        else:
            print("输入无效，请重新输入。")

    # 保存成功的消息
    print(f"Excel file saved successfully to {xls_path}.")


if __name__ == '__main__':
    save_data()
