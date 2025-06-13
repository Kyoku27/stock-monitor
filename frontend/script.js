async function loadStock() {
  const manageNumber = "smartpetfeeder"; // 目前固定为 smartpetfeeder
  const skuInput = document.getElementById("skuSearch").value.trim();
  const brand = document.getElementById("brandFilter").value;

  // 获取 SKU 映射表
  const mapRes = await fetch("/api/stock/mapping");
  const mapping = await mapRes.json();

  let filtered = mapping;

  if (skuInput) {
    const keyword = skuInput.toLowerCase();
    filtered = filtered.filter(row =>
      row["システム連携用SKU番号"].toLowerCase().includes(keyword)
    );
  }

  if (brand) {
    filtered = filtered.filter(row => row["ブランド"] === brand);
  }

  const skuList = filtered.map(row => row["システム連携用SKU番号"]);
  if (skuList.length === 0) {
    document.getElementById("stock-table").innerHTML =
      "<tr><td colspan='4'>一致するデータがありません</td></tr>";
    return;
  }

  // 调用在庫API
  const query = skuList.map(sku => `sku=${encodeURIComponent(sku)}`).join("&");
  const res = await fetch(`/api/stock/rakuten?manage=${manageNumber}&${query}`);
  const data = await res.json();

  const tableBody = document.getElementById("stock-table");
  tableBody.innerHTML = "";

  data.forEach(row => {
    const brandName = (mapping.find(m => m["システム連携用SKU番号"] === row.sku) || {})["ブランド"] || "";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${brandName}</td>
      <td>${row.sku}</td>
      <td>${row.rakuten}</td>
      <td>${row.google}</td>
    `;
    tableBody.appendChild(tr);
  });
}
