# via-adt_assessment.py
# VIA × ADT 統合診断アセスメント Web App (Gemini API版 / エラー修正版)

import streamlit as st
import random
from collections import defaultdict
from google import genai

# ---------------------------------------------------------
# 1. ページ基本設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="VIA-ADT 統合診断アセスメント",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 質問データの定義（バリエーション対応）
# ---------------------------------------------------------
# Aパターン（std: 標準 / cas: カジュアル）
QUESTIONS_PATTERN_A = [
    # I. 知性・知識
    {"id": 1, "cat": "I. 知性・知識 (Wisdom)", "strength": "好奇心", 
     "text_std": "未知の話題や新しい分野に出会うと、自ら進んで調べたり試したりしたくなる。",
     "text_cas": "新しいことや面白そうなものを見つけると、ワクワクしてすぐ調べたくなる？"},
    {"id": 2, "cat": "I. 知性・知識 (Wisdom)", "strength": "好奇心", 
     "text_std": "日常の当たり前の現象に対しても、「なぜだろう？」と興味や疑問を抱くことが多い。",
     "text_cas": "ふだんの生活の中で「これってなんでだろう？」と疑問を持つことが多い？"},
    {"id": 3, "cat": "I. 知性・知識 (Wisdom)", "strength": "知的探求心", 
     "text_std": "新しい知識やスキルを自分のものにしていくプロセスそのものに大きな喜びを感じる。",
     "text_cas": "新しいスキルや知識を学んで自分のものにしていく過程が、とにかく楽しい？"},
    {"id": 4, "cat": "I. 知性・知識 (Wisdom)", "strength": "判断力・思考力", 
     "text_std": "情報を鵜呑みにせず、事実や根拠に基づいて客観的に物事を評価するよう心がけている。",
     "text_cas": "ウワサや思い込みに流されず、ちゃんと事実や理由を確かめてから判断する？"},
    {"id": 5, "cat": "I. 知性・知識 (Wisdom)", "strength": "創造性", 
     "text_std": "既存のやり方に捉われず、自分なりの新しいアイデアやユニークなアプローチを生み出すのが得意だ。",
     "text_cas": "決まったやり方にとらわれず、自分ならではの新しい工夫やアイデアを出すのが好き？"},
    {"id": 6, "cat": "I. 知性・知識 (Wisdom)", "strength": "大所高所の視点", 
     "text_std": "周囲が目先の混乱に惑わされている時でも、状況を俯瞰して本質的な助言を示すことができる。",
     "text_cas": "みんなが慌てている時でも、一歩引いて落ち着いたアドバイスができる？"},

    # II. 勇気・情熱
    {"id": 7, "cat": "II. 勇気・情熱 (Courage)", "strength": "勇敢さ", 
     "text_std": "反対意見やリスクがあっても、自分が「正解だ」と信じることのために踏み出せる。",
     "text_cas": "周りと意見が違ったりリスクがあっても、自分の信念のために思い切って行動できる？"},
    {"id": 8, "cat": "II. 勇気・情熱 (Courage)", "strength": "粘り強さ", 
     "text_std": "途中で壁や失敗にあたっても、決めた目標を最後までやり遂げる執着心がある。",
     "text_cas": "途中でうまくいかないことがあっても、あきらめずに最後までやり遂げられる？"},
    {"id": 9, "cat": "II. 勇気・情熱 (Courage)", "strength": "誠実さ", 
     "text_std": "自分を良く見せようと偽らず、どんな相手に対してもありのままの素の自分（言葉と行動）で接する。",
     "text_cas": "見栄を張ったり嘘をついたりせず、いつでも素の自分で誠実に向き合っている？"},
    {"id": 10, "cat": "II. 勇気・情熱 (Courage)", "strength": "情熱・熱意", 
     "text_std": "毎日の生活や仕事に対して高いエネルギーを持ち、ワクワクしながら精力的に取り組める。",
     "text_cas": "毎日やっていることに対して、エネルギー全開で楽しく情熱的に取り組めている？"},

    # III. 人間愛・共感
    {"id": 11, "cat": "III. 人間愛・共感 (Humanity)", "strength": "愛する力", 
     "text_std": "身近な人々（家族・パートナー・友人）と深い信頼関係を築き、互いを心から大切に思える。",
     "text_cas": "大切な人と深い絆をつくり、お互いを心から思い合える関係を大切にしている？"},
    {"id": 12, "cat": "III. 人間愛・共感 (Humanity)", "strength": "親切心", 
     "text_std": "見返りを期待せず、困っている人や周囲の人を自然と助けたり気遣ったりする。",
     "text_cas": "困っている人がいたら、見返りを求めずにサッと手を差し伸べられる？"},
    {"id": 13, "cat": "III. 人間愛・共感 (Humanity)", "strength": "社会的知性", 
     "text_std": "他者の感情やその場の空気を察するのが早く、相手が何を求めているかを直感的に理解できる。",
     "text_cas": "相手の気持ちや場の空気を察するのが得意で、気配りが自然にできる？"},

    # IV. 正義感・市民性
    {"id": 14, "cat": "IV. 正義感・市民性 (Justice)", "strength": "チームワーク", 
     "text_std": "集団の目標達成のために自分の役割を果たし、メンバーと協力して取り組むことができる。",
     "text_cas": "みんなで協力して何かを成し遂げるために、自分の役割をしっかり果たせる？"},
    {"id": 15, "cat": "IV. 正義感・市民性 (Justice)", "strength": "公平さ", 
     "text_std": "自分の好き嫌いや利害関係に関わらず、すべての人を偏りなく平等に扱うよう努めている。",
     "text_cas": "好き嫌いや相手によって態度を変えず、だれに対してもフェアに接している？"},
    {"id": 16, "cat": "IV. 正義感・市民性 (Justice)", "strength": "リーダーシップ", 
     "text_std": "集団を1つの方向へ導き、メンバーの意欲を引き出しながら目標へ前進させることができる。",
     "text_cas": "チームの雰囲気を盛り上げながら、みんなを引っぱっていける？"},

    # V. 節制・自律
    {"id": 17, "cat": "V. 節制・自律 (Temperance)", "strength": "寛容さ・許し", 
     "text_std": "他人の過ちや自分を傷つけた言動に対して、根に持たずに許すことができる。",
     "text_cas": "人の失敗や自分への嫌な言動を引きずらず、おだやかに許すことができる？"},
    {"id": 18, "cat": "V. 節制・自律 (Temperance)", "strength": "謙虚さ", 
     "text_std": "自分の実績や成果を自慢したり誇張したりせず、控えめな態度を保っている。",
     "text_cas": "自分の成果を威張ったり自慢したりせず、いつでも控え目でいられる？"},
    {"id": 19, "cat": "V. 節制・自律 (Temperance)", "strength": "思慮深さ", 
     "text_std": "言動を起こす前にそのリスクや周囲への影響を慎重に考慮し、軽率な失敗を防ぐことができる。",
     "text_cas": "行動を起こす前に「これをしたらどうなるか」を一歩止まってしっかり考えられる？"},
    {"id": 20, "cat": "V. 節制・自律 (Temperance)", "strength": "自己統制", 
     "text_std": "感情の起伏や自制心を乱す誘惑に振り回されず、自分の行動や習慣を適切にコントロールできる。",
     "text_cas": "気分や誘惑に流されず、やるべきことに集中して自分をコントロールできる？"},

    # VI. 超越性・精神性
    {"id": 21, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "審美眼", 
     "text_std": "自然の美しさ、芸術作品、あるいは他人の優れた技術や生き方に深く感動する。",
     "text_cas": "綺麗な景色や素敵なアート、人の素晴らしいこだわりを見て心から感動できる？"},
    {"id": 22, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "感謝", 
     "text_std": "日常の当たり前の中にある恵みや、他者からの小さな助けに対して心から「ありがたい」と感じられる。",
     "text_cas": "普段の暮らしや周りの人の優しさに、普段から「ありがたいな」と感じている？"},
    {"id": 23, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "希望・楽観性", 
     "text_std": "未来に対して明るい見通しを持ち、どんな状況でも「きっと良くなる」と前向きに信じられる。",
     "text_cas": "「これからはきっと良くなる！」と、未来に対して前向きな気持ちを持てている？"},
    {"id": 24, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "目的意識", 
     "text_std": "自分の人生には果たすべき目的や明確な意味が存在していると信じている。",
     "text_cas": "「自分は何のために頑張っているのか」という自分なりの軸や目的を感じている？"}
]

