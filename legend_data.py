# ============================================================
# 10大投資家 スクリーニング データ生成スクリプト
# 実行すると legend_result.json が生成されます
# その後 legend_dashboard.html をブラウザで開いてください
#
# 【実行方法】
#   py legend_data.py
# ============================================================

import yfinance as yf
import pandas as pd
import json, os, time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------
# ★ 設定エリア
# ------------------------------------------------------------
TOP_N        = 10   # 各投資家の上位表示件数

# 対象銘柄リスト（S&P500全銘柄 + 日本株主要銘柄）
# ※ 日本株はyfinanceのティッカー形式（証券コード.T）で指定
UNIVERSE = [
    # ===== S&P500 米国株 =====
    # テクノロジー
    'AAPL','MSFT','NVDA','GOOGL','GOOG','META','AMZN','TSLA','AMD','INTC',
    'CSCO','ORCL','IBM','ADBE','CRM','NOW','INTU','QCOM','TXN','AMAT',
    'LRCX','KLAC','SNPS','CDNS','PANW','FTNT','NFLX','PYPL','ADSK','DDOG',
    'CRWD','WDAY','SNOW','TEAM','ZS','OKTA','NET','PLTR','MDB','TTD',
    'CTSH','GDDY','HUBS','EPAM','ON','MPWR','ENPH','FSLR','ROP',
    # 金融
    'BRK-B','JPM','BAC','WFC','GS','MS','AXP','V','MA','BLK',
    'SPGI','MCO','ICE','CME','CB','AIG','MET','PRU','AFL','ALL',
    'TRV','PGR','COF','AMP','TROW','NDAQ','RJF','SYF','AJG',
    'AON','WTW','USB','PNC','TFC','MTB','RF','HBAN','FITB',
    'STT','BK','NTRS','CFG','KEY','CMA','ZION','WAL',
    # ヘルスケア
    'JNJ','LLY','ABBV','MRK','PFE','ABT','TMO','DHR','MDT','SYK',
    'BSX','ISRG','REGN','AMGN','GILD','VRTX','BMY','CVS','UNH','HUM',
    'CI','ELV','HCA','IDXX','IQV','RMD','STE','ZBH','ZTS','EW',
    'HOLX','PODD','DXCM','MTD','WST','TECH','TFX','RVTY',
    # 生活必需品
    'PG','KO','PEP','WMT','COST','HD','LOW','TGT','SBUX','MCD',
    'YUM','CMG','DG','DLTR','CL','KMB','GIS','MKC','CLX',
    'CAG','HRL','TSN','MDLZ','MO','PM','STZ','TAP','CPB','SJM',
'KR','SYY','ADM','BG','INGR','CALM','CHEF','USFD','PFGC',
    # 資本財
    'CAT','DE','HON','MMM','GE','ETN','EMR','ITW','PH','ROK',
    'CMI','GD','LMT','RTX','NOC','BA','UPS','FDX','NSC','CSX',
    'UNP','FAST','GWW','HUBB','IEX','SWK','AME','CARR','TT','PCAR',
    'WAB','EXPD','JBHT','ODFL','XPO','SAIA','CHRW','GXO','LDOS','LHX',
    'TDY','GNRC','AOS','AYI','WSO','NDSN','IR','OTIS','ALLE','JCI',
    # エネルギー
    'XOM','CVX','COP','EOG','SLB','MPC','VLO','PSX','OXY','HAL',
    'DVN','FANG','APA','BKR','NOV','KMI','OKE','WMB',
    'LNG','TRGP','ET','MPLX','AM','DT','HESM','CTRA','SM','MTDR',
    # 通信・メディア
    'VZ','T','TMUS','CMCSA','DIS','CHTR','NWSA','NWS','WBD',
    'FOX','FOXA','LUMN','SIRI','TTWO','EA','MTCH','ZM','SNAP','PINS',
    # 素材
    'LIN','APD','ECL','NEM','FCX','NUE','VMC','MLM','ALB','CF',
    'MOS','FMC','IFF','PPG','SHW','RPM','SEE','SON','PKG','IP',
    'AVY','BALL','CCK','OLN','CE','EMN','HUN','LYB','DD',
    # 不動産・公益
    'AMT','EQIX','PLD','CCI','PSA','NEE','DUK','SO','D','AEP',
    'EXC','XEL','ES','ETR','FE','PPL','AEE','WEC','CNP','NI',
    'ARE','AVB','CPT','EQR','ESS','MAA','UDR','INVH','VICI','GLPI',
    'SPG','O','REG','KIM','BXP','WELL','VTR','DOC','HR',
    # 小売・消費者
    'BKNG','ABNB','EXPE','ETSY','EBAY','W','RH','BBY','DKS','ROST',
    'TJX','BURL','ULTA','SIG','NKE','LULU','PVH','RL','TPR','VFC',
    # 成長・その他
    'UBER','LYFT','COIN','HOOD','SOFI','AFRM','AXON','CELH','RBLX','DKNG',
    'BX','KKR','APO','ARES','TPG','CG','BAM','MSCI','VRSK','FICO',
    'SPGI','EFX','TRI','CSGP','AME','ROP','HUBB',

    # ===== 日本株主要銘柄（.T = 東証） =====
    # 超大型・時価総額上位
    '7203.T',  # トヨタ自動車
    '6758.T',  # ソニーグループ
    '8306.T',  # 三菱UFJフィナンシャル
    '9984.T',  # ソフトバンクグループ
    '6861.T',  # キーエンス
    '7974.T',  # 任天堂
    '4063.T',  # 信越化学工業
    '8035.T',  # 東京エレクトロン
    '6098.T',  # リクルートHD
    '9432.T',  # NTT
    # 製造・素材
    '6501.T',  # 日立製作所
    '6702.T',  # 富士通
    '6723.T',  # ルネサスエレクトロニクス
    '6971.T',  # 京セラ
    '6981.T',  # 村田製作所
    '4568.T',  # 第一三共
    '4519.T',  # 中外製薬
    '4502.T',  # 武田薬品工業
    '5401.T',  # 日本製鉄
    '7011.T',  # 三菱重工業
    # 金融
    '8316.T',  # 三井住友フィナンシャル
    '8411.T',  # みずほフィナンシャル
    '8591.T',  # オリックス
    '8766.T',  # 東京海上HD
    '7182.T',  # ゆうちょ銀行
    # 消費・サービス
    '9983.T',  # ファーストリテイリング（ユニクロ）
    '2914.T',  # JT（日本たばこ産業）
    '3382.T',  # セブン＆アイHD
    '8267.T',  # イオン
    '9433.T',  # KDDI
    '9434.T',  # ソフトバンク（通信）
    '4755.T',  # 楽天グループ
    '2413.T',  # エムスリー
    '6367.T',  # ダイキン工業
    '7751.T',  # キヤノン
    # 成長・新興
    '4478.T',  # フリー
    '3659.T',  # ネクソン
    '9697.T',  # カプコン
    '2432.T',  # DeNA
    '3765.T',  # ガンホー
    '4385.T',  # メルカリ
    '3092.T',  # ZOZO
    '9020.T',  # JR東日本
    '9022.T',  # JR東海
    '9101.T',  # 日本郵船
]

