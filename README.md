# 市場共識 GitHub Pages

這個資料夾是獨立的 Git Repository，只管理 GitHub Pages 公開內容，不納入父層的推文原始資料、判讀資料、價格快取、成本帳本或 API 狀態檔。

## 公開內容

- `index.html`：每日最新的市場共識儀表板。
- `.nojekyll`：要求 GitHub Pages 原樣發布靜態檔案。

## 每日同步

正式報告通過事實溯源、覆蓋率閘門及 HTML 驗證後，執行：

```bash
python3 sync_dashboard.py
```

同步程式只接受可解析、非空且未包含明顯本機路徑或憑證字串的 HTML，並以原子替換方式更新 `index.html`。

GitHub 遠端完成設定後，可執行：

```bash
./publish_to_github.sh
```

它會先重新驗證及同步，再提交有變動的 `index.html`，最後推送到 `origin/main`。如果沒有變動、沒有遠端或 Git 作者資料未設定，程式會安全停止。

## GitHub Pages 設定

1. 在 GitHub 建立專用 Repository。
2. 將本資料夾連接為 `origin`。
3. 推送 `main` 分支。
4. 在 GitHub Repository 的 `Settings → Pages`，將來源設為 `Deploy from a branch`、`main`、`/(root)`。

## 公開性提醒

GitHub Pages 網址屬於公開網站。不要將父層資料夾整體加入本 Repository，也不要在此放入 API Key、原始推文庫、Keychain 內容或個人資料。

