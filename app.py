import streamlit as st
import streamlit.components.v1 as components
import base64
import anthropic

st.set_page_config(
    page_title="😤 상사 처단 센터",
    page_icon="😤",
    layout="centered",
    initial_sidebar_state="collapsed",
)

PASSWORD = "BKU1010"

# ── 다크 테마 CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700&display=swap');

[data-testid="stAppViewContainer"] { background: #1a0a0a !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
section[data-testid="stSidebar"] { background: #2a1010; }
h1, h2, h3, p, label, .stMarkdown { color: #f5e6e6 !important; }

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    background: #2a1010;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #3a1818;
}
.stTabs [data-baseweb="tab"] {
    color: #c49a9a !important;
    background: transparent !important;
    border-radius: 7px;
    font-family: 'Noto Sans KR', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: #ff4444 !important;
    color: #fff !important;
    font-weight: 700;
}

/* 입력 필드 */
input[type="text"], input[type="password"], textarea {
    background: #2a1010 !important;
    color: #f5e6e6 !important;
    border: 1px solid #553333 !important;
    border-radius: 8px !important;
}
input:focus, textarea:focus {
    border-color: #ff4444 !important;
    box-shadow: 0 0 0 1px #ff4444 !important;
}

/* 버튼 */
.stButton > button[kind="primary"] {
    background: #ff4444 !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Black Han Sans', sans-serif !important;
    letter-spacing: 2px;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    transition: all 0.2s;
}
.stButton > button[kind="primary"]:hover {
    background: #A32D2D !important;
    transform: scale(1.02);
}
.stButton > button[kind="secondary"] {
    background: #2a1010 !important;
    color: #c49a9a !important;
    border: 1px solid #553333 !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #ff4444 !important;
    color: #f5e6e6 !important;
}

/* 파일 업로더 */
[data-testid="stFileUploader"] {
    background: #2a1010;
    border: 2px dashed #553333;
    border-radius: 16px;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover { border-color: #ff4444; }

/* 채팅 */
[data-testid="stChatMessage"] {
    background: #2a1010 !important;
    border: 1px solid #3a1818;
    border-radius: 12px;
}
[data-testid="stChatMessageContent"] { color: #f5e6e6 !important; }
[data-testid="stChatInput"] textarea {
    background: #2a1010 !important;
    color: #f5e6e6 !important;
    border: 1px solid #553333 !important;
}

/* 경고·정보 박스 */
[data-testid="stAlert"] { background: #2a1010 !important; border-color: #553333 !important; }

/* 구분선 */
hr { border-color: #3a1818 !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# 비밀번호 게이트
# ════════════════════════════════════════
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 0 2rem;">
      <div style="font-size:5rem; margin-bottom:1rem;">😤</div>
      <h1 style="font-family:'Black Han Sans',sans-serif; color:#ff4444;
                 font-size:2.2rem; letter-spacing:3px; margin-bottom:0.5rem;">
        상사 처단 센터
      </h1>
      <p style="color:#c49a9a;">직장인의 마음의 평화를 위한 가상 스트레스 해소 공간</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        pw = st.text_input(
            "비밀번호",
            type="password",
            placeholder="🔐 비밀번호 입력...",
            label_visibility="collapsed",
        )
        if st.button("🚪 입장하기", use_container_width=True, type="primary"):
            if pw == PASSWORD:
                st.session_state.auth = True
                st.rerun()
            elif pw:
                st.error("❌ 비밀번호가 틀렸습니다")
    st.stop()

# ════════════════════════════════════════
# 세션 상태 초기화
# ════════════════════════════════════════
# secrets.toml에서 API 키 자동 로드
_default_api_key = st.secrets.get("anthropic_api_key", "") if hasattr(st, "secrets") else ""

for k, v in {
    "boss_name": "",
    "boss_title": "",
    "boss_img_b64": None,
    "chat_history": [],
    "api_key": _default_api_key,
    "game_ready": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════
# 헤더
# ════════════════════════════════════════
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 0.5rem; border-bottom: 1px solid #3a1818; margin-bottom:1rem;">
      <h1 style="font-family:'Black Han Sans',sans-serif; color:#ff4444;
                 font-size:2.2rem; letter-spacing:2px;
                 text-shadow: 0 0 30px rgba(255,68,68,0.35); margin:0;">
        😤 상사 처단 센터
      </h1>
      <p style="color:#c49a9a; font-size:0.9rem; margin-top:0.4rem;">
        직장인의 마음의 평화를 위한 가상 스트레스 해소 공간
      </p>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.markdown("<div style='padding-top:1.2rem;'>", unsafe_allow_html=True)
    if st.button("🚪 로그아웃", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════
# 탭
# ════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["👤 상사 설정", "🔥 고문하기", "💬 대화하기"])

# ────────────────────────────────────────
# TAB 1 — 상사 설정
# ────────────────────────────────────────
with tab1:
    st.divider()

    st.markdown("#### 📸 상사 얼굴 사진")
    uploaded = st.file_uploader(
        "상사 얼굴",
        type=["jpg", "jpeg", "png", "gif", "webp"],
        label_visibility="collapsed",
    )
    if uploaded:
        img_bytes = uploaded.read()
        b64 = base64.b64encode(img_bytes).decode()
        st.session_state.boss_img_b64 = f"data:{uploaded.type};base64,{b64}"

    if st.session_state.boss_img_b64:
        st.image(st.session_state.boss_img_b64, width=90)

    st.markdown("#### 📝 상사 정보")
    col1, col2 = st.columns(2)
    with col1:
        name_in = st.text_input(
            "상사 이름 (별명 가능)",
            placeholder="예: 이 과장, 찐따 팀장...",
            max_chars=20,
            value=st.session_state.boss_name,
        )
    with col2:
        title_in = st.text_input(
            "직급 / 특징",
            placeholder="예: 매일 야근 강요하는 꼰대...",
            max_chars=40,
            value=st.session_state.boss_title,
        )

    st.session_state.boss_name = name_in
    st.session_state.boss_title = title_in

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 분풀이 시작하기", use_container_width=True, type="primary"):
        st.session_state.boss_name = name_in or "이 과장"
        st.session_state.boss_title = title_in or "직장 원수"
        st.session_state.game_ready = True
        st.session_state.chat_history = []

    if st.session_state.game_ready:
        st.markdown("""
        <div style="background:#2a1010;border:1px solid #ff4444;border-radius:12px;
                    padding:1rem;text-align:center;margin-top:1rem;">
          <span style="color:#ff4444;font-size:1.1rem;font-weight:700;">
            ✅ 설정 완료!
          </span>
          <br>
          <span style="color:#c49a9a;font-size:.9rem;">
            위의 <b style="color:#ff4444;">🔥 고문하기</b> 탭이나
            <b style="color:#ff4444;">💬 대화하기</b> 탭을 클릭하세요
          </span>
        </div>
        """, unsafe_allow_html=True)

# ────────────────────────────────────────
# TAB 2 — 고문하기 (embedded HTML)
# ────────────────────────────────────────
with tab2:
    if not st.session_state.game_ready:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#c49a9a;">
          <div style="font-size:3rem">👆</div>
          <p>먼저 <b>상사 설정</b> 탭에서 상사를 등록하고<br>
          <b>분풀이 시작하기</b>를 눌러주세요!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        boss_name_safe = st.session_state.boss_name.replace("'", "\\'").replace("`", "\\`")
        img_data = st.session_state.boss_img_b64 or ""
        img_html = f'<img src="{img_data}" alt="{boss_name_safe}">' if img_data else "😈"

        game_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  :root{{
    --red:#E24B4A;--red-dark:#A32D2D;--amber:#EF9F27;
    --bg:#1a0a0a;--surface:#2a1010;--surface2:#3a1818;
    --text:#f5e6e6;--text-muted:#c49a9a;--accent:#ff4444;
  }}
  body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);padding:.8rem;}}
  .relief-meter{{display:flex;gap:.7rem;width:100%;margin-bottom:.7rem;}}
  .relief-card{{flex:1;background:var(--surface);border-radius:12px;padding:.8rem;text-align:center;border:1px solid #3a1818;}}
  .relief-card .val{{font-family:'Black Han Sans',sans-serif;font-size:1.5rem;color:var(--accent);}}
  .relief-card .lbl{{font-size:.75rem;color:var(--text-muted);margin-top:.2rem;}}
  .stress-bar-wrap{{width:100%;background:var(--surface);border-radius:12px;padding:1rem;display:flex;align-items:center;gap:1rem;margin-bottom:.7rem;}}
  .stress-label{{font-size:.85rem;color:var(--text-muted);min-width:80px;}}
  .stress-bar-bg{{flex:1;height:20px;background:#3a1818;border-radius:10px;overflow:hidden;}}
  .stress-bar-fill{{height:100%;border-radius:10px;background:linear-gradient(90deg,var(--amber),var(--accent));transition:width .3s;width:0%;}}
  .stress-val{{font-family:'Black Han Sans',sans-serif;font-size:1.1rem;color:var(--accent);min-width:50px;text-align:right;}}
  .boss-name-display{{font-family:'Black Han Sans',sans-serif;font-size:1rem;color:var(--accent);text-align:center;margin-bottom:.3rem;}}
  .boss-display{{position:relative;width:200px;height:200px;display:flex;align-items:center;justify-content:center;margin:0 auto .7rem;}}
  .boss-face{{width:160px;height:160px;border-radius:50%;background:var(--surface2);border:4px solid var(--accent);display:flex;align-items:center;justify-content:center;font-size:5rem;overflow:hidden;cursor:pointer;transition:transform .1s;position:relative;z-index:2;user-select:none;}}
  .boss-face img{{width:100%;height:100%;object-fit:cover;pointer-events:none;}}
  .boss-face:active{{transform:scale(.88);}}
  .hit-effect{{position:absolute;font-size:2rem;font-weight:900;color:var(--accent);pointer-events:none;animation:hitAnim .6s forwards;z-index:10;}}
  @keyframes hitAnim{{
    0%{{opacity:1;transform:scale(.5) translateY(0);}}
    50%{{opacity:1;transform:scale(1.3) translateY(-20px);}}
    100%{{opacity:0;transform:scale(1) translateY(-50px);}}
  }}
  .boss-reaction{{background:var(--surface);border-radius:12px;padding:.8rem 1.2rem;font-size:1rem;text-align:center;border-left:3px solid var(--accent);min-height:50px;width:100%;display:flex;align-items:center;justify-content:center;margin-bottom:.7rem;}}
  .tools-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem;width:100%;}}
  .tool-btn{{background:var(--surface);border:1px solid #553333;border-radius:12px;padding:.8rem .5rem;cursor:pointer;text-align:center;transition:all .15s;color:var(--text);}}
  .tool-btn:hover{{background:var(--surface2);border-color:var(--accent);transform:scale(1.05);}}
  .tool-btn:active{{transform:scale(.95);}}
  .tool-icon{{font-size:1.8rem;display:block;}}
  .tool-name{{font-size:.75rem;color:var(--text-muted);margin-top:.2rem;}}
  @keyframes shakeAnim{{
    0%,100%{{transform:translateX(0) rotate(0);}}
    20%{{transform:translateX(-8px) rotate(-3deg);}}
    40%{{transform:translateX(8px) rotate(3deg);}}
    60%{{transform:translateX(-5px) rotate(-2deg);}}
    80%{{transform:translateX(5px) rotate(2deg);}}
  }}
  .shake{{animation:shakeAnim .3s ease-in-out;}}
  .game-arena{{display:flex;flex-direction:column;align-items:center;gap:.7rem;}}
</style>
</head>
<body>
<div class="game-arena">
  <div class="relief-meter">
    <div class="relief-card"><div class="val" id="hitCount">0</div><div class="lbl">총 타격 수</div></div>
    <div class="relief-card"><div class="val" id="comboCount">0</div><div class="lbl">콤보</div></div>
    <div class="relief-card"><div class="val" id="reliefScore">0%</div><div class="lbl">스트레스 해소</div></div>
  </div>
  <div class="stress-bar-wrap">
    <span class="stress-label">😤 스트레스</span>
    <div class="stress-bar-bg"><div class="stress-bar-fill" id="stressBar"></div></div>
    <span class="stress-val" id="stressVal">0</span>
  </div>
  <div class="boss-name-display">😈 {boss_name_safe}</div>
  <div class="boss-display" id="bossDisplay">
    <div class="boss-face" id="bossFace" onclick="hitBoss()">{img_html}</div>
  </div>
  <div class="boss-reaction" id="bossReaction">클릭해서 타격하거나 아래 도구를 사용하세요!</div>
  <div class="tools-grid">
    <div class="tool-btn" onclick="useTool('slap',this)"><span class="tool-icon">👋</span><span class="tool-name">따귀</span></div>
    <div class="tool-btn" onclick="useTool('water',this)"><span class="tool-icon">💦</span><span class="tool-name">물벼락</span></div>
    <div class="tool-btn" onclick="useTool('pillow',this)"><span class="tool-icon">🪣</span><span class="tool-name">돌직구</span></div>
    <div class="tool-btn" onclick="useTool('scream',this)"><span class="tool-icon">📢</span><span class="tool-name">귓방망이</span></div>
    <div class="tool-btn" onclick="useTool('ink',this)"><span class="tool-icon">🖊️</span><span class="tool-name">볼펜세례</span></div>
    <div class="tool-btn" onclick="useTool('memo',this)"><span class="tool-icon">📋</span><span class="tool-name">보고서 던지기</span></div>
    <div class="tool-btn" onclick="useTool('coffee',this)"><span class="tool-icon">☕</span><span class="tool-name">커피 붓기</span></div>
    <div class="tool-btn" onclick="useTool('resign',this)"><span class="tool-icon">📄</span><span class="tool-name">사직서 투척</span></div>
  </div>
</div>
<script>
let hits=0,combo=0,stressRelief=0,comboTimer=null;
const toolReactions={{
  slap:['아야!! 이게 무슨..!','감히 나한테!!','으으으... 이 직원이...','야!! 너 내일부터 나와!!'],
  water:['꺄악!! 옷이!!!!','이, 이거 세탁비 물어내!!','내 정장이!!!! 정장!!!'],
  pillow:['윽!! 정통으로 맞았다!','이게 날아오네?!','어지러워...'],
  scream:['귀가 찢어져!!','으아아아!!','이 귓청이 얼마짜리인 줄 알아!'],
  ink:['내 셔츠에 잉크가!!','이거 얼마짜리 셔츠인지 알아?!','으아 지워지지도 않잖아!!'],
  memo:['보고서에 맞았어!!','야!! 이 보고서 다시 써 와!!'],
  coffee:['뜨거워!! 뜨거워!!','카피 값 물어내!!','아 내 커피... 아까워...'],
  resign:['사직서?! 야!! 이리 와봐!!','배은망덕한 놈!!','흥! 나가!! 나가라고!!','...사실 나도 그러고 싶다']
}};
const hitEmojis=['💥','⚡','🔥','💢','😤','👊','💫'];
function hitBoss(){{
  hits++;combo++;
  clearTimeout(comboTimer);
  comboTimer=setTimeout(()=>{{combo=0;updateStats();}},1500);
  stressRelief=Math.min(100,stressRelief+(combo>=5?3:2));
  updateStats();
  const r=['아야!!','이게!!','으으!!','윽!!','감히!!','살려줘!!','으아악!'];
  document.getElementById('bossReaction').textContent=r[Math.floor(Math.random()*r.length)];
  shakeAndSpark(1);
}}
function useTool(tool,btn){{
  const arr=toolReactions[tool];
  document.getElementById('bossReaction').textContent=arr[Math.floor(Math.random()*arr.length)];
  hits+=3;combo+=2;stressRelief=Math.min(100,stressRelief+5);
  clearTimeout(comboTimer);
  comboTimer=setTimeout(()=>{{combo=0;updateStats();}},2000);
  updateStats();shakeAndSpark(2);
  btn.style.transform='scale(0.9)';
  setTimeout(()=>btn.style.transform='',150);
}}
function shakeAndSpark(n){{
  const face=document.getElementById('bossFace');
  face.classList.remove('shake');void face.offsetWidth;face.classList.add('shake');
  setTimeout(()=>face.classList.remove('shake'),350);
  for(let i=0;i<n;i++)spawnHit();
}}
function spawnHit(){{
  const display=document.getElementById('bossDisplay');
  const el=document.createElement('div');
  el.className='hit-effect';
  el.textContent=hitEmojis[Math.floor(Math.random()*hitEmojis.length)];
  el.style.left=(15+Math.random()*65)+'%';
  el.style.top=(5+Math.random()*45)+'%';
  display.appendChild(el);setTimeout(()=>el.remove(),650);
}}
function updateStats(){{
  document.getElementById('hitCount').textContent=hits;
  document.getElementById('comboCount').textContent=combo>1?combo+'x':combo;
  document.getElementById('reliefScore').textContent=stressRelief+'%';
  document.getElementById('stressBar').style.width=stressRelief+'%';
  document.getElementById('stressVal').textContent=stressRelief;
}}
</script>
</body>
</html>"""
        components.html(game_html, height=620, scrolling=False)

# ────────────────────────────────────────
# TAB 3 — 대화하기 (native Streamlit streaming)
# ────────────────────────────────────────
with tab3:
    if not st.session_state.game_ready:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#c49a9a;">
          <div style="font-size:3rem">👆</div>
          <p>먼저 <b>상사 설정</b> 탭에서 상사를 등록하고<br>
          <b>분풀이 시작하기</b>를 눌러주세요!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 채팅 헤더
        col_img, col_info, col_badge = st.columns([1, 4, 2])
        with col_img:
            if st.session_state.boss_img_b64:
                st.markdown(
                    f'<img src="{st.session_state.boss_img_b64}" '
                    'style="width:50px;height:50px;border-radius:50%;'
                    'border:2px solid #ff4444;object-fit:cover;">',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div style="font-size:2.5rem">😈</div>', unsafe_allow_html=True)
        with col_info:
            st.markdown(
                f'<b style="color:#f5e6e6;">{st.session_state.boss_name}</b><br>'
                f'<span style="color:#c49a9a;font-size:.8rem;">{st.session_state.boss_title}</span>',
                unsafe_allow_html=True,
            )
        with col_badge:
            st.markdown(
                '<span style="background:#2a1010;border:1px solid #ff4444;'
                'border-radius:20px;padding:.3rem .8rem;color:#ff4444;font-size:.8rem;">'
                '😤 빡침 상태</span>',
                unsafe_allow_html=True,
            )

        st.divider()

        if not st.session_state.api_key:
            st.warning("💡 **상사 설정** 탭에서 Anthropic API 키를 입력해야 대화가 가능합니다.")

        # 빠른 메시지 버튼
        QUICK = [
            ("야근 왜 나만?",   "야근 왜 항상 나만 해요?"),
            ("공 가로채기",     "제 아이디어 왜 맨날 본인 공으로 돌려요?"),
            ("월급 올려줘",     "월급 올려주세요"),
            ("스트레스 폭발",   "당신 때문에 스트레스 폭발했잖아요!"),
            ("사직서 쓰고파",   "저 사직서 쓰고 싶어요"),
            ("따져볼게요",      "진짜 너무한 거 아니에요? 제대로 따져볼게요"),
            ("보고서 또요?",    "왜 맨날 보고서 다시 쓰라는 거예요?"),
            ("말 왜 끊어요",    "회의 중에 제 말 왜 자꾸 끊어요?"),
        ]
        q_cols = st.columns(4)
        for i, (label, full_msg) in enumerate(QUICK):
            with q_cols[i % 4]:
                if st.button(label, key=f"q{i}", use_container_width=True):
                    st.session_state._pending = full_msg

        st.markdown("<br>", unsafe_allow_html=True)

        # 기존 대화 표시
        if not st.session_state.chat_history:
            with st.chat_message("assistant", avatar="😈"):
                st.write("...(상사가 뚱한 표정으로 앉아있다)")

        for msg in st.session_state.chat_history:
            role = msg["role"]
            avatar = "😈" if role == "assistant" else "🧑‍💼"
            with st.chat_message(role, avatar=avatar):
                st.write(msg["content"])

        # 사용자 입력 받기 (텍스트 입력 or 빠른 메시지)
        user_input = st.chat_input("하고 싶은 말 마음껏 털어놓으세요... ✍️")

        pending = st.session_state.pop("_pending", None) if "_pending" in st.session_state else None
        msg_to_send = pending or user_input

        if msg_to_send:
            if not st.session_state.api_key:
                st.error("❌ 상사 설정 탭에서 API 키를 먼저 입력해주세요!")
            else:
                with st.chat_message("user", avatar="🧑‍💼"):
                    st.write(msg_to_send)
                st.session_state.chat_history.append({"role": "user", "content": msg_to_send})

                system_prompt = (
                    f'당신은 "{st.session_state.boss_name}"이라는 상사 캐릭터입니다. '
                    f'직급/특징: "{st.session_state.boss_title}".\n'
                    "당신은 전형적인 한국 꼰대 상사로 직원들에게 억압적이고 부당하게 대했습니다.\n"
                    "지금 직원이 화풀이를 하러 왔습니다.\n"
                    "- 처음엔 권위적으로 반응하다가 점점 당황하거나 변명하거나 꼬리내리세요\n"
                    "- 가끔 잘못을 인정하는 척하다가 다시 변명하세요\n"
                    "- 욕설은 직접 쓰지 않되 빈정대거나 불쾌한 말을 하세요\n"
                    "- 1-3문장으로 짧고 임팩트 있게 한국어로 답하세요"
                )

                def stream_boss():
                    client = anthropic.Anthropic(api_key=st.session_state.api_key)
                    with client.messages.stream(
                        model="claude-sonnet-4-6",
                        max_tokens=300,
                        system=system_prompt,
                        messages=st.session_state.chat_history,
                    ) as stream:
                        for text in stream.text_stream:
                            yield text

                with st.chat_message("assistant", avatar="😈"):
                    try:
                        response_text = st.write_stream(stream_boss())
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response_text}
                        )
                    except Exception as e:
                        fallbacks = [
                            "야!! 나한테 그런 말 하면 어떡해!!",
                            "...그, 그건 내가 좀 심했나... 어쨌든 네 탓이야!!",
                            "흥!! 말도 안 돼!! 보고서나 다시 써!!",
                            "그래도 상사한테... 어, 어어... 할 말 없네.",
                        ]
                        import random
                        fallback = random.choice(fallbacks)
                        st.write(fallback)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": fallback}
                        )
                        st.caption(f"⚠️ API 오류: {e}")