# ------------------------------------------------------------
# 日本株 日本語名マップ
# ------------------------------------------------------------
JP_NAMES = {
    '7203.T': 'トヨタ自動車',
    '6758.T': 'ソニーグループ',
    '8306.T': '三菱UFJフィナンシャル',
    '9984.T': 'ソフトバンクグループ',
    '6861.T': 'キーエンス',
    '7974.T': '任天堂',
    '4063.T': '信越化学工業',
    '8035.T': '東京エレクトロン',
    '6098.T': 'リクルートHD',
    '9432.T': 'NTT',
    '6501.T': '日立製作所',
    '6702.T': '富士通',
    '6723.T': 'ルネサスエレクトロニクス',
    '6971.T': '京セラ',
    '6981.T': '村田製作所',
    '4568.T': '第一三共',
    '4519.T': '中外製薬',
    '4502.T': '武田薬品工業',
    '5401.T': '日本製鉄',
    '7011.T': '三菱重工業',
    '8316.T': '三井住友フィナンシャル',
    '8411.T': 'みずほフィナンシャル',
    '8591.T': 'オリックス',
    '8766.T': '東京海上HD',
    '7182.T': 'ゆうちょ銀行',
    '9983.T': 'ファーストリテイリング',
    '2914.T': 'JT（日本たばこ産業）',
    '3382.T': 'セブン＆アイHD',
    '8267.T': 'イオン',
    '9433.T': 'KDDI',
    '9434.T': 'ソフトバンク',
    '4755.T': '楽天グループ',
    '2413.T': 'エムスリー',
    '6367.T': 'ダイキン工業',
    '7751.T': 'キヤノン',
    '4478.T': 'フリー',
    '3659.T': 'ネクソン',
    '9697.T': 'カプコン',
    '2432.T': 'DeNA',
    '3765.T': 'ガンホー',
    '4385.T': 'メルカリ',
    '3092.T': 'ZOZO',
    '9020.T': 'JR東日本',
    '9022.T': 'JR東海',
    '9101.T': '日本郵船',
}

