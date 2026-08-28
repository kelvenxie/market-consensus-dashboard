#!/bin/sh
set -eu

# 先完成正式 HTML 驗證與原子同步；任何失敗都不得提交舊檔。
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 "$SCRIPT_DIR/sync_dashboard.py"

cd "$SCRIPT_DIR"

# 尚未連接 GitHub 時安全停止，避免推送到錯誤位置。
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "❌ 尚未設定 GitHub origin，未提交也未推送。" >&2
  exit 2
fi

# Git 作者資料必須明確設定，不能用猜的。
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "❌ 尚未設定 Git user.name 或 user.email，未提交也未推送。" >&2
  exit 2
fi

git add -- index.html .nojekyll README.md sync_dashboard.py publish_to_github.sh .gitignore

if git diff --cached --quiet; then
  echo "✅ GitHub Pages 內容沒有變動，不需推送。"
  exit 0
fi

REPORT_DATE=$(date '+%Y-%m-%d')
git commit -m "Update market consensus dashboard ${REPORT_DATE}"
git push origin main
echo "✅ 已推送 GitHub Pages 更新。"