# Bパターン（シャッフル時の別表現）
QUESTIONS_PATTERN_B = [
    {"id": 1, "cat": "I. 知性・知識 (Wisdom)", "strength": "好奇心", "text_std": "自分の専門外のことでも、興味を感じたら積極的に情報収集を行う。", "text_cas": "あまり知らないジャンルでも、気になったらどんどん調べちゃう？"},
    {"id": 2, "cat": "I. 知性・知識 (Wisdom)", "strength": "好奇心", "text_std": "新しい場所や食べたことのない料理に挑戦することに強い魅力を感じる。", "text_cas": "行ったことのない場所や食べたことのないものにトライするのが好き？"},
    {"id": 3, "cat": "I. 知性・知識 (Wisdom)", "strength": "知的探求心", "text_std": "本を読んだり講座を受けたりして、知識を体系的に深める時間が好きだ。", "text_cas": "じっくり読書したり勉強したりして、知識を深めるのが好き？"},
    {"id": 4, "cat": "I. 知性・知識 (Wisdom)", "strength": "判断力・思考力", "text_std": "反対の意見にも耳を傾け、複数の視点から論理的に分析しようとする。", "text_cas": "自分と違う考え意見もちゃんと聞いた上で、ロジカルに考えられる？"},
    {"id": 5, "cat": "I. 知性・知識 (Wisdom)", "strength": "創造性", "text_std": "何か問題が起きた時、誰も思いつかないようなユニークな解決策を思いつく。", "text_cas": "困ったことが起きたとき、ハッとするような面白い解決法を思いつく？"},
    {"id": 6, "cat": "I. 知性・知識 (Wisdom)", "strength": "大所高所の視点", "text_std": "複雑な問題が発生しても、全体像を整理して物事をシンプルに捉え直せる。", "text_cas": "ややこしい問題も、スッキリ整理して「要するにこうだよね」と言える？"},
    {"id": 7, "cat": "II. 勇気・情熱 (Courage)", "strength": "勇敢さ", "text_std": "プレッシャーがかかる場面でも、言うべきことを恐れずに発言できる。", "text_cas": "緊張する場面や目上の人が相手でも、言うべきことをきちんと言える？"},
    {"id": 8, "cat": "II. 勇気・情熱 (Courage)", "strength": "粘り強さ", "text_std": "困難なタスクほど燃え上がり、形になるまで泥臭く続けられる。", "text_cas": "大変な仕事や目標ほど燃えて、完成するまで粘り強くがんばれる？"},
    {"id": 9, "cat": "II. 勇気・情熱 (Courage)", "strength": "誠実さ", "text_std": "約束を守り、裏表のない言動を徹底することで信頼を得ている。", "text_cas": "約束は絶対に守るし、ウラオモテのない対応で信頼されていると感じる？"},
    {"id": 10, "cat": "II. 勇気・情熱 (Courage)", "strength": "情熱・熱意", "text_std": "自分の仕事やプロジェクトに対して熱量を持って語ることができる。", "text_cas": "自分がやっていることについて、熱っぽくワクワクしながら語れる？"},
    {"id": 11, "cat": "III. 人間愛・共感 (Humanity)", "strength": "愛する力", "text_std": "大切な人のためなら、自分の時間や労力を惜しみなく使うことができる。", "text_cas": "大事な家族や友人のためなら、自分の時間や手間を惜しまず使える？"},
    {"id": 12, "cat": "III. 人間愛・共感 (Humanity)", "strength": "親切心", "text_std": "日常の中で、周りの人が心地よく過ごせるようにちょっとした気配りをする。", "text_cas": "みんなが気持ちよく過ごせるように、普段から小さな気配りができる？"},
    {"id": 13, "cat": "III. 人間愛・共感 (Humanity)", "strength": "社会的知性", "text_std": "人間関係の摩擦が起きた時、双方の感情に配慮してうまく仲裁できる。", "text_cas": "人がモメている時、お互いの気持ちを気づかってうまく間に入れる？"},
    {"id": 14, "cat": "IV. 正義感・市民性 (Justice)", "strength": "チームワーク", "text_std": "自分の手柄にこだわらず、チーム全体が成果を出せるように動くことができる。", "text_cas": "自分を目立たせることより、チームみんなで成功することを目指せる？"},
    {"id": 15, "cat": "IV. 正義感・市民性 (Justice)", "strength": "公平さ", "text_std": "立場が弱い人に対しても、尊重をもって公平に接することを意識している。", "text_cas": "どんな立場の人に対しても、上から目線にならず平等に接している？"},
    {"id": 16, "cat": "IV. 正義感・市民性 (Justice)", "strength": "リーダーシップ", "text_std": "みんなの意見を吸い上げながら、合意形成をして方向性を決めるのが得意だ。", "text_cas": "みんなの意見を聞き取りながら、うまくまとめ上げて方向性を決められる？"},
    {"id": 17, "cat": "V. 節制・自律 (Temperance)", "strength": "寛容さ・許し", "text_std": "失敗した人を責めるのではなく、「次どうするか」に気持ちを切り替えられる。", "text_cas": "失敗した人を責めずに、「次がんばろう！」と気持ちを切り替えられる？"},
    {"id": 18, "cat": "V. 節制・自律 (Temperance)", "strength": "謙虚さ", "text_std": "自分が褒められても過度に浮かれず、周囲のおかげだと感謝できる。", "text_cas": "褒められても調子に乗らず、「周りの協力のおかげだな」と思える？"},
    {"id": 19, "cat": "V. 節制・自律 (Temperance)", "strength": "思慮深さ", "text_std": "感情的になって思わぬ発言をしてしまわないよう、一度心を落ち着かせる。", "text_cas": "カッとなって余計なことを言わないように、一呼吸置くことができる？"},
    {"id": 20, "cat": "V. 節制・自律 (Temperance)", "strength": "自己統制", "text_std": "長期的目標のために、目先の誘惑（スマホや娯楽など）を我慢できる。", "text_cas": "目標を達成するために、目先の誘惑（スマホや遊びなど）をガマンできる？"},
    {"id": 21, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "審美眼", "text_std": "優れたデザインやプロの仕事ぶりに触れると、胸が熱くなる感覚がある。", "text_cas": "プロのこだわりや洗練されたデザインを見ると、キュンと感動する？"},
    {"id": 22, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "感謝", "text_std": "「今日も一日無事に過ごせた」といった日常の平穏に感謝の気持ちが湧く。", "text_cas": "「今日が無事に終わってよかったな」と日常にほっこり感謝できる？"},
    {"id": 23, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "希望・楽観性", "text_std": "逆境に陥ったとしても「ここから学べることや良い面がある」と考え直せる。", "text_cas": "ピンチになっても「ここから何か得られるはず！」とポジティブになれる？"},
    {"id": 24, "cat": "VI. 超越性・精神性 (Transcendence)", "strength": "目的意識", "text_std": "自分の軸（ビジョンや信念）を持っているため、選択に迷うことが少ない。", "text_cas": "自分の中にしっかりした軸があるから、大事な決断でグラつきにくい？"}
]