# 米国株 日本語名マップ（主要銘柄）
US_NAMES = {
    # テクノロジー
    'AAPL':  'アップル',
    'MSFT':  'マイクロソフト',
    'NVDA':  'エヌビディア',
    'GOOGL': 'アルファベット(Google)',
    'GOOG':  'アルファベット(Google)',
    'META':  'メタ・プラットフォームズ',
    'AMZN':  'アマゾン',
    'TSLA':  'テスラ',
    'AMD':   'AMD',
    'INTC':  'インテル',
    'CSCO':  'シスコシステムズ',
    'ORCL':  'オラクル',
    'IBM':   'IBM',
    'ADBE':  'アドビ',
    'CRM':   'セールスフォース',
    'NOW':   'サービスナウ',
    'INTU':  'イントゥイット',
    'QCOM':  'クアルコム',
    'TXN':   'テキサス・インスツルメンツ',
    'AMAT':  'アプライドマテリアルズ',
    'LRCX':  'ラムリサーチ',
    'KLAC':  'KLAコーポレーション',
    'SNPS':  'シノプシス',
    'CDNS':  'ケイデンス・デザイン',
    'PANW':  'パロアルトネットワークス',
    'FTNT':  'フォーティネット',
    'NFLX':  'ネットフリックス',
    'PYPL':  'ペイパル',
    'ADSK':  'オートデスク',
    'DDOG':  'データドッグ',
    'CRWD':  'クラウドストライク',
    'WDAY':  'ワークデイ',
    'SNOW':  'スノーフレーク',
    'TEAM':  'アトラシアン',
    'NET':   'クラウドフレア',
    'PLTR':  'パランティア',
    # 金融
    'BRK-B': 'バークシャー・ハサウェイ',
    'JPM':   'JPモルガン・チェース',
    'BAC':   'バンク・オブ・アメリカ',
    'WFC':   'ウェルズ・ファーゴ',
    'GS':    'ゴールドマン・サックス',
    'MS':    'モルガン・スタンレー',
    'AXP':   'アメリカン・エキスプレス',
    'V':     'ビザ',
    'MA':    'マスターカード',
    'BLK':   'ブラックロック',
    'SPGI':  'S&Pグローバル',
    'MCO':   'ムーディーズ',
    'ICE':   'インターコンチネンタル取引所',
    'CME':   'CMEグループ',
    'CB':    'チャブ',
    'AIG':   'AIG',
    'MET':   'メットライフ',
    'PRU':   'プルデンシャル',
    'AFL':   'アフラック',
    'ALL':   'オールステート',
    'TRV':   'トラベラーズ',
    'PGR':   'プログレッシブ',
    'COF':   'キャピタル・ワン',
    'AMP':   'アメリプライズ',
    'TROW':  'Tロウ・プライス',
    'NDAQ':  'ナスダック',
    'RJF':   'レイモンド・ジェームズ',
    # ヘルスケア
    'JNJ':   'ジョンソン＆ジョンソン',
    'LLY':   'イーライリリー',
    'ABBV':  'アッヴィ',
    'MRK':   'メルク',
    'PFE':   'ファイザー',
    'ABT':   'アボット',
    'TMO':   'サーモフィッシャー',
    'DHR':   'ダナハー',
    'MDT':   'メドトロニック',
    'SYK':   'ストライカー',
    'BSX':   'ボストン・サイエンティフィック',
    'ISRG':  'インテュイティブ・サージカル',
    'REGN':  'リジェネロン',
    'AMGN':  'アムジェン',
    'GILD':  'ギリアド・サイエンシズ',
    'VRTX':  'バーテックス・ファーマ',
    'BMY':   'ブリストル・マイヤーズ',
    'CVS':   'CVSヘルス',
    'UNH':   'ユナイテッドヘルス',
    'HUM':   'ヒューマナ',
    'CI':    'シグナ',
    'ELV':   'エレバンス・ヘルス',
    # 生活必需品
    'PG':    'P&G',
    'KO':    'コカ・コーラ',
    'PEP':   'ペプシコ',
    'WMT':   'ウォルマート',
    'COST':  'コストコ',
    'HD':    'ホーム・デポ',
    'LOW':   'ロウズ',
    'TGT':   'ターゲット',
    'SBUX':  'スターバックス',
    'MCD':   'マクドナルド',
    'YUM':   'ヤム・ブランズ',
    'CMG':   'チポトレ',
    'DG':    'ダラー・ゼネラル',
    'DLTR':  'ダラー・ツリー',
    'CL':    'コルゲート',
    'KMB':   'キンバリークラーク',
    'GIS':   'ゼネラル・ミルズ',
    'MKC':   'マコーミック',
    'MO':    'アルトリア',
    'PM':    'フィリップ・モリス',
    # 資本財
    'CAT':   'キャタピラー',
    'DE':    'ジョン・ディア',
    'HON':   'ハネウェル',
    'MMM':   'スリーエム',
    'GE':    'GEエアロスペース',
    'ETN':   'イートン',
    'EMR':   'エマソン・エレクトリック',
    'ITW':   'イリノイ・ツール・ワークス',
    'PH':    'パーカー・ハネフィン',
    'ROK':   'ロックウェル・オートメーション',
    'GD':    'ゼネラル・ダイナミクス',
    'LMT':   'ロッキード・マーティン',
    'RTX':   'RTXコーポレーション',
    'NOC':   'ノースロップ・グラマン',
    'BA':    'ボーイング',
    'UPS':   'UPS',
    'FDX':   'フェデックス',
    'NSC':   'ノーフォーク・サザン',
    'CSX':   'CSXコーポレーション',
    'UNP':   'ユニオン・パシフィック',
    # エネルギー
    'XOM':   'エクソンモービル',
    'CVX':   'シェブロン',
    'COP':   'コノコフィリップス',
    'EOG':   'EOGリソーシズ',
    'SLB':   'シュルンベルジェ',
    'MPC':   'マラソン・ペトロリアム',
    'VLO':   'バレロ・エナジー',
    'PSX':   'フィリップス66',
    'OXY':   'オクシデンタル・ペトロリアム',
    'HAL':   'ハリバートン',
    # 通信
    'VZ':    'ベライゾン',
    'T':     'AT&T',
    'TMUS':  'Tモバイル',
    'CMCSA': 'コムキャスト',
    'DIS':   'ウォルト・ディズニー',
    'CHTR':  'チャーター・コミュニケーションズ',
    # 素材
    'LIN':   'リンデ',
    'APD':   'エア・プロダクツ',
    'ECL':   'エコラボ',
    'NEM':   'ニューモント',
    'FCX':   'フリーポート・マクモラン',
    'NUE':   'ニューコア',
    # 不動産・公益
    'AMT':   'アメリカン・タワー',
    'EQIX':  'エクイニクス',
    'PLD':   'プロロジス',
    'CCI':   'クラウン・キャッスル',
    'PSA':   'パブリック・ストレージ',
    'NEE':   'ネクステラ・エナジー',
    'DUK':   'デューク・エナジー',
    'SO':    'サザン・カンパニー',
    # 成長・その他
    'UBER':  'ウーバー',
    'AXON':  'アクソン・エンタープライズ',
    'CELH':  'セルシウス・ホールディングス',
    'ENPH':  'エンフェーズ・エナジー',
    'FSLR':  'ファースト・ソーラー',
    'BX':    'ブラックストーン',
    'KKR':   'KKR',
    'MSCI':  'MSCIインク',
    'VRSK':  'バリスク・アナリティクス',
    'FICO':  'フェア・アイザック',
    # 追加銘柄
    'TTD':   'ザ・トレード・デスク',
    'CTSH':  'コグニザント・テクノロジー',
    'MDB':   'モンゴDB',
    'NET':   'クラウドフレア',
    'DDOG':  'データドッグ',
    'CRWD':  'クラウドストライク',
    'SNOW':  'スノーフレーク',
    'WDAY':  'ワークデイ',
    'ZS':    'ジースケーラー',
    'OKTA':  'オクタ',
    'PLTR':  'パランティア',
    'TEAM':  'アトラシアン',
    'GDDY':  'ゴーダディ',
    'HUBS':  'ハブスポット',
    'EPAM':  'EPAMシステムズ',
    'ON':    'ONセミコンダクター',
    'MPWR':  'モノリシックパワー',
    'SYF':   'シンクロニー・ファイナンシャル',
    'DFS':   'ディスカバー・ファイナンシャル',
    'AJG':   'アーサー・J・ギャラガー',
    'MMC':   'マーシュ＆マクレナン',
    'AON':   'エーオン',
    'WTW':   'ウィリス・タワーズワトソン',
    'USB':   'USバンコープ',
    'PNC':   'PNCファイナンシャル',
    'TFC':   'トルーイスト・ファイナンシャル',
    'MTB':   'M&Tバンク',
    'RF':    'リージョンズ・ファイナンシャル',
    'HBAN':  'ハンティントン・バンクシェアーズ',
    'FITB':  'フィフス・サード・バンコープ',
    'STT':   'ステート・ストリート',
    'BK':    'バンク・オブ・ニューヨーク・メロン',
    'NTRS':  'ノーザン・トラスト',
    'CFG':   'シティズンズ・ファイナンシャル',
    'KEY':   'キーコープ',
    'CMA':   'コメリカ',
    'ZION':  'ザイオンズ・バンコーポレーション',
    'HCA':   'HCAヘルスケア',
    'IDXX':  'アイデックス・ラボラトリーズ',
    'IQV':   'IQVIA',
    'RMD':   'レスメド',
    'STE':   'ステリス',
    'ZBH':   'ジンマー・バイオメット',
    'EW':    'エドワーズ・ライフサイエンシズ',
    'HOLX':  'ホロジック',
    'PODD':  'インスレット',
    'DXCM':  'デクスコム',
    'MTD':   'メトラー・トレド',
    'WST':   'ウェスト・ファーマシューティカル',
    'RVTY':  'レブビティ',
    'STZ':   'コンステレーション・ブランズ',
    'TAP':   'モルソン・クアーズ',
    'CPB':   'キャンベル・スープ',
    'SJM':   'JMスマッカー',
    'KR':    'クローガー',
    'SYY':   'シスコ（食品）',
    'ADM':   'アーチャー・ダニエルズ・ミッドランド',
    'BG':    'バンジ・グローバル',
    'INGR':  'インググリーディエンツ',
    'CALM':  'カル・メイン・フーズ',
    'USFD':  'USフーズ',
    'PFGC':  'パフォーマンス・フード・グループ',
    'PCAR':  'パッカー',
    'WAB':   'ウェスティングハウス・エア・ブレーキ',
    'EXPD':  'エクスペダイターズ',
    'JBHT':  'JBハント・トランスポート',
    'ODFL':  'オールド・ドミニオン・フレイト',
    'XPO':   'XPOロジスティクス',
    'SAIA':  'サイア',
    'CHRW':  'CH・ロビンソン',
    'GXO':   'GXOロジスティクス',
    'LDOS':  'ライドス',
    'LHX':   'L3ハリス・テクノロジーズ',
    'TDY':   'テレダイン・テクノロジーズ',
    'GNRC':  'ジェネラック',
    'AOS':   'Aオースミス',
    'AYI':   'アクイティ・ブランズ',
    'WSO':   'ウォルシュ・エア・コンディショニング',
    'NDSN':  'ノードソン',
    'OTIS':  'オーチス・ワールドワイド',
    'ALLE':  'アレグリオン',
    'JCI':   'ジョンソン・コントロールズ',
    'DVN':   'デボン・エナジー',
    'FANG':  'ダイアモンドバック・エナジー',
    'MRO':   'マラソン・オイル',
    'APA':   'APA コーポレーション',
    'BKR':   'ベーカー・ヒューズ',
    'NOV':   'NOV',
    'KMI':   'キンダー・モルガン',
    'OKE':   'ワンオーク',
    'WMB':   'ウィリアムズ・カンパニーズ',
    'LNG':   'シェニエール・エナジー',
    'TRGP':  'ターガ・リソーシズ',
    'NWSA':  'ニューズ・コーポレーション',
    'WBD':   'ワーナー・ブラザース・ディスカバリー',
    'LUMN':  'ルーメン・テクノロジーズ',
    'SIRI':  'シリウスXM',
    'TTWO':  'テイクツー・インタラクティブ',
    'MTCH':  'マッチ・グループ',
    'VMC':   'バルカン・マテリアルズ',
    'MLM':   'マーティン・マリエッタ',
    'ALB':   'アルベマール',
    'MOS':   'モザイク',
    'IFF':   'インターナショナル・フレーバーズ',
    'SEE':   'シールド・エア',
    'PKG':   'パッケージング・コーポレーション',
    'WRK':   'ウェストロック',
    'AVY':   'エイベリー・デニソン',
    'CCK':   'クラウン・ホールディングス',
    'OLN':   'オリン',
    'EMN':   'イーストマン・ケミカル',
    'HUN':   'ハンツマン',
    'LYB':   'ライオンデルバゼル',
    'ARE':   'アレクサンドリア不動産',
    'AVB':   'アバロンベイ・コミュニティーズ',
    'CPT':   'カムデン・プロパティ',
    'EQR':   'エクイティ・レジデンシャル',
    'ESS':   'エセックス・プロパティ',
    'MAA':   'ミッドアメリカ・アパートメント',
    'UDR':   'UDRインク',
    'INVH':  'インビテーション・ホームズ',
    'VICI':  'ビシ・プロパティーズ',
    'GLPI':  'ゲーミング＆レジャー・プロパティーズ',
    'REG':   'レゲンシー・センターズ',
    'KIM':   'キムコ・リアルティ',
    'BXP':   'ボストン・プロパティーズ',
    'WELL':  'ウェルタワー',
    'VTR':   'ベンタス',
    'BKNG':  'ブッキング・ホールディングス',
    'ABNB':  'エアビーアンドビー',
    'EXPE':  'エクスペディア',
    'ETSY':  'エッツィー',
    'RH':    'RH（レストレーションハードウェア）',
    'BBY':   'ベスト・バイ',
    'DKS':   'ディックス・スポーティング・グッズ',
    'ROST':  'ロス・ストアーズ',
    'TJX':   'TJXカンパニーズ',
    'BURL':  'バーリントン・ストアーズ',
    'ULTA':  'ウルタ・ビューティー',
    'SIG':   'シグネット・ジュエラーズ',
    'LULU':  'ルルレモン',
    'PVH':   'PVHコープ',
    'TPR':   'タペストリー',
    'VFC':   'VFコーポレーション',
    'LYFT':  'リフト',
    'COIN':  'コインベース',
    'HOOD':  'ロビンフッド',
    'SOFI':  'ソーファイ・テクノロジーズ',
    'AFRM':  'アファーム',
    'RBLX':  'ロブロックス',
    'DKNG':  'ドラフトキングス',
    'APO':   'アポロ・グローバル・マネジメント',
    'ARES':  'アレス・マネジメント',
    'TPG':   'TPGインク',
    'CG':    'カーライル・グループ',
    'BAM':   'ブルックフィールド・アセット・マネジメント',
    'EFX':   'エクイファックス',
    'TRI':   'トムソン・ロイター',
    'CSGP':  'コスター・グループ',
    'ROP':   'ローパー・テクノロジーズ',
    'IEX':   'IDEXコーポレーション',
    'SWK':   'スタンレー・ブラック＆デッカー',
    'CARR':  'キャリア・グローバル',
    'IR':    'インガーソル・ランド',
    'FAST':  'ファスナル',
    'GWW':   'グレンジャー',
    'AMP':   'アメリプライズ・ファイナンシャル',
    'SPG':   'サイモン・プロパティ・グループ',
    'O':     'リアルティ・インカム',
    'NEM':   'ニューモント',
    'DD':    'デュポン',
    'IP':    'インターナショナル・ペーパー',
    'SON':   'ソノコ・プロダクツ',
    'RPM':   'RPMインターナショナル',
    'PPG':   'PPGインダストリーズ',
    'FMC':   'FMCコーポレーション',
    'CF':    'CFインダストリーズ',
    'PPL':   'PPLコーポレーション',
    'AEE':   'アメレン',
    'WEC':   'WECエナジー',
    'CNP':   'センターポイント・エナジー',
    'NI':    'ナイソース',
    'ETR':   'エンタジー',
    'FE':    'ファーストエナジー',
    'XEL':   'エクセル・エナジー',
    'ES':    'エバーソース・エナジー',
    'AEP':   'アメリカン・エレクトリック・パワー',
    'EXC':   'エクセロン',
    'DUK':   'デューク・エナジー',
    'D':     'ドミニオン・エナジー',
    'PEAK':  'ヘルスピーク・プロパティーズ',
    'DOC':   'ドクターズ・リアルティ',
    'HR':    'ヘルスケアREIT',
    'AM':    'アンテロ・ミッドストリーム',
    'DT':    'ダイナトレース',
    'HESM':  'HESミッドストリーム',
    'CTRA':  'コテラ・エナジー',
    'SM':    'SM エナジー',
    'MTDR':  'マタドール・リソーシズ',
    'MPLX':  'MPLXリミテッド',
    'ET':    'エナジー・トランスファー',
    'FOXA':  'フォックス・コーポレーション',
    'FOX':   'フォックス・コーポレーション',
    'ZM':    'ズーム・ビデオ',
    'SNAP':  'スナップ',
    'W':     'ウェイフェア',
    'RL':    'ラルフ・ローレン',
}

