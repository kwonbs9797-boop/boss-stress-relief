import streamlit as st
import streamlit.components.v1 as components
import base64
import anthropic
import random

st.set_page_config(
    page_title="👹 데빌 헌터스",
    page_icon="👹",
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
      <div style="font-size:5rem; margin-bottom:1rem;">👹</div>
      <h1 style="font-family:'Black Han Sans',sans-serif; color:#ff4444;
                 font-size:2.4rem; letter-spacing:4px; margin-bottom:0.5rem;">
        데빌 헌터스
      </h1>
      <p style="color:#c49a9a; font-size:.9rem;">악마를 사냥하고 스트레스를 날려버려라</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        pw = st.text_input(
            "비밀번호",
            type="password",
            placeholder="🔑 헌터 코드 입력...",
            label_visibility="collapsed",
        )
        if st.button("⚔️ 사냥 시작", use_container_width=True, type="primary"):
            if pw == PASSWORD:
                st.session_state.auth = True
                st.rerun()
            elif pw:
                st.error("❌ 헌터 코드가 틀렸습니다")
    st.stop()

# ════════════════════════════════════════
# API 키 — secrets에서 직접 읽기 (세션 무관)
# ════════════════════════════════════════
def get_api_key():
    try:
        return st.secrets["anthropic_api_key"]
    except Exception:
        return ""

# ════════════════════════════════════════
# 세션 상태 초기화
# ════════════════════════════════════════
for k, v in {
    "boss_name": "",
    "boss_title": "",
    "boss_img_b64": None,
    "chat_history": [],
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
                 font-size:2.2rem; letter-spacing:3px;
                 text-shadow: 0 0 30px rgba(255,68,68,0.35); margin:0;">
        👹 데빌 헌터스
      </h1>
      <p style="color:#c49a9a; font-size:0.9rem; margin-top:0.4rem;">
        악마를 사냥하고 스트레스를 날려버려라
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
tab1, tab2, tab3 = st.tabs(["👹 악마 등록", "⚔️ 사냥하기", "💬 도발하기"])

# ────────────────────────────────────────
# TAB 1 — 상사 설정
# ────────────────────────────────────────
with tab1:
    st.divider()

    st.markdown("#### 📸 악마 사진 등록")
    uploaded = st.file_uploader(
        "악마 사진",
        type=["jpg", "jpeg", "png", "gif", "webp"],
        label_visibility="collapsed",
    )
    if uploaded:
        img_bytes = uploaded.read()
        b64 = base64.b64encode(img_bytes).decode()
        st.session_state.boss_img_b64 = f"data:{uploaded.type};base64,{b64}"

    if st.session_state.boss_img_b64:
        st.image(st.session_state.boss_img_b64, width=90)

    st.markdown("#### 📝 악마 정보")
    col1, col2 = st.columns(2)
    with col1:
        name_in = st.text_input(
            "악마 이름 (별명 가능)",
            placeholder="예: 이 과장, 야근 강요 마귀...",
            max_chars=20,
            value=st.session_state.boss_name,
        )
    with col2:
        title_in = st.text_input(
            "악마 특성",
            placeholder="예: 매일 야근 강요하는 꼰대...",
            max_chars=40,
            value=st.session_state.boss_title,
        )

    st.session_state.boss_name = name_in
    st.session_state.boss_title = title_in

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚔️ 사냥 시작하기", use_container_width=True, type="primary"):
        st.session_state.boss_name = name_in or "야근 악마"
        st.session_state.boss_title = title_in or "직장 원수"
        st.session_state.game_ready = True
        st.session_state.chat_history = []

    if st.session_state.game_ready:
        st.markdown("""
        <div style="background:#2a1010;border:1px solid #ff4444;border-radius:12px;
                    padding:1rem;text-align:center;margin-top:1rem;">
          <span style="color:#ff4444;font-size:1.1rem;font-weight:700;">
            ✅ 악마 등록 완료!
          </span>
          <br>
          <span style="color:#c49a9a;font-size:.9rem;">
            위의 <b style="color:#ff4444;">⚔️ 사냥하기</b> 탭이나
            <b style="color:#ff4444;">💬 도발하기</b> 탭을 클릭하세요
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
          <p>먼저 <b>악마 등록</b> 탭에서 악마를 등록하고<br>
          <b>사냥 시작하기</b>를 눌러주세요!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        boss_name_safe = (st.session_state.boss_name or "최종 보스").replace("'","\\'").replace("`","\\`")
        img_data = st.session_state.boss_img_b64 or ""
        boss_img_css = f'background-image:url("{img_data}");background-size:cover;background-position:center;' if img_data else ""

        game_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Noto Sans KR',sans-serif;background:#1a0e2e;color:#f0eaff;padding:.7rem;overflow-x:hidden;}}

/* ── 월드 ── */
.world{{
  position:relative;width:100%;height:260px;border-radius:16px;overflow:hidden;
  border:3px solid #c89820;box-shadow:0 4px 24px rgba(200,152,32,.3);
  margin-bottom:.7rem;
}}
.sky{{
  position:absolute;inset:0;
  background:linear-gradient(180deg,#1a3a6b 0%,#2a5fa0 40%,#4a8fd4 65%,#6aafe4 72%);
}}
/* 구름 */
.cloud{{position:absolute;background:rgba(255,255,255,.85);border-radius:50px;}}
.cloud::before,.cloud::after{{content:'';position:absolute;background:rgba(255,255,255,.85);border-radius:50%;}}
.c1{{width:70px;height:22px;top:18%;left:5%;animation:drift 18s linear infinite;}}
.c1::before{{width:32px;height:32px;top:-14px;left:10px;}}
.c1::after{{width:24px;height:24px;top:-10px;left:34px;}}
.c2{{width:55px;height:18px;top:12%;left:40%;animation:drift 25s linear infinite 5s;}}
.c2::before{{width:26px;height:26px;top:-12px;left:8px;}}
.c2::after{{width:20px;height:20px;top:-8px;left:28px;}}
.c3{{width:80px;height:24px;top:22%;left:70%;animation:drift 20s linear infinite 10s;}}
.c3::before{{width:36px;height:36px;top:-16px;left:12px;}}
.c3::after{{width:26px;height:26px;top:-12px;left:40px;}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-110vw)}}}}

/* 배경 나무 */
.bg-trees{{
  position:absolute;bottom:28%;left:0;right:0;
  font-size:2.2rem;letter-spacing:4px;opacity:.5;
  text-align:left;padding-left:4px;pointer-events:none;
}}

/* 땅 */
.ground{{
  position:absolute;bottom:0;left:0;right:0;height:28%;
  background:linear-gradient(180deg,#5aaf32 0%,#3d8a1e 25%,#2d6a16 100%);
}}
.ground::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:7px;
  background:linear-gradient(90deg,#6dd43a 0%,#7ee844 50%,#6dd43a 100%);
  border-radius:3px;
}}
/* 잔디 블록 패턴 */
.ground::after{{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:repeating-linear-gradient(90deg,transparent,transparent 40px,rgba(0,0,0,.06) 40px,rgba(0,0,0,.06) 41px);
}}

/* ── 플레이어 ── */
.player{{
  position:absolute;bottom:28%;left:30px;
  font-size:3rem;z-index:10;
  filter:drop-shadow(2px 4px 4px rgba(0,0,0,.5));
  animation:idle 1s ease-in-out infinite;
  transform-origin:bottom center;
  transition:left .25s ease;
  cursor:default;user-select:none;
}}
@keyframes idle{{0%,100%{{transform:translateY(0) scaleY(1);}}50%{{transform:translateY(-5px) scaleY(1.04);}}}}
.player.attack{{animation:lunge .35s ease forwards;}}
@keyframes lunge{{
  0%{{transform:translateX(0) scaleX(1);}}
  45%{{transform:translateX(90px) scaleX(1.15) scaleY(.9);}}
  70%{{transform:translateX(75px) scaleX(.9) scaleY(1.05);}}
  100%{{transform:translateX(0) scaleX(1);}}
}}

/* ── 몬스터 영역 ── */
.monster-zone{{
  position:absolute;bottom:28%;right:40px;
  display:flex;flex-direction:column;align-items:center;z-index:10;
}}
.m-hp-outer{{
  width:110px;height:10px;background:rgba(0,0,0,.6);
  border-radius:5px;overflow:hidden;margin-bottom:3px;
  border:1px solid rgba(255,255,255,.25);
}}
.m-hp-fill{{
  height:100%;border-radius:5px;
  background:linear-gradient(90deg,#ef4444,#ff6b6b);
  transition:width .2s;
}}
.m-name{{
  color:#fff;font-size:.62rem;font-weight:700;
  text-shadow:1px 1px 3px #000;margin-bottom:3px;letter-spacing:1px;
}}
.m-sprite{{
  font-size:4rem;cursor:pointer;user-select:none;
  filter:drop-shadow(0 4px 8px rgba(0,0,0,.6));
  animation:mbob 1.2s ease-in-out infinite;
  transition:transform .08s;
}}
.m-sprite:active{{transform:scale(.82);}}
@keyframes mbob{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-9px);}}}}
.m-sprite.hit{{animation:mhit .35s ease;}}
@keyframes mhit{{
  0%,100%{{transform:translateX(0);filter:drop-shadow(0 4px 8px rgba(0,0,0,.6));}}
  25%{{transform:translateX(14px);filter:drop-shadow(0 0 18px #ff4444) brightness(2.2);}}
  55%{{transform:translateX(-9px);filter:drop-shadow(0 0 12px #ff8888);}}
  75%{{transform:translateX(6px);}}
}}

/* 보스 이미지 모드 */
.m-sprite.boss-img{{
  width:90px;height:90px;border-radius:50%;
  border:3px solid #dc2626;
  box-shadow:0 0 24px rgba(220,38,38,.6);
  overflow:hidden;font-size:0;
  {boss_img_css}
}}

/* 데미지 숫자 */
.dmg{{
  position:absolute;font-family:'Black Han Sans',sans-serif;font-weight:900;
  pointer-events:none;z-index:50;
  text-shadow:2px 2px 0 #000,-1px -1px 0 #000;
  animation:dmgup .9s forwards;
}}
.dmg.n{{font-size:1.4rem;color:#fff;}}
.dmg.c{{font-size:1.9rem;color:#ffdd00;}}
@keyframes dmgup{{
  0%{{opacity:1;transform:translateY(0) scale(.7);}}
  35%{{opacity:1;transform:translateY(-35px) scale(1.25);}}
  100%{{opacity:0;transform:translateY(-75px) scale(.95);}}
}}

/* 드롭 아이템 */
.loot{{
  position:absolute;font-size:1.1rem;pointer-events:none;
  animation:lootfall 1.4s forwards;z-index:25;
}}
@keyframes lootfall{{
  0%{{opacity:1;transform:translateY(-15px) rotate(0);}}
  60%{{opacity:1;transform:translateY(18px) rotate(200deg);}}
  100%{{opacity:0;transform:translateY(28px) rotate(300deg);}}
}}

/* ── 스테이지 뱃지 ── */
.stage-row{{
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:.6rem;
}}
.stage-txt{{
  font-size:.75rem;color:#c89820;letter-spacing:3px;font-weight:700;
}}

/* ── 플레이어 스탯 ── */
.pstat{{
  background:rgba(0,0,0,.6);border:2px solid #c89820;border-radius:12px;
  padding:.55rem 1rem;display:flex;align-items:center;gap:.8rem;
  margin-bottom:.6rem;
}}
.lv-badge{{
  background:linear-gradient(135deg,#b8860b,#ffd700);color:#000;
  font-family:'Black Han Sans',sans-serif;font-size:.85rem;
  padding:.25rem .65rem;border-radius:20px;white-space:nowrap;min-width:48px;text-align:center;
}}
.exp-area{{flex:1;}}
.exp-lbl{{font-size:.6rem;color:#888;margin-bottom:2px;}}
.exp-bg{{height:7px;background:#111;border-radius:4px;overflow:hidden;}}
.exp-fill{{height:100%;background:linear-gradient(90deg,#4ade80,#22d3ee);border-radius:4px;transition:width .5s;}}
.hp-area{{display:flex;flex-direction:column;align-items:flex-end;}}
.hp-lbl{{font-size:.6rem;color:#f87171;margin-bottom:2px;}}
.hp-row{{display:flex;gap:.3rem;font-size:.8rem;}}

/* ── 스탯 박스 ── */
.stats-row{{display:flex;gap:.5rem;margin-bottom:.6rem;}}
.sbox{{
  flex:1;background:rgba(0,0,0,.55);border:1px solid #c89820;
  border-radius:10px;padding:.5rem;text-align:center;
}}
.sval{{font-family:'Black Han Sans',sans-serif;font-size:1.3rem;color:#ffd700;}}
.slbl{{font-size:.65rem;color:#888;margin-top:.1rem;}}

/* ── 몬스터 반응 말풍선 ── */
.say-bubble{{
  background:rgba(0,0,0,.65);border:1px solid #c89820;border-radius:10px;
  padding:.55rem 1rem;text-align:center;font-size:.88rem;color:#f0eaff;
  min-height:38px;display:flex;align-items:center;justify-content:center;
  margin-bottom:.6rem;
}}

/* ── 스킬 ── */
.skills{{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;}}
.sk{{
  background:linear-gradient(135deg,#1a1440,#12102e);
  border:2px solid #c89820;border-radius:12px;
  padding:.6rem .3rem;cursor:pointer;text-align:center;
  transition:all .15s;position:relative;overflow:hidden;
}}
.sk::before{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,215,0,.08),transparent);
}}
.sk:hover{{border-color:#ffd700;transform:scale(1.06);background:linear-gradient(135deg,#2a2460,#1e1c52);}}
.sk:active{{transform:scale(.91);}}
.sk-icon{{font-size:1.6rem;display:block;}}
.sk-name{{font-size:.66rem;color:#ccc;margin-top:.1rem;}}
.sk-dmg{{font-size:.7rem;color:#ffd700;font-weight:700;}}

/* ── 클리어 오버레이 ── */
.clear-ov{{
  display:none;position:absolute;inset:0;
  background:rgba(0,0,0,.78);z-index:100;
  align-items:center;justify-content:center;
  flex-direction:column;gap:.8rem;border-radius:14px;
}}
.clear-ov.show{{display:flex;animation:fi .3s;}}
@keyframes fi{{from{{opacity:0}}to{{opacity:1}}}}
.clear-em{{font-size:4rem;animation:bnc .5s ease-in-out infinite alternate;}}
@keyframes bnc{{from{{transform:translateY(0)}}to{{transform:translateY(-16px)}}}}
.clear-ttl{{
  font-family:'Black Han Sans',sans-serif;font-size:2rem;
  color:#ffd700;letter-spacing:3px;text-shadow:0 0 24px rgba(255,215,0,.7);
}}
.clear-sub{{color:#ccc;font-size:.85rem;}}
.next-btn{{
  background:linear-gradient(135deg,#b8860b,#ffd700);color:#000;
  border:none;border-radius:12px;padding:.65rem 2rem;
  font-family:'Black Han Sans',sans-serif;font-size:1rem;
  cursor:pointer;letter-spacing:2px;transition:all .2s;
}}
.next-btn:hover{{transform:scale(1.06);}}

/* ── 올클리어 ── */
.allclear{{
  display:none;position:fixed;inset:0;
  background:radial-gradient(ellipse at center,#1a0a2e 0%,#0d0a1a 100%);
  z-index:200;align-items:center;justify-content:center;
  flex-direction:column;gap:1rem;text-align:center;
}}
.allclear.show{{display:flex;animation:fi .5s;}}
.ac-stars{{font-size:2.5rem;letter-spacing:.5rem;animation:starSpin 2s ease-in-out infinite;}}
@keyframes starSpin{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.15);}}}}
.ac-title{{
  font-family:'Black Han Sans',sans-serif;font-size:2.8rem;
  color:#ffd700;letter-spacing:5px;
  text-shadow:0 0 30px rgba(255,215,0,.9),0 0 60px rgba(255,215,0,.4);
}}
.ac-score{{font-size:1.1rem;color:#a78bfa;}}
.replay-btn{{
  background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff;
  border:none;border-radius:16px;padding:.9rem 3rem;
  font-family:'Black Han Sans',sans-serif;font-size:1.1rem;
  cursor:pointer;letter-spacing:2px;transition:all .2s;margin-top:.5rem;
}}
.replay-btn:hover{{transform:scale(1.05);}}
</style>
</head>
<body>

<!-- ══ 월드 ══ -->
<div class="world" id="world">
  <div class="sky"></div>
  <div class="cloud c1"></div>
  <div class="cloud c2"></div>
  <div class="cloud c3"></div>
  <div class="bg-trees">🌲🌳🌲🌳🌲🌳🌲🌳</div>
  <div class="ground"></div>

  <!-- 플레이어 -->
  <div class="player" id="player">🧙</div>

  <!-- 몬스터 -->
  <div class="monster-zone" id="monsterZone">
    <div class="m-hp-outer"><div class="m-hp-fill" id="mHpFill" style="width:100%"></div></div>
    <div class="m-name" id="mName">로딩중...</div>
    <div class="m-sprite" id="mSprite" onclick="attack(5)"></div>
  </div>

  <!-- 클리어 오버레이 -->
  <div class="clear-ov" id="clearOv">
    <div class="clear-em" id="clearEm">✨</div>
    <div class="clear-ttl" id="clearTtl">처치!</div>
    <div class="clear-sub" id="clearSub"></div>
    <button class="next-btn" id="nextBtn" onclick="nextMonster()">다음 몬스터 ▶</button>
  </div>
</div>

<!-- ══ 스테이지 ══ -->
<div class="stage-row">
  <span class="stage-txt" id="stageTxt">STAGE 1 / 5</span>
  <span style="font-size:.72rem;color:#888;" id="stageSubTxt"></span>
</div>

<!-- ══ 플레이어 스탯 ══ -->
<div class="pstat">
  <div class="lv-badge" id="lvBadge">Lv.1</div>
  <div class="exp-area">
    <div class="exp-lbl">EXP</div>
    <div class="exp-bg"><div class="exp-fill" id="expFill" style="width:0%"></div></div>
  </div>
  <div class="hp-area">
    <div class="hp-lbl">❤️ HP</div>
    <div class="hp-row"><span id="playerHp" style="color:#f87171;font-weight:700;">100</span><span style="color:#666;">/100</span></div>
  </div>
</div>

<!-- ══ 스탯 ══ -->
<div class="stats-row">
  <div class="sbox"><div class="sval" id="sDmg">0</div><div class="slbl">총 데미지</div></div>
  <div class="sbox"><div class="sval" id="sCombo">0</div><div class="slbl">콤보</div></div>
  <div class="sbox"><div class="sval" id="sKills">0</div><div class="slbl">처치 수</div></div>
</div>

<!-- ══ 말풍선 ══ -->
<div class="say-bubble" id="sayBubble">👆 몬스터를 클릭하거나 스킬을 사용하세요!</div>

<!-- ══ 스킬 ══ -->
<div class="skills">
  <div class="sk" onclick="useSkill(15)"><span class="sk-icon">⚔️</span><span class="sk-name">참격</span><span class="sk-dmg">-15</span></div>
  <div class="sk" onclick="useSkill(25)"><span class="sk-icon">🔥</span><span class="sk-name">화염</span><span class="sk-dmg">-25</span></div>
  <div class="sk" onclick="useSkill(20)"><span class="sk-icon">⚡</span><span class="sk-name">번개</span><span class="sk-dmg">-20</span></div>
  <div class="sk" onclick="useSkill(30)"><span class="sk-icon">❄️</span><span class="sk-name">빙결</span><span class="sk-dmg">-30</span></div>
  <div class="sk" onclick="useSkill(20)"><span class="sk-icon">☄️</span><span class="sk-name">유성</span><span class="sk-dmg">-20</span></div>
  <div class="sk" onclick="useSkill(35)"><span class="sk-icon">💥</span><span class="sk-name">폭발</span><span class="sk-dmg">-35</span></div>
  <div class="sk" onclick="useSkill(25)"><span class="sk-icon">🌪️</span><span class="sk-name">회오리</span><span class="sk-dmg">-25</span></div>
  <div class="sk" onclick="useSkill(50)"><span class="sk-icon">🌟</span><span class="sk-name">필살기</span><span class="sk-dmg">-50</span></div>
</div>

<!-- ══ 올클리어 ══ -->
<div class="allclear" id="allClear">
  <div class="ac-stars">⭐⭐⭐⭐⭐</div>
  <div class="ac-title">ALL CLEAR!</div>
  <div class="ac-score">총 데미지 <span id="acDmg" style="color:#ffd700;font-weight:900;">0</span></div>
  <div style="color:#888;font-size:.85rem;margin-top:-.3rem;">악마 사냥 완전 성공 🎉</div>
  <button class="replay-btn" onclick="initGame()">🔄 다시 하기</button>
</div>

<script>
const BOSS_NAME = '{boss_name_safe}';
const BOSS_IMG_CSS = `{boss_img_css}`;

const MONSTERS = [
  {{ name:'잔업 요괴',    emoji:'🐛', hp:80,  exp:20,  says:['앗뜨거!','왜 때려!','살살 해줘요!','으앗!'] }},
  {{ name:'꼰대 슬라임',  emoji:'🟢', hp:130, exp:35,  says:['뭐하는짓!','이놈!','네 탓이야!','끈적끈적~'] }},
  {{ name:'갑질 도깨비',  emoji:'👹', hp:180, exp:50,  says:['감히!!','아프다!','이 직원이!','야근해!!'] }},
  {{ name:'초과근무 악마',emoji:'👿', hp:260, exp:70,  says:['크하하!','도망 못 가!','야근 각오해!','내가 상사다!'] }},
  {{ name:BOSS_NAME,     emoji:'💀', hp:400, exp:150, says:['크아아!','이럴 수가!','나를 이겨?!','불가능해!'], isBoss:true }},
];

const LOOTS = ['🪙','🪙','🪙','💎','⭐','🎁'];

let stage=0, mHp=0, mMaxHp=0;
let totalDmg=0, combo=0, kills=0;
let playerLv=1, playerExp=0, playerExpMax=100;
let comboTimer=null, locked=false;

function initGame(){{
  document.getElementById('allClear').classList.remove('show');
  stage=0; totalDmg=0; combo=0; kills=0;
  playerLv=1; playerExp=0; playerExpMax=100;
  updatePlayerStat();
  loadMonster();
}}

function loadMonster(){{
  locked=false;
  const m=MONSTERS[stage];
  mHp=m.hp; mMaxHp=m.hp;

  document.getElementById('mName').textContent=m.name;
  document.getElementById('mHpFill').style.width='100%';
  document.getElementById('stageTxt').textContent=`STAGE ${{stage+1}} / ${{MONSTERS.length}}`;
  document.getElementById('stageSubTxt').textContent=`HP ${{m.hp}} | EXP +${{m.exp}}`;
  document.getElementById('sayBubble').textContent='👆 몬스터를 클릭하거나 스킬을 사용하세요!';
  document.getElementById('clearOv').classList.remove('show');

  const sp=document.getElementById('mSprite');
  sp.classList.remove('boss-img');
  if(m.isBoss && BOSS_IMG_CSS){{
    sp.textContent='';
    sp.classList.add('boss-img');
    sp.style.cssText += BOSS_IMG_CSS;
  }} else {{
    sp.style.cssText='';
    sp.textContent=m.emoji;
  }}
  updateStats();
}}

function dealDamage(base){{
  if(locked) return;
  const isCrit=Math.random()<0.18;
  const dmg=isCrit?Math.floor(base*(1.8+Math.random()*.6)):base;

  mHp=Math.max(0,mHp-dmg);
  totalDmg+=dmg;
  combo++;
  clearTimeout(comboTimer);
  comboTimer=setTimeout(()=>{{combo=0;updateStats();}},2000);

  animPlayer();
  hitMonster();
  spawnDmg(dmg,isCrit);
  updateMHp();
  updateStats();
  sayReact();

  if(mHp<=0){{locked=true;setTimeout(()=>onKill(),350);}}
}}

function attack(d){{dealDamage(d);}}
function useSkill(d){{dealDamage(d);}}

function animPlayer(){{
  const p=document.getElementById('player');
  p.classList.remove('attack');void p.offsetWidth;p.classList.add('attack');
  setTimeout(()=>p.classList.remove('attack'),380);
}}

function hitMonster(){{
  const s=document.getElementById('mSprite');
  s.classList.remove('hit');void s.offsetWidth;s.classList.add('hit');
  setTimeout(()=>s.classList.remove('hit'),380);
}}

function updateMHp(){{
  const pct=(mHp/mMaxHp)*100;
  const fill=document.getElementById('mHpFill');
  fill.style.width=pct+'%';
  fill.style.background=pct<25?'linear-gradient(90deg,#7f1d1d,#ef4444)':
                         pct<50?'linear-gradient(90deg,#92400e,#f59e0b)':
                                'linear-gradient(90deg,#ef4444,#ff6b6b)';
}}

function spawnDmg(dmg,isCrit){{
  const world=document.getElementById('world');
  const el=document.createElement('div');
  el.className='dmg '+(isCrit?'c':'n');
  el.textContent=isCrit?'💥'+dmg:''+dmg;
  el.style.right=(30+Math.random()*80)+'px';
  el.style.bottom=(80+Math.random()*80)+'px';
  world.appendChild(el);
  setTimeout(()=>el.remove(),950);
}}

function spawnLoot(){{
  const world=document.getElementById('world');
  for(let i=0;i<3;i++){{
    setTimeout(()=>{{
      const el=document.createElement('div');
      el.className='loot';
      el.textContent=LOOTS[Math.floor(Math.random()*LOOTS.length)];
      el.style.right=(50+Math.random()*100)+'px';
      el.style.bottom='80px';
      world.appendChild(el);
      setTimeout(()=>el.remove(),1500);
    }},i*120);
  }}
}}

function sayReact(){{
  const s=MONSTERS[stage].says;
  document.getElementById('sayBubble').textContent=s[Math.floor(Math.random()*s.length)];
}}

function onKill(){{
  kills++;
  spawnLoot();
  gainExp(MONSTERS[stage].exp);

  const isFinal=stage===MONSTERS.length-1;
  document.getElementById('clearEm').textContent=isFinal?'🏆':'✨';
  document.getElementById('clearTtl').textContent=isFinal?`${{MONSTERS[stage].name}} 처치!`:`${{MONSTERS[stage].name}} 처치!`;
  document.getElementById('clearSub').textContent=isFinal
    ?`전설의 보스를 쓰러뜨렸습니다! 총 데미지: ${{totalDmg.toLocaleString()}}`
    :`EXP +${{MONSTERS[stage].exp}} 획득!`;
  const btn=document.getElementById('nextBtn');
  if(isFinal){{ btn.textContent='🏆 결과 보기'; btn.onclick=showAllClear; }}
  else{{ btn.textContent='다음 스테이지 ▶'; btn.onclick=nextMonster; }}
  document.getElementById('clearOv').classList.add('show');
  updateStats();
}}

function gainExp(amount){{
  playerExp+=amount;
  while(playerExp>=playerExpMax){{
    playerExp-=playerExpMax;
    playerLv++;
    playerExpMax=Math.floor(playerExpMax*1.4);
  }}
  updatePlayerStat();
}}

function updatePlayerStat(){{
  document.getElementById('lvBadge').textContent=`Lv.${{playerLv}}`;
  const pct=(playerExp/playerExpMax)*100;
  document.getElementById('expFill').style.width=pct+'%';
  const hp=Math.min(100,100+playerLv*10);
  document.getElementById('playerHp').textContent=hp;
}}

function updateStats(){{
  document.getElementById('sDmg').textContent=totalDmg.toLocaleString();
  document.getElementById('sCombo').textContent=combo>1?combo+'x':combo;
  document.getElementById('sKills').textContent=kills;
}}

function nextMonster(){{ stage++; loadMonster(); }}

function showAllClear(){{
  document.getElementById('clearOv').classList.remove('show');
  document.getElementById('acDmg').textContent=totalDmg.toLocaleString();
  document.getElementById('allClear').classList.add('show');
}}

initGame();
</script>
</body>
</html>"""
        components.html(game_html, height=760, scrolling=False)

# ────────────────────────────────────────
# TAB 3 — 대화하기 (native Streamlit streaming)
# ────────────────────────────────────────
with tab3:
    if not st.session_state.game_ready:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#c49a9a;">
          <div style="font-size:3rem">👆</div>
          <p>먼저 <b>악마 등록</b> 탭에서 악마를 등록하고<br>
          <b>사냥 시작하기</b>를 눌러주세요!</p>
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
                '😈 경계 중</span>',
                unsafe_allow_html=True,
            )

        st.divider()


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
                st.write("...(악마가 으르렁거리며 노려보고 있다)")

        for msg in st.session_state.chat_history:
            role = msg["role"]
            avatar = "😈" if role == "assistant" else "🧑‍💼"
            with st.chat_message(role, avatar=avatar):
                st.write(msg["content"])

        # 사용자 입력 받기 (텍스트 입력 or 빠른 메시지)
        user_input = st.chat_input("악마를 도발해보세요... ⚔️")

        pending = st.session_state.pop("_pending", None) if "_pending" in st.session_state else None
        msg_to_send = pending or user_input

        if msg_to_send:
            with st.chat_message("user", avatar="🧑‍💼"):
                st.write(msg_to_send)
            st.session_state.chat_history.append({"role": "user", "content": msg_to_send})

            # 대화 횟수에 따라 상사가 점점 무너지도록
            turn = len(st.session_state.chat_history) // 2
            moods = [
                ("권위적·냉소적", "직원을 무시하고 권위를 내세우며 반박"),
                ("방어적·변명", "잘못을 인정 안 하고 핑계를 댐"),
                ("당황·짜증", "말문이 막히지만 억지로 우기는 척"),
                ("꼬리내리는 척·위협", "잘못인 척하다 갑자기 협박으로 선회"),
                ("분노·자기연민", "억울하다고 호소하며 큰 소리를 침"),
                ("수세·횡설수설", "논리가 무너져서 앞뒤가 안 맞는 말을 함"),
            ]
            mood_label, mood_desc = moods[min(turn, len(moods)-1)]
            forbidden = []
            for m in st.session_state.chat_history:
                if m["role"] == "assistant" and len(m["content"]) < 60:
                    forbidden.append(m["content"][:30])
            forbidden_str = " / ".join(forbidden[-3:]) if forbidden else "없음"

            system_prompt = (
                f'당신은 "{st.session_state.boss_name}"({st.session_state.boss_title})이라는 악마 캐릭터입니다.\n'
                f'현재 감정 상태: [{mood_label}] — {mood_desc}\n'
                f'현재 대화 {turn+1}번째. 도발이 쌓일수록 점점 더 궁지에 몰리고 무너져 가세요.\n\n'
                "## 캐릭터 설정\n"
                "- 직장인들을 괴롭히는 악마. 야근 강요, 공 가로채기, 갑질이 특기인 직장 내 악마 존재\n"
                "- 도발당하면 처음엔 위압적으로 나오다가 점점 당황하고 자기모순에 빠짐\n"
                "- 절대 완전히 굴복하지 않음. 인정하는 척하다 반드시 뒤집음\n\n"
                "## 답변 규칙\n"
                "- 반드시 상대방의 이번 말 내용에 구체적으로 반응\n"
                "- 매번 다른 표현 사용. 이전에 한 말 절대 반복 금지\n"
                f"- 특히 이 표현들 재사용 금지: {forbidden_str}\n"
                "- 비꼬기·억울함·협박·자기합리화 등 다양한 반응 섞기\n"
                "- 욕설 없이 1~2문장. 짧고 임팩트 있게. 반드시 한국어\n"
            )

            def stream_boss():
                client = anthropic.Anthropic(api_key=get_api_key())
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
                    api_key = get_api_key()
                    if not api_key:
                        st.error("❌ API 키가 설정되지 않았습니다. Streamlit Cloud → Settings → Secrets에 `anthropic_api_key`를 추가해주세요.")
                        st.stop()
                    response_text = st.write_stream(stream_boss())
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response_text}
                    )
                except Exception as e:
                    st.error(f"⚠️ API 오류: {e}")