OPTIONS = [1, 2, 3, 4, 5]
OPTION_LABELS = {
    1: "1: 全くあてはまらない",
    2: "2: あまりあてはまらない",
    3: "3: どちらとも言えない",
    4: "4: ややあてはまる",
    5: "5: 非常にあてはまる"
}

# ---------------------------------------------------------
# 3. サイドバー設定 (操作系をまとめて即時反映させる)
# ---------------------------------------------------------
st.sidebar.title("⚙️ 設定")

api_key = st.sidebar.text_input("Gemini API Key", type="password", help="AI Studioで取得したAPIキーを入力してください")

st.sidebar.markdown("---")

# 言葉遣いモード
mode = st.sidebar.radio(
    "💬 言葉遣い・トーン",
    ["カジュアル（わかりやすい言葉）", "プロフェッショナル（本格コーチング）"],
    index=0
)

st.sidebar.markdown("---")

# アクセス（ページ読み込み）のたびにランダムで A または B を選択する
if "pattern_type" not in st.session_state:
    st.session_state["pattern_type"] = random.choice(["A", "B"])

# 選択されたパターンのデータセットを取得
active_questions = QUESTIONS_PATTERN_A if st.session_state["pattern_type"] == "A" else QUESTIONS_PATTERN_B


# ---------------------------------------------------------
# 4. メイン表示 ＆ 入力フォーム
# ---------------------------------------------------------
st.title("🧠 VIA-ADT 統合診断アセスメント")
st.caption("あなたの「強み（VIA）」と「葛藤パターン（ADT）」をAIがやさしく読み解きます。")