# ------------------------------------------------------------
# 財務データ取得
# ------------------------------------------------------------

def parse_info(ticker, info):
    """infoオブジェクトから財務データを抽出（まとめ取得・個別取得共用）"""
    try:
        price     = info.get('currentPrice') or info.get('regularMarketPrice')
        eps       = info.get('trailingEps')
        w52high   = info.get('fiftyTwoWeekHigh')
        market_cap= info.get('marketCap')
        div_yield = info.get('dividendYield')
        psr       = info.get('priceToSalesTrailing12Months')
        pbr       = info.get('priceToBook')
        peg       = info.get('pegRatio')
        current_r = info.get('currentRatio')

        roe        = info.get('returnOnEquity')
        op_margin  = info.get('operatingMargins')
        debt_eq    = info.get('debtToEquity')
        fcf        = info.get('freeCashflow')
        eps_growth = info.get('earningsGrowth')
        rev_growth = info.get('revenueGrowth')

        # トレンド指標
        w52low      = info.get('fiftyTwoWeekLow')
        price_50ma  = info.get('fiftyDayAverage')
        price_200ma = info.get('twoHundredDayAverage')

        # 52週トレンド：50日MA > 200日MA かつ現在値が50日MAより上
        trend_52w = bool(
            price and price_50ma and price_200ma and
            price_50ma > price_200ma and price > price_50ma
        )
        w52_pos = round((price - w52low) / (w52high - w52low), 3)                   if price and w52high and w52low and w52high > w52low else None

        trend_eps = bool(eps_growth and eps_growth > 0)
        trend_rev = bool(rev_growth and rev_growth > 0)
        tscore    = sum([trend_52w, trend_eps, trend_rev])
        tlabel    = ['↓ 要注意','→ 一部改善','→ 概ね改善','↑ 全指標改善中'][tscore]

        # 日本語名の決定
        long_name = info.get('longName', '') or info.get('shortName', ticker)
        display_name = JP_NAMES.get(ticker, US_NAMES.get(ticker, long_name))

        if not price:
            return None

        return {
            'ticker':       ticker,
            'name':         display_name,
            'shortName':    info.get('shortName', ticker),
            'sector':       info.get('sector', '—'),
            'price':        round(price, 2)           if price       else None,
            'marketCap':    market_cap,
            'ROE':          round(roe * 100, 2)       if roe         else None,
            'opMargin':     round(op_margin * 100, 2) if op_margin   else None,
            'debtRatio':    round(debt_eq / 100, 3)   if debt_eq     else None,
            'FCF':          round(fcf / 1e8, 2)       if fcf         else None,
            'PER':          round(price / eps, 2)     if price and eps and eps > 0 else None,
            'PBR':          round(pbr, 2)             if pbr         else None,
            'PEG':          round(peg, 2)             if peg         else None,
            'PSR':          round(psr, 2)             if psr         else None,
            'epsGrowth':    round(eps_growth * 100, 2)if eps_growth  else None,
            'revGrowth':    round(rev_growth * 100, 2)if rev_growth  else None,
            'currentRatio': round(current_r, 2)       if current_r   else None,
            'divYield':     round(div_yield * 100, 2) if div_yield   else None,
            'w52Ratio':     round(price / w52high, 3) if price and w52high and w52high > 0 else None,
            'w52Position':  w52_pos,
            'price50ma':    round(price_50ma, 2)      if price_50ma  else None,
            'price200ma':   round(price_200ma, 2)     if price_200ma else None,
            'trend52w':     trend_52w,
            'trendEps':     trend_eps,
            'trendRev':     trend_rev,
            'trendScore':   tscore,
            'trendLabel':   tlabel,
        }
    except Exception:
        return None


