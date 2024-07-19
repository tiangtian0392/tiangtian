function getFormattedDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    const second = String(now.getSeconds()).padStart(2, '0');
    return `${year}${month}${day}_${hour}${minute}${second}`;
}

function exportToCSV(rows) {
    let csvContent = "\uFEFF";  // 添加BOM

    rows.forEach(rowArray => {
        let row = rowArray.map(cell => `"${cell.replace(/'/g, '')}"`).join(",");  // 去掉单引号并添加双引号
        csvContent += row + "\r\n";
    });

    const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `data_${getFormattedDateTime()}.csv`);
    document.body.appendChild(link);
    link.click();
}

function extractTableData() {
    const titleTable = document.querySelector("#__grid_goods_grid > div:nth-child(2) > div.xhdr > table > tbody");
    const contentTable = document.querySelector("#__grid_goods_grid > div:nth-child(2) > div.objbox > table > tbody");

    const titleRows = Array.from(titleTable.rows);
    const contentRows = Array.from(contentTable.rows);
    const filteredRows = [];

    // 目标列顺序
    const targetColumns = ["配送状態", "注文番号", "カート番号", "配送会社", "送り状番号", "発送日", "注文日", "入金日", "お届け希望日", "発送予定日", "配送完了日", "配送方法", "商品番号", "商品名", "数量", "オプション情報", "オプションコード", "おまけ", "受取人名", "受取人名(フリガナ)", "受取人電話番号", "受取人携帯電話番号", "住所", "郵便番号", "国家", "送料の決済", "決済サイト", "通貨", "購入者決済金額", "販売価格", "割引額", "注文金額の合計", "供給原価の合計", "購入者名", "購入者名(フリガナ)", "配送要請事項", "購入者電話番号", "購入者携帯電話番号", "販売者商品コード", "JANコード", "規格番号", "プレゼント贈り主", "外部広告", "素材", "ギフト注文"];

    // 获取标题行数据，使用第二行作为标题
    let headers = [];
    if (titleRows.length > 1) {
        headers = Array.from(titleRows[1].cells).map(cell => cell.innerText.trim());
    }

    // 重新排序标题行
    const orderedHeaders = targetColumns.map(col => headers.includes(col) ? col : '');

    filteredRows.push(orderedHeaders);

    // 用于记录已处理的地址
    const seenAddresses = new Set();

    // 获取内容行数据
    contentRows.forEach(row => {
        const img = row.querySelector('img');
        if (img && img.src.includes('item_chk1.gif')) {
            const cells = Array.from(row.cells).map(cell => cell.innerText.trim());
            const rowData = {};

            // 建立列名和单元格值的对应关系
            headers.forEach((header, index) => {
                rowData[header] = cells[index];
            });

            // 检查地址列是否已经存在
            if (rowData["住所"] && !seenAddresses.has(rowData["住所"])) {
                seenAddresses.add(rowData["住所"]);

                // 按目标列顺序重新排列数据
                const orderedRow = targetColumns.map(col => {
                    // 去掉“郵便番号”列中的单引号
                    if (col === "郵便番号") {
                        return (rowData[col] || '').replace(/'/g, '');
                    }
                    return rowData[col] || '';
                });

                filteredRows.push(orderedRow);
            }
        }
    });

    exportToCSV(filteredRows);
}

// 执行提取和导出操作
extractTableData();
