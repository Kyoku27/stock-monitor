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