def get_data(ticker, retries=2):
    """個別取得（フォールバック用）- リトライ付き"""
    for attempt in range(retries + 1):
        try:
            stock = yf.Ticker(ticker)
            info  = stock.info
            # Yahoo落ち検知: infoが空またはquoteTypeがNONEの場合
            if not info or info.get('quoteType') == 'NONE' or not info.get('regularMarketPrice') and not info.get('currentPrice'):
                if attempt < retries:
                    time.sleep(1.0 * (attempt + 1))  # 1秒, 2秒と待機
                    continue
                return None
            return parse_info(ticker, info)
        except Exception as e:
            err = str(e)
            if '429' in err or 'Too Many Requests' in err:
                # レート制限: 長めに待つ
                wait = 30 * (attempt + 1)
                print(f'\n  ⚠ レート制限({ticker}) {wait}秒待機...', end=' ')
                time.sleep(wait)
            elif attempt < retries:
                time.sleep(1.0 * (attempt + 1))
            else:
                return None
    return None


def screen_buffett(d):
    s, c = 0, {}
    c['roe']  = d['ROE']      is not None and d['ROE']      >= 20;  s += 3 if c['roe']  else 0
    c['om']   = d['opMargin'] is not None and d['opMargin'] >= 20;  s += 3 if c['om']   else 0
    c['debt'] = d['debtRatio']is not None and d['debtRatio']<= 0.5; s += 2 if c['debt'] else 0
    c['fcf']  = d['FCF']      is not None and d['FCF']       > 0;   s += 1 if c['fcf']  else 0
    c['per']  = d['PER']      is not None and d['PER']       <= 30; s += 1 if c['per']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'roe':'ROE≥20% (3点)','om':'営業利益率≥20% (3点)','debt':'負債比率≤0.5 (2点)','fcf':'FCFプラス (1点)','per':'PER≤30 (1点)'}}

def screen_lynch(d):
    s, c = 0, {}
    c['peg'] = d['PEG'] is not None and 0 < d['PEG'] < 1.0;        s += 4 if c['peg'] else 0
    c['cap'] = d['marketCap'] is not None and 3e8 <= d['marketCap'] <= 1e10; s += 2 if c['cap'] else 0
    c['eps'] = d['epsGrowth'] is not None and d['epsGrowth'] > 0;   s += 3 if c['eps'] else 0
    c['per'] = d['PER']       is not None and d['PER'] <= 50;       s += 1 if c['per'] else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'peg':'PEG<1.0 (4点)','cap':'時価総額3億〜100億$ (2点)','eps':'EPS成長率プラス (3点)','per':'PER≤50 (1点)'}}

def screen_graham(d):
    s, c = 0, {}
    pp = d['PER'] * d['PBR'] if d['PER'] and d['PBR'] else None
    c['gn']   = pp is not None and pp <= 22.5;                      s += 4 if c['gn']   else 0
    c['cr']   = d['currentRatio'] is not None and d['currentRatio'] >= 2.0; s += 2 if c['cr'] else 0
    c['per']  = d['PER']  is not None and d['PER']  <= 15;         s += 2 if c['per']  else 0
    c['pbr']  = d['PBR']  is not None and d['PBR']  <= 1.5;        s += 1 if c['pbr']  else 0
    c['debt'] = d['debtRatio'] is not None and d['debtRatio'] <= 1.0; s += 1 if c['debt'] else 0
    return {'score': s, 'max': 10, 'checks': c, 'perPbr': round(pp, 2) if pp else None,
            'scoring': {'gn':'PER×PBR≤22.5 (4点)','cr':'流動比率≥200% (2点)','per':'PER≤15 (2点)','pbr':'PBR≤1.5 (1点)','debt':'負債比率≤1.0 (1点)'}}

