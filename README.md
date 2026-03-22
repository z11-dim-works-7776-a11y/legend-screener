# 📊 Legend Screener

15大投資家によるマルチスクリーニングツール

## ファイル構成

| ファイル | 説明 |
|---|---|
| `legend_data.py` | スクリーニングスクリプト |
| `legend_dashboard.html` | ダッシュボード |
| `legend_result.json` | 最新スキャン結果（自動更新） |
| `legend_history.json` | スキャン履歴（自動蓄積） |
| `requirements.txt` | Pythonパッケージ一覧 |
| `.github/workflows/daily_scan.yml` | 毎朝自動実行設定 |

## 使い方

### ローカルで見る
1. `server.bat` をダブルクリック
2. ブラウザで `http://localhost:8000/legend_dashboard.html` を開く

### 手動でスキャン
```
py legend_data.py
```

### 自動スキャン
GitHub Actionsが毎朝7時（日本時間）に自動実行します。

## 投資家一覧
🏦 バフェット / 📈 リンチ / 📚 グレアム / 🧮 グリーンブラット / 🚀 オニール
⚖️ ダリオ / 🔄 ドレマン / 💰 ネフ / 📉 フィッシャー / 🤖 サイモンズ
🎯 テスタ / 🎁 桐谷広人 / 🌱 藤野英人 / 🏯 奥野一成 / 🎭 井村俊哉

## 免責事項
このツールは学習・研究目的です。投資はあくまで自己責任でお願いします。
