// Thử app trên máy: mở trang chủ ở 1 ngày giả lập rồi bấm lần lượt mọi nút "Bắt đầu", báo lỗi nếu có.
// Chạy app trước:  cd work && HOCBA_FAKE_NOW=2026-11-15T15:00:00 HOCBA_DATA_FILE=/tmp/prog.json streamlit run app_main.py --server.port 8599 --server.headless true
// Rồi:  node tools/smoke_test.js
const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 1200, height: 1800}});
  await p.goto('http://localhost:8599'); await p.waitForTimeout(7000);
  let t = (await p.innerText('body')).replace(/\s*\n\s*/g, ' ');
  const i = t.indexOf('Hôm nay ·'); console.log(t.slice(i, i + 120));
  const n = await p.getByRole('button', {name: /Bắt đầu$/}).count();
  for (let k = 0; k < n; k++) {
    await p.goto('http://localhost:8599'); await p.waitForTimeout(5000);
    const bs = p.getByRole('button', {name: /Bắt đầu$/}); if (await bs.count() <= k) break;
    await bs.nth(k).click(); await p.waitForTimeout(3500);
    const e = await p.$$eval('[data-testid=stException]', e => e.map(x => x.innerText.slice(0, 300)));
    const s = (await p.innerText('body')).replace(/\s*\n\s*/g, ' '); const j = s.indexOf('←');
    console.log(' nút', k, e.length ? 'LỖI ' + e : 'ok', '|', s.slice(j, j + 90));
  }
  await b.close();
})();