def screen_greenblatt(d):
    s, c = 0, {}
    c['roic'] = d['ROE']      is not None and d['ROE']      >= 25;  s += 4 if c['roic'] else 0
    c['ey']   = d['opMargin'] is not None and d['opMargin'] >= 20;  s += 4 if c['ey']   else 0
    c['per']  = d['PER']      is not None and d['PER']      <= 30;  s += 1 if c['per']  else 0
    c['cap']  = d['marketCap']is not None and d['marketCap']>= 5e8; s += 1 if c['cap']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'roic':'ROE≥25% ROIC代替 (4点)','ey':'営業利益率≥20% 益回り代替 (4点)','per':'PER≤30 (1点)','cap':'時価総額≥5億$ (1点)'}}

def screen_oneil(d):
    s, c = 0, {}
    c['eps'] = d['epsGrowth'] is not None and d['epsGrowth'] >= 25; s += 4 if c['eps'] else 0
    c['w52'] = d['w52Ratio']  is not None and d['w52Ratio']  >= 0.85;s += 3 if c['w52'] else 0
    c['roe'] = d['ROE']       is not None and d['ROE']       >= 17;  s += 2 if c['roe'] else 0
    c['rev'] = d['revGrowth'] is not None and d['revGrowth'] >= 20;  s += 1 if c['rev'] else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'eps':'EPS成長率≥25% (4点)','w52':'52週高値85%以上 (3点)','roe':'ROE≥17% (2点)','rev':'売上成長≥20% (1点)'}}

def screen_dalio(d):
    s, c = 0, {}
    c['div']  = d['divYield'] is not None and d['divYield']  >= 2.5; s += 4 if c['div']  else 0
    c['debt'] = d['debtRatio']is not None and d['debtRatio'] <= 0.6; s += 3 if c['debt'] else 0
    c['om']   = d['opMargin'] is not None and d['opMargin']  >= 12;  s += 1 if c['om']   else 0
    c['pbr']  = d['PBR']      is not None and d['PBR']       <= 2.5; s += 1 if c['pbr']  else 0
    c['roe']  = d['ROE']      is not None and d['ROE']       >= 10;  s += 1 if c['roe']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'div':'配当利回り≥2.5% (4点)','debt':'負債比率≤0.6 (3点)','om':'営業利益率≥12% (1点)','pbr':'PBR≤2.5 (1点)','roe':'ROE≥10% (1点)'}}

def screen_dreman(d):
    s, c = 0, {}
    c['per']  = d['PER']      is not None and d['PER']       <= 10;  s += 4 if c['per']  else 0
    c['pbr']  = d['PBR']      is not None and d['PBR']       <= 1.0; s += 3 if c['pbr']  else 0
    c['div']  = d['divYield'] is not None and d['divYield']  >= 2;   s += 2 if c['div']  else 0
    c['debt'] = d['debtRatio']is not None and d['debtRatio'] <= 1.0; s += 1 if c['debt'] else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'per':'PER≤10 (4点)','pbr':'PBR≤1.0 (3点)','div':'配当利回り≥2% (2点)','debt':'負債比率≤1.0 (1点)'}}

def screen_neff(d):
    s, c = 0, {}
    c['per'] = d['PER']      is not None and d['PER']      <= 10;  s += 4 if c['per'] else 0
    c['div'] = d['divYield'] is not None and d['divYield'] >= 3;   s += 4 if c['div'] else 0
    c['eps'] = d['epsGrowth']is not None and d['epsGrowth']>= 7;   s += 1 if c['eps'] else 0
    c['om']  = d['opMargin'] is not None and d['opMargin'] >= 10;  s += 1 if c['om']  else 0
    neff_idx = round((d['epsGrowth'] + d['divYield']) / d['PER'], 2) \
               if d['epsGrowth'] and d['divYield'] and d['PER'] and d['PER'] > 0 else None
    return {'score': s, 'max': 10, 'checks': c, 'neffIdx': neff_idx,
            'scoring': {'per':'PER≤10 (4点)','div':'配当利回り≥3% (4点)','eps':'EPS成長率≥7% (1点)','om':'営業利益率≥10% (1点)'}}

def screen_fisher(d):
    s, c = 0, {}
    c['psr'] = d['PSR']       is not None and d['PSR']       <= 1.2; s += 4 if c['psr'] else 0
    c['cap'] = d['marketCap'] is not None and d['marketCap'] >= 5e9; s += 2 if c['cap'] else 0
    c['rev'] = d['revGrowth'] is not None and d['revGrowth'] >= 15;  s += 3 if c['rev'] else 0
    c['om']  = d['opMargin']  is not None and d['opMargin']  >= 10;  s += 1 if c['om']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'psr':'PSR≤1.2 (4点)','cap':'時価総額≥50億$ (2点)','rev':'売上成長≥15% (3点)','om':'営業利益率≥10% (1点)'}}

def screen_simons(d):
    s, c = 0, {}
    c['w52'] = d['w52Ratio']  is not None and d['w52Ratio']  >= 0.80; s += 3 if c['w52'] else 0
    c['eps'] = d['epsGrowth'] is not None and d['epsGrowth'] >= 15;   s += 3 if c['eps'] else 0
    c['rev'] = d['revGrowth'] is not None and d['revGrowth'] >= 10;   s += 2 if c['rev'] else 0
    c['roe'] = d['ROE']       is not None and d['ROE']       >= 15;   s += 1 if c['roe'] else 0
    c['peg'] = d['PEG']       is not None and 0 < d['PEG']   <= 2.0; s += 1 if c['peg'] else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'w52':'52週高値80%以上 (3点)','eps':'EPS成長≥15% (3点)','rev':'売上成長≥10% (2点)','roe':'ROE≥15% (1点)','peg':'PEG≤2.0 (1点)'}}

def screen_testa(d):
    """テスタ（近似）: 高配当・安定収益・低負債の長期保有スタイル"""
    s, c = 0, {}
    c['div']  = d['divYield']  is not None and d['divYield']  >= 3;    s += 4 if c['div']  else 0
    c['roe']  = d['ROE']       is not None and d['ROE']       >= 15;   s += 2 if c['roe']  else 0
    c['debt'] = d['debtRatio'] is not None and d['debtRatio'] <= 0.8;  s += 2 if c['debt'] else 0
    c['om']   = d['opMargin']  is not None and d['opMargin']  >= 15;   s += 1 if c['om']   else 0
    c['fcf']  = d['FCF']       is not None and d['FCF']       > 0;     s += 1 if c['fcf']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'div':'配当利回り≥3% (4点)','roe':'ROE≥15% (2点)','debt':'負債比率≤0.8 (2点)','om':'営業利益率≥15% (1点)','fcf':'FCFプラス (1点)'}}

