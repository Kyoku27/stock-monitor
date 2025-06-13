let allMappingData = [];

async function fetchMappingData() {
  const res = await fetch("/api/stock/mapping");
  const data = await res.json();
  allMappingData = data;
  populateBrandFilter(data);
  renderTable(data); // 默认全显示
}

function populateBrandFilter(data) {
  const select = document.getElementById("brandFilter");
  const brands = Array.from(new Set(data.map(row => row["ブランド"]).filter(Boolean))).sort();
  select.innerHTML = '<option value="">すべて</option>';
  brands.forEach(brand => {
    const option = document.createElement("option");
    option.value = brand;
    option.textContent = brand;
    select.appendChild(option);
  });
}

function renderTable(data) {
  const tbody = document.getElementById("stock-table");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = "<tr><td colspan='4'>一致するデータがありません</td></tr>";
    return;
  }

  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row["ブランド"] || "-"}</td>
      <td>${row["システム連携用SKU番号"] || "-"}</td>
      <td>-</td> <!-- 楽天在庫：暂时空 -->
      <td>${row["在庫"] || "-"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function loadStock() {
  const skuKeyword = document.getElementById("skuSearch").value.trim().toLowerCase();
  const selectedBrand = document.getElementById("brandFilter").value;

  const filtered = allMappingData.filter(row => {
    const sku = (row["システム連携用SKU番号"] || "").toLowerCase();
    const brand = row["ブランド"] || "";
    return (!skuKeyword || sku.includes(skuKeyword)) &&
           (!selectedBrand || brand === selectedBrand);
  });

  renderTable(filtered);
}

// 初始化
fetchMappingData();