with st.form("via_adt_form"):
    st.subheader("1. 基本情報")
    user_name = st.text_input("お名前 / ニックネーム", value="ゲスト")

    st.markdown("---")
    st.subheader("2. 強みチェック（VIAアセスメント）")
    st.info(f"現在のトーン：**{mode}** （表現パターン: {st.session_state['pattern_type']}）")

    answers = {}
    current_cat = ""
    
    for q in active_questions:
        if q["cat"] != current_cat:
            current_cat = q["cat"]
            st.markdown(f"#### 🔹 {current_cat}")
        
        # モード（カジュアル / プロ）に応じてテキストを切り替え
        q_text = q["text_cas"] if "カジュアル" in mode else q["text_std"]
        
        answers[q["id"]] = st.radio(
            f"**Q{q['id']}. {q_text}**",
            options=OPTIONS,
            format_func=lambda x: OPTION_LABELS[x],
            index=2,
            key=f"q_{q['id']}"
        )

    st.markdown("---")
    st.subheader("3. 葛藤と内省チェック（ADTアセスメント）")
    
    if "カジュアル" in mode:
        st.caption("最近のモヤモヤや悩みから、あなたの成長のヒントを探ります。")
        adt_q1 = st.text_area("Q1.【モヤモヤ】最近、仕事や人間関係で一番「モヤッとした」「納得いかなかった」出来事は？", value="チームの提案を出したのに反対された")
        adt_q2 = st.text_area("Q2.【自分のこだわり】その時、自分のどんな「大事にしたい考え・ルール」が邪魔された感じがした？", value="成果を出すためにどんどん変えるべき")
        adt_q3 = st.text_area("Q3.【とった行動】その時、あなた自身は周りにどんな対応をとった？", value="表面上は合わせて引き下がったが内心がっかりした")
        adt_q4 = st.text_area("Q4.【心の裏の不安】もし相手に歩み寄って譲ったら、どんな嫌なことや不安が起こりそう？", value="軸がないと思われたり、成果が出なくなるのが怖い")
        adt_q5 = st.text_area("Q5.【いつものクセ】普段は「周りの期待」と「自分の信念」、どちらを優先しやすい？", value="自分の信念を優先しがち")
        adt_q6 = st.text_area("Q6.【これからの自分】これからどんな自分に成長していきたい？", value="自分の意見に固執せず、みんなを巻き込める人になりたい")
    else:
        st.caption("現在の葛藤構造、意思決定の癖、および変容への不都合（Immunity to Change）を掘り下げます。")
        adt_q1 = st.text_area("Q1.【現象】最近の仕事や人間関係で、最もモヤモヤした事や葛藤した出来事は何ですか？", value="チームの提案を出したのに反対された")
        adt_q2 = st.text_area("Q2.【価値観・ルール】その時、自分の中のどんな「譲れない信念や個人的なルール」が脅かされたと感じましたか？", value="成果を出すためにどんどん変えるべき")
        adt_q3 = st.text_area("Q3.【行動パターン】その葛藤に対して、あなた自身は相手や周囲にどんな対応や行動を取りましたか？", value="表面上は合わせて引き下がったが内心がっかりした")
        adt_q4 = st.text_area("Q4.【裏の目標・恐れ】もしその信念を緩めて歩み寄った場合、どんな恐れやリスクが生じると思いますか？", value="軸がないと思われたり、成果が出なくなるのが怖い")
        adt_q5 = st.text_area("Q5.【認知の軸】周囲の期待を優先するか、自分の信念を優先するか、普段どちらの傾斜が強いですか？", value="自分の信念を優先しがち")
        adt_q6 = st.text_area("Q6.【変容の兆候】今後、こうした葛藤を乗り越えて、自分自身がどう変化・成長していきたいですか？", value="自分の意見に固執せず、みんなを巻き込める人になりたい")

    submitted = st.form_submit_button("🚀 診断結果を送信して VIA-ADT 統合レポートを生成する", type="primary")