def screen_kiritani(d):
    """桐谷広人: 株主優待・高配当・割安バリュー"""
    s, c = 0, {}
    c['div']  = d['divYield']  is not None and d['divYield']  >= 2;    s += 3 if c['div']  else 0
    c['per']  = d['PER']       is not None and d['PER']       <= 15;   s += 3 if c['per']  else 0
    c['pbr']  = d['PBR']       is not None and d['PBR']       <= 1.2;  s += 2 if c['pbr']  else 0
    c['debt'] = d['debtRatio'] is not None and d['debtRatio'] <= 1.0;  s += 1 if c['debt'] else 0
    c['fcf']  = d['FCF']       is not None and d['FCF']       > 0;     s += 1 if c['fcf']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'div':'配当利回り≥2% (3点)','per':'PER≤15 (3点)','pbr':'PBR≤1.2 (2点)','debt':'負債比率≤1.0 (1点)','fcf':'FCFプラス (1点)'}}

def screen_fujino(d):
    """藤野英人: 成長企業・ROE重視・長期ファンダメンタル"""
    s, c = 0, {}
    c['roe']  = d['ROE']       is not None and d['ROE']       >= 15;   s += 3 if c['roe']  else 0
    c['eps']  = d['epsGrowth'] is not None and d['epsGrowth'] >= 10;   s += 3 if c['eps']  else 0
    c['rev']  = d['revGrowth'] is not None and d['revGrowth'] >= 10;   s += 2 if c['rev']  else 0
    c['om']   = d['opMargin']  is not None and d['opMargin']  >= 10;   s += 1 if c['om']   else 0
    c['debt'] = d['debtRatio'] is not None and d['debtRatio'] <= 1.5;  s += 1 if c['debt'] else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'roe':'ROE≥15% (3点)','eps':'EPS成長≥10% (3点)','rev':'売上成長≥10% (2点)','om':'営業利益率≥10% (1点)','debt':'負債比率≤1.5 (1点)'}}

def screen_okuno(d):
    """奥野一成: 長期・参入障壁・高ROE・低負債の本質的価値投資"""
    s, c = 0, {}
    c['roe']  = d['ROE']       is not None and d['ROE']       >= 20;   s += 3 if c['roe']  else 0
    c['om']   = d['opMargin']  is not None and d['opMargin']  >= 20;   s += 3 if c['om']   else 0
    c['debt'] = d['debtRatio'] is not None and d['debtRatio'] <= 0.5;  s += 2 if c['debt'] else 0
    c['eps']  = d['epsGrowth'] is not None and d['epsGrowth'] >= 5;    s += 1 if c['eps']  else 0
    c['fcf']  = d['FCF']       is not None and d['FCF']       > 0;     s += 1 if c['fcf']  else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'roe':'ROE≥20% (3点)','om':'営業利益率≥20% (3点)','debt':'負債比率≤0.5 (2点)','eps':'EPS成長≥5% (1点)','fcf':'FCFプラス (1点)'}}

def screen_imura(d):
    """井村俊哉: 売上成長×割安×モメンタム。成長の源泉である売上が伸びており、PERが成長率より低い割安成長株"""
    s, c = 0, {}
    c['rev']  = d['revGrowth']  is not None and d['revGrowth']  >= 20;  s += 3 if c['rev']  else 0
    c['eps']  = d['epsGrowth']  is not None and d['epsGrowth']  >= 20;  s += 3 if c['eps']  else 0
    # PEGが1未満＝成長率よりPERが低い（割安成長）
    c['peg']  = d['PEG']        is not None and 0 < d['PEG']    < 1.0;  s += 2 if c['peg']  else 0
    c['w52']  = d['w52Ratio']   is not None and d['w52Ratio']   >= 0.75; s += 1 if c['w52']  else 0
    c['om']   = d['opMargin']   is not None and d['opMargin']   >= 10;   s += 1 if c['om']   else 0
    return {'score': s, 'max': 10, 'checks': c,
            'scoring': {'rev':'売上成長率≥20% (3点)','eps':'EPS成長率≥20% (3点)','peg':'PEG<1.0・割安成長 (2点)','w52':'52週高値75%以上 (1点)','om':'営業利益率≥10% (1点)'}}

SCREENERS = {
    'buffett':    {'fn': screen_buffett,    'name': 'ウォーレン・バフェット',    'icon': '🏦'},
    'lynch':      {'fn': screen_lynch,      'name': 'ピーター・リンチ',          'icon': '📈'},
    'graham':     {'fn': screen_graham,     'name': 'ベンジャミン・グレアム',    'icon': '📚'},
    'greenblatt': {'fn': screen_greenblatt, 'name': 'ジョエル・グリーンブラット','icon': '🧮'},
    'oneil':      {'fn': screen_oneil,      'name': 'ウィリアム・オニール',      'icon': '🚀'},
    'dalio':      {'fn': screen_dalio,      'name': 'レイ・ダリオ',              'icon': '⚖️'},
    'dreman':     {'fn': screen_dreman,     'name': 'デビッド・ドレマン',        'icon': '🔄'},
    'neff':       {'fn': screen_neff,       'name': 'ジョン・ネフ',              'icon': '💰'},
    'fisher':     {'fn': screen_fisher,     'name': 'ケン・フィッシャー',        'icon': '📉'},
    'simons':     {'fn': screen_simons,     'name': 'ジム・サイモンズ',          'icon': '🤖'},
    # 日本人投資家
    'testa':      {'fn': screen_testa,      'name': 'テスタ（近似）',             'icon': '🎯'},
    'kiritani':   {'fn': screen_kiritani,   'name': '桐谷広人',                  'icon': '🎁'},
    'fujino':     {'fn': screen_fujino,     'name': '藤野英人',                  'icon': '🌱'},
    'okuno':      {'fn': screen_okuno,      'name': '奥野一成',                  'icon': '🏯'},
    'imura':      {'fn': screen_imura,      'name': '井村俊哉',                  'icon': '🎭'},
}

# 各投資家の通過閾値（厳密基準）
PASS_THRESHOLD = {
    'buffett':    6,  # 10点中6点以上
    'lynch':      6,  # 10点中6点以上
    'graham':     6,  # 10点中6点以上
    'greenblatt': 7,  # 10点中7点以上（ROIC+益回り必須）
    'oneil':      6,  # 10点中6点以上
    'dalio':      5,  # 10点中5点以上
    'dreman':     6,  # 10点中6点以上
    'neff':       7,  # 10点中7点以上（PER+配当必須）
    'fisher':     5,  # 10点中5点以上
    'simons':     6,  # 10点中6点以上
    'testa':      6,  # 10点中6点以上（配当必須）
    'kiritani':   6,  # 10点中6点以上（配当+PER必須）
    'fujino':     6,  # 10点中6点以上（ROE+成長必須）
    'okuno':      6,  # 10点中6点以上（ROE+営業利益率必須）
    'imura':      6,  # 10点中6点以上（売上+EPS成長必須）
}

