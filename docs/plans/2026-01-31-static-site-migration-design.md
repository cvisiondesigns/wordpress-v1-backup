# 靜態網站遷移設計：從 WordPress 到 Astro

**日期：** 2026-01-31
**狀態：** 草稿

## 1. 執行摘要 (Executive Summary)
本計畫的目標是將現有的「WordPress 靜態匯出」網站現代化，遷移至使用 **Astro** 與 **Tailwind CSS** 的乾淨架構。新網站將建立在獨立的隔離目錄中，以避免與舊檔案衝突。視覺設計將會 1:1 復刻，保持與目前網站完全一致。

## 2. 技術堆疊 (Technical Stack)
- **框架：** [Astro](https://astro.build/) (v5.x)
  - 選擇與理由：預設零 JavaScript (Zero-JS-by-default)，HTML 優先，極度適合內容型網站，效能極佳。
- **樣式：** [Tailwind CSS](https://tailwindcss.com/)
  - 選擇與理由：易於長期維護，Utility-first 的開發模式能快速建立與統一 UI。
- **內容管理：** Markdown / MDX / Content Collections
- **隔離策略：** 專案將位於當前 Repo 下的子目錄（例如 `astro-rebuild/`）。

## 3. 架構與組件 (Architecture & Components)

### 3.1 目錄結構
我們將建立一個全新的獨立專案資料夾：
```text
repo-root/
├── ... (舊檔案，如 wp-content/, index.html)
└── astro-rebuild/       <-- 新專案根目錄
    ├── src/
    │   ├── components/  <-- 可重複使用的 UI (Header, Footer, Card)
    │   ├── layouts/     <-- 頁面佈局 (BaseLayout)
    │   ├── pages/       <-- 路由 (index.astro, about.astro)
    │   └── styles/      <-- 全域樣式 (fonts, resets)
    ├── public/          <-- 靜態資源 (從舊網站複製過來的圖片)
    └── astro.config.mjs
```

### 3.2 關鍵組件
我們將把目前單一大檔的 HTML 拆解為組件：
- **MainLayout.astro**：包含 `<head>`、SEO meta標籤、全域 CSS 引入。
- **Header.astro**：導覽選單。
- **Footer.astro**：版權宣告與網站連結。
- **Content Blocks**：若有重複出現的區塊（如「服務項目」、「作品集網格」），將提取為獨立組件。

## 4. 遷移策略 (Migration Strategy)

### 第一階段：環境建置與樣式逆向工程
1. 在 `astro-rebuild/` 初始化純淨的 Astro 專案。
2. 安裝與設定 Tailwind CSS。
3. 分析現有的 `style.css`（及行內樣式），提取出：
   - 色票 (Color Palette)：如主色藍 `#4275f4`、文字灰 `#545353` 等。
   - 排版 (Typography)：系統字體 vs 指定字體 (如 Verdana)。
   - 間距與斷點 (Breakpoints/Spacing)。
4. 將上述參數設定至 `tailwind.config.mjs`。

### 第二階段：核心結構 (Skeleton)
1. 建立 `MainLayout.astro`，複製現有的 `<head>` 設定。
2. 使用 Tailwind 建立 `Header` 與 `Footer` 組件，確保像素級還原 (Pixel-perfect)。
3. 驗證響應式設計 (RWD)，確保手機/桌機版面與原站一致。

### 第三階段：首頁遷移
1. 將 `index.html` 的 `<body>` 內容移植到 `pages/index.astro`。
2. 將 `wp-content` 的圖片路徑替換為指向 `public/` 的新路徑。
3. 重構 HTML class，轉為 Tailwind utility classes。
   - *範例：* 將 `.header_wrapper` 改寫為 `<header class="w-full flex justify-between...">`

## 5. 風險與緩解 (Risks & Mitigation)
- **風險：** 更新路徑時遺漏圖片或資源。
  - *緩解：* 初期先將所有 `wp-content/uploads` 批量複製到 `astro-rebuild/public/uploads`，確保連結有效。
- **風險：** 設計與原站有落差。
  - *緩解：* 開發過程中使用「截圖對照」或瀏覽器分割視窗進行左右比對。