# ---------------------------------------------------------
# 5. 集計 ＆ Gemini API レポート生成
# ---------------------------------------------------------
if submitted:
    if not api_key:
        st.error("⚠️ 左側のサイドバーに Gemini API Key を入力してください。")
        st.stop()

    adt_answers = [adt_q1, adt_q2, adt_q3, adt_q4, adt_q5, adt_q6]
    if any(not q.strip() for q in adt_answers):
        st.warning("⚠️ 内省質問（Q1〜Q6）をすべて入力してください。")
        st.stop()

    # 集計
    strength_scores = defaultdict(list)
    for q in active_questions:
        strength_scores[q["strength"]].append(answers[q["id"]])

    avg_scores = {s: sum(scores) / len(scores) for s, scores in strength_scores.items()}
    sorted_strengths = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

    top5 = sorted_strengths[:5]
    bottom2 = sorted_strengths[-2:]

    st.markdown("---")
    st.header(f"📊 {user_name} さんの診断結果サマリー")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 あなたの光る強み (Top 5)")
        for rank, (s_name, score) in enumerate(top5, 1):
            st.write(f"**第 {rank} 位：{s_name}** （スコア: {score:.1f} / 5.0）")

    with col2:
        st.subheader("🌱 これからの伸びしろ (Bottom 2)")
        for rank, (s_name, score) in enumerate(bottom2, len(sorted_strengths)-1):
            st.write(f"**第 {rank} 位：{s_name}** （スコア: {score:.1f} / 5.0）")

    # プロンプト設計
    tone_instruction = """
- 全体として専門用語を極力使わず、親しみやすく温かい「伴走者」のような言葉遣いで書いてください。
- 難しい心理学用語（Subject/Object、Immunity to Changeなど）は「心のクセ」「お守り」「防衛反応」など分かりやすい言葉に噛み砕いて説明してください。
""" if "カジュアル" in mode else """
- 成人発達理論およびVIAの学術・コーチング的知見に基づき、深く洞察に満ちた構造的な記述を徹底してください。
- エグゼクティブ・コーチとしてプロフェッショナルかつ説得力のあるトーンを保持してください。
"""

    prompt_content = f"""
# 役割定義
あなたは「成人発達理論（ADT）」と「VIA（24の強み）」を統合した優秀なコーチです。
クライアントの強みデータと6つの内省回答に基づき、深層的な気づきを与える『VIA-ADT 統合変容レポート』を作成してください。

# トーン＆表現指示
{tone_instruction}

# 【絶対遵守ルール】
1. 「評価・格付け」の排除: クライアントを「低い」「下がった」「未熟」と評価する表現は厳禁。発達段階は「状況による心のゆらぎ」として表現すること。
2. 防衛反応の受容: 葛藤やモヤモヤは、心を守るための正常なメカニズム（心の防衛力）としてねぎらいと承認をベースに書くこと。
3. 強みの光と影: 現在の悩みは、強みを一所懸命発揮したからこそ生じている「光と影」としてポジティブに捉え直すこと。

# 【入力データ】
■ お名前: {user_name} 様
■ トーン設定: {mode}
■ 強み Top 5: {', '.join([f"{s[0]}({s[1]:.1f})" for s in top5])}
■ 伸びしろ: {', '.join([f"{s[0]}({s[1]:.1f})" for s in bottom2])}
■ 内省回答:
- Q1.出来事: {adt_q1}
- Q2.こだわり: {adt_q2}
- Q3.とった行動: {adt_q3}
- Q4.心の裏の不安: {adt_q4}
- Q5.いつものクセ: {adt_q5}
- Q6.なりたい自分: {adt_q6}

# レポート構成
## 1. はじめに（サマリー）
## 2. あなたの今の「心のものの見方（発達の視点）」
## 3. あなたの強み（Top 5）の活躍と「ちょっとした落とし穴」
## 4. これからの伸びしろポイント
## 5. 次のステップへ進むための3つのヒント
"""

    st.markdown("---")
    st.header("📄 VIA-ADT 統合解析レポート")

    client = genai.Client(api_key=api_key)

    def generate_report():
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt_content,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    with st.spinner("AIがレポートを作成中..."):
        st.write_stream(generate_report)