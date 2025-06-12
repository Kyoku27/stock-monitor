async function queryRakuten() {
  const manage = document.getElementById("manage-number").value.trim();
  const rawSkus = document.getElementById("sku-list").value.trim().replace(/[\n,]+/g, ",");
  const skus = rawSkus.split(",").map(s => s.trim()).filter(Boolean);

  if (!manage || skus.length === 0) {
    alert("请填写管理番号和至少一个 SKU！");
    return;
  }

  const url = `/api/stock/rakuten?manage=${encodeURIComponent(manage)}&` + 
              skus.map(s => `sku=${encodeURIComponent(s)}`).join("&");

  const res = await fetch(url);
  const data = await res.json();

  const table = document.getElementById("stock-table");
  table.innerHTML = "";

  data.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.variantId || item.sku}</td>
      <td>${item.quantity ?? '—'}</td>
      <td>${item.updated ?? '—'}</td>
    `;
    table.appendChild(tr);
  });
}

async function fetchStock(manage, skuList) {
  const url = `/api/stock/rakuten?manage=${manage}&` + skuList.map(sku => `sku=${sku}`).join("&")
  const res = await fetch(url)
  return await res.json()
}

function filterStock() {
  const brand = document.getElementById('brandFilter').value
  const keyword = document.getElementById('skuInput').value.trim().toLowerCase()

  const filtered = window.allStock.filter(row => {
    return (!brand || row.brand === brand) &&
           (!keyword || row.sku.toLowerCase().includes(keyword))
  })

  updateTable(filtered)
}

function updateTable(data) {
  const tbody = document.querySelector("#stock-table tbody")
  tbody.innerHTML = data.map(row => `
    <tr>
      <td>${row.sku}</td>
      <td>${row.rakuten_stock}</td>
      <td>${row.google_stock}</td>
    </tr>
  `).join("")
}

// 初始加载
(async () => {
  const res = await fetch("/api/stock/rakuten?manage=smartpetfeeder&sku=PF20-SS&sku=PF20-CC")
  const data = await res.json()
  window.allStock = data
  updateTable(data)
})()