# ------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------

if __name__ == '__main__':
    print('\n📊 15大投資家 レジェンドスクリーナー データ生成')
    print('=' * 55)

    # Step1: まとめ取得（50銘柄ずつ → リクエスト数を大幅削減）
    BATCH_SIZE = 50
    all_data   = []
    total      = len(UNIVERSE)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f'\n🔍 {total}銘柄を{BATCH_SIZE}銘柄ずつ取得中...')

    for batch_idx in range(total_batches):
        batch = UNIVERSE[batch_idx*BATCH_SIZE:(batch_idx+1)*BATCH_SIZE]
        s = batch_idx*BATCH_SIZE
        print(f'\n  📦 バッチ {batch_idx+1}/{total_batches} ({s+1}〜{min(s+BATCH_SIZE,total)}銘柄目)...')
        try:
            tickers_obj = yf.Tickers(' '.join(batch))
            for j, ticker in enumerate(batch):
                print(f'    [{s+j+1:>3}/{total}] {ticker}...', end=' ', flush=True)
                try:
                    d = parse_info(ticker, tickers_obj.tickers[ticker].info)
                    if d:
                        all_data.append(d)
                        print('✓')
                    else:
                        print('✗ データなし')
                except Exception as e:
                    print(f'✗ {str(e)[:30]}')
                time.sleep(0.2)  # スロットリング：銘柄間0.2秒
        except Exception as e:
            print(f'  ⚠ バッチ失敗({e})→個別取得...')
            for j, ticker in enumerate(batch):
                print(f'    [{s+j+1:>3}/{total}] {ticker}...', end=' ', flush=True)
                d = get_data(ticker)
                if d: all_data.append(d); print('✓')
                else: print('✗')
                time.sleep(0.3)
        if batch_idx + 1 < total_batches:
            time.sleep(0.5)  # バッチ間0.5秒待機

    # Yahoo完全停止チェック：取得成功が10件未満なら警告
    if len(all_data) < 10:
        print('\n⚠ 警告: 取得できた銘柄が10件未満です。')
        print('  → Yahoo Financeが一時的に利用できない可能性があります。')
        print('  → 30分〜1時間後に再実行してください。')

    print(f'\n✅ 取得完了: {len(all_data)}/{total}銘柄')

    # Step2: 各投資家でスクリーニング
    print('\n📋 スクリーニング実行中...')
    screened = {}

    for key, meta in SCREENERS.items():
        results = []
        for d in all_data:
            r = meta['fn'](d)
            results.append({
                'ticker':  d['ticker'],
                'name':    d['name'],
                'sector':  d['sector'],
                'price':   d['price'],
                'marketCapB': round(d['marketCap'] / 1e9, 2) if d['marketCap'] else None,
                'ROE':     d['ROE'],
                'opMargin':d['opMargin'],
                'debtRatio':d['debtRatio'],
                'FCF':     d['FCF'],
                'PER':     d['PER'],
                'PBR':     d['PBR'],
                'PEG':     d['PEG'],
                'PSR':     d['PSR'],
                'epsGrowth':d['epsGrowth'],
                'revGrowth':d['revGrowth'],
                'currentRatio':d['currentRatio'],
                'divYield':d['divYield'],
                'isJP':       d['ticker'].endswith('.T'),
                'w52Ratio':   d['w52Ratio'],
                'w52Position':d.get('w52Position'),
                'price50ma':  d.get('price50ma'),
                'price200ma': d.get('price200ma'),
                'trend52w':   d.get('trend52w', False),
                'trendEps':   d.get('trendEps', False),
                'trendRev':   d.get('trendRev', False),
                'trendScore': d.get('trendScore', 0),
                'trendLabel': d.get('trendLabel', '—'),
                'score':   r['score'],
                'max':     r['max'],
                'checks':  r['checks'],
                **{k: v for k, v in r.items() if k not in ['score','max','checks']},
            })

        results.sort(key=lambda x: x['score'], reverse=True)

        # 厳密基準で通過銘柄を絞る（緩和なし・0件は0件）
        threshold    = PASS_THRESHOLD.get(key, 5)
        strict_pass  = [r for r in results if r['score'] >= threshold]
        passed_count = len(strict_pass)
        display_results = strict_pass  # 通過銘柄のみ表示

        print(f'  {meta["icon"]} {meta["name"]}: {passed_count}件通過'
              + (f' → Top{TOP_N}表示' if passed_count > TOP_N else '')
              + (' ← 該当なし' if passed_count == 0 else ''))

        screened[key] = {
            'name':        meta['name'],
            'icon':        meta['icon'],
            'passedCount': passed_count,
            'hitCount':    passed_count,
            'relaxed':     False,
            'threshold':   threshold,
            'results':     display_results,  # 全件保存（表示件数はHTML側で制御）
        }

    # Step3: JSON出力
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 前回データを読み込んでスコア変化を計算
    out_path      = os.path.join(script_dir, 'legend_result.json')
    history_path  = os.path.join(script_dir, 'legend_history.json')
    prev_scores   = {}  # {key: {ticker: score}}

    if os.path.exists(out_path):
        try:
            with open(out_path, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
            for key, inv in prev_data.get('screened', {}).items():
                prev_scores[key] = {r['ticker']: r['score'] for r in inv.get('results', [])}
        except Exception:
            pass

    # スコア変化をresultsに付与
    for key, inv in screened.items():
        prev = prev_scores.get(key, {})
        for r in inv['results']:
            t = r['ticker']
            if t in prev:
                r['scoreDiff'] = r['score'] - prev[t]  # プラス=上昇 マイナス=下降
            else:
                r['scoreDiff'] = None  # 新規登場

    output = {
        'generatedAt':  datetime.now().strftime('%Y-%m-%d %H:%M'),
        'totalScanned': len(all_data),
        'universe':     len(UNIVERSE),
        'screened':     screened,
    }

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 履歴ファイルにスコアサマリーを追記（最大90件）
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            pass

    snapshot = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'scores': {
            key: {r['ticker']: r['score'] for r in inv['results']}
            for key, inv in screened.items()
        }
    }
    history.append(snapshot)
    history = history[-90:]  # 最大90件（3ヶ月分）
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f'\n✅ データ保存完了: {out_path}')
    print(f'📚 履歴保存完了:   {history_path} ({len(history)}件蓄積)')
    print('🌐 次に legend_dashboard.html をブラウザで開いてください！')
    print('=' * 55)
