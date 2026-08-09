import random
from datetime import datetime
import os
import streamlit as st
from google import genai

# ---------------------------------------------------------
# 1. ページ基本設定 ＆ APIキー取得
# ---------------------------------------------------------
st.set_page_config(
    page_title="VIA-ADT 統合診断アセスメント",
    page_icon="🧠",
    layout="centered"
)

# StreamlitのSecrets（設定画面）からAPIキーを自動取得
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 万が一Secretsの設定がない場合のみ入力枠を出す（予備）
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password", help="AI Studioで取得したAPIキーを入力してください")

# ---------------------------------------------------------
# 2. 質問データ定義 (パターンA / パターンB)
# ---------------------------------------------------------
QUESTIONS_PATTERN_A = [
    # 知性・知識
    {"id": "q1", "category": "知性・知識", "text": "Q1. あまり知られていないジャンルでも、気になったらどんどん調べちゃう？"},
    {"id": "q2", "category": "知性・知識", "text": "Q2. 行ったことのない場所や食べたことのないものにトライするのが好き？"},
    {"id": "q3", "category": "知性・知識", "text": "Q3. 物事の仕組みや、「なぜそうなるのか」を突き詰めて考える方だ？"},
    {"id": "q4", "category": "知性・知識", "text": "Q4. 新しいスキルや知識を身につけること自体にワクワクする？"},
    {"id": "q5", "category": "知性・知識", "text": "Q5. 複雑な問題が起きたとき、冷静に全体を観察して判断できる？"},
]

QUESTIONS_PATTERN_B = [
    # 知性・知識
    {"id": "q1", "category": "知性・知識", "text": "Q1. 知らないことに出会うと、納得いくまで徹底的に調べたくなる？"},
    {"id": "q2", "category": "知性・知識", "text": "Q2. 新しい体験や未知の分野に飛び込むことに抵抗がない？"},
    {"id": "q3", "category": "知性・知識", "text": "Q3. 事実やデータをじっくり分析して真実を見極めるのが得意？"},
    {"id": "q4", "category": "知性・知識", "text": "Q4. 自分の成長のために常に新しいことを学び続けている？"},
    {"id": "q5", "category": "知性・知識", "text": "Q5. 周囲から「アドバイスが的確で視野が広い」と言われることが多い？"},
]

# アクセス（ページ読み込み）のたびにランダムで A または B を選択する
if "pattern_type" not in st.session_state:
    st.session_state["pattern_type"] = random.choice(["A", "B"])

active_questions = QUESTIONS_PATTERN_A if st.session_state["pattern_type"] == "A" else QUESTIONS_PATTERN_B

# ---------------------------------------------------------
# 3. メイン表示 ＆ 入力フォーム
# ---------------------------------------------------------
st.title("🧠 VIA-ADT 統合診断アセスメント")
st.caption("あなたの「強み（VIA）」と「葛藤パターン（ADT）」をAIがやさしく読み解きます。")

# トーン選択（タイトルの直下に配置）
mode = st.radio(
    "💬 表示モードを選択してください",
    ["カジュアル（わかりやすい言葉）", "プロフェッショナル（本格コーチング）"],
    index=0,
    horizontal=True
)

st.markdown("---")

with st.form("via_adt_form"):
    st.subheader("1. 基本情報")
    user_name = st.text_input("お名前 / ニックネーム", value="ゲスト")

    st.markdown("---")
    st.subheader("2. 強みチェック（VIAアセスメント）")
    st.info(f"現在のトーン：**{mode}** （表現パターン: {st.session_state['pattern_type']}）")

    answers = {}
    options = [
        "1: 全くあてはまらない",
        "2: あまりあてはまらない",
        "3: どちらとも言えない",
        "4: ややあてはまる",
        "5: 非常にあてはまる"
    ]

    current_cat = ""
    for q in active_questions:
        if q["category"] != current_cat:
            current_cat = q["category"]
            st.markdown(f"### ◆ {current_cat}")
        
        answers[q["id"]] = st.radio(
            q["text"],
            options,
            index=2,
            key=q["id"]
        )

    st.markdown("---")
    submitted = st.form_submit_button("🚀 診断レポートを生成する", use_container_width=True)

# ---------------------------------------------------------
# 4. AI診断レポートの生成処理
# ---------------------------------------------------------
if submitted:
    if not api_key:
        st.error("APIキーが設定されていません。StreamlitのSecretsにGEMINI_API_KEYを設定してください。")
    else:
        with st.spinner("AIが回答を分析してレポートを作成中..."):
            try:
                # APIクライアントの準備
                client = genai.Client(api_key=api_key)

                # 回答の整形
                answer_summary = "\n".join([f"- {q['text']}: {answers[q['id']]}" for q in active_questions])

                # プロンプトの組み立て
                prompt = f"""
あなたは優しく洞察力に満ちた専門心理コーチです。
以下のユーザーの回答結果を基に、VIA強みアセスメントとADT（葛藤・葛藤パターン）の視点を統合した個別診断レポートを作成してください。

【受診者情報】
- お名前: {user_name}様
- 希望トーン: {mode}

【回答データ】
{answer_summary}

【出力フォーマット要求】
1. **ファーストインプレッション・全体傾向**
2. **あなた際立つ「強み」の分析（VIA）**
3. **隠れた「葛藤やブレーキ」のサイン（ADT）**
4. **明日から使える具体的なアクションプラン（1〜2点）**

トーン設定が「カジュアル」の場合は、親しみやすくポジティブな言葉遣い（絵文字適度）で書いてください。
トーン設定が「プロフェッショナル」の場合は、洞察深く論理的でプロフェッショナルなコーチングトーンで書いてください。
"""

                # Gemini API呼び出し
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                report_text = response.text

                # 結果表示
                st.success("🎉 アセスメントレポートが完成しました！")
                st.markdown("---")
                st.markdown(report_text)

                # コピペ用エリア
                st.markdown("---")
                st.subheader("📋 テキストのコピー")
                st.caption("以下の枠内のテキストは右上のアイコンから全選択・コピーができます。")
                st.code(report_text, language=None)

            except Exception as e:
                st.error(f"レポート生成中にエラーが発生しました: {e}")
