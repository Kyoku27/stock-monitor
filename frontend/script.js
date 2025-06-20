<script>
let allMappingData = [];

async function fetchMappingData() {
  const res = await fetch("/api/stock/mapping");
  const data = await res.json();
  allMappingData = data;
  populateBrandFilter(data);
  loadStock(); // 初期化加载
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

async function renderTable(data) {
  const tbody = document.getElementById("stock-table");
  tbody.innerHTML = "";

  if (data.length === 0) {
    tbody.innerHTML = "<tr><td colspan='5'>一致するデータがありません</td></tr>";
    return;
  }

  for (const row of data) {
    const sku = row["システム連携用SKU番号"] || row["型番"];
    const brand = row["ブランド"] || "-";

    let rakuten = "-";
    let googleSelf = "-";
    let googleCity = "-";

    try {
      const res = await fetch(`/api/stock/real?sku=${encodeURIComponent(sku)}`);
      const json = await res.json();

      // 乐天库存是一个字段
      rakuten = json["楽天在庫"] ?? "-";

      const stock = json["在庫"] || {};
      if (brand === "HRP") {
        googleSelf = stock["自社"] ?? "-";
        googleCity = stock["City"] ?? "-";
      } else {
        googleSelf = stock["在庫"] ?? "-";
      }
    } catch (e) {
      console.error("在庫取得失敗", e);
    }

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${brand}</td>
      <td>${sku}</td>
      <td>${rakuten}</td>
      <td>${googleSelf}</td>
      <td>${googleCity}</td>
    `;
    tbody.appendChild(tr);
  }
}

function loadStock() {
  const skuKeyword = document.getElementById("skuSearch").value.trim().toLowerCase();
  const selectedBrand = document.getElementById("brandFilter").value;

  const filtered = allMappingData.filter(row => {
    const sku = (row["型番"] || row["システム連携用SKU番号"] || "").toLowerCase();
    const brand = row["ブランド"] || "";
    return (!skuKeyword || sku.includes(skuKeyword)) &&
           (!selectedBrand || brand === selectedBrand);
  });

  renderTable(filtered);
}

fetchMappingData(); // 页面初始化时加载
</script>

