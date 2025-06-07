const skuList = ["CZR001", "CZR002", "CZR003"];

async function fetchStock(api, skus) {
  const query = skus.map(sku => "sku=" + sku).join("&");
  const res = await fetch(`/api/stock/${api}?` + query);
  return await res.json();
}

async function renderTable() {
  const tbody = document.getElementById("stock-table");
  const rakutenData = await fetchStock("rakuten", skuList);
  const gsheetData = await fetchStock("gsheet", skuList);

  tbody.innerHTML = "";
  skuList.forEach(sku => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${sku}</td>
      <td>${rakutenData[sku] ?? "-"}</td>
      <td>${gsheetData[sku] ?? "-"}</td>
    `;
    tbody.appendChild(tr);
  });
}

renderTable();
