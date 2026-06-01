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
        boss_img_tag = f'<img src="{img_data}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">' if img_data else ""

        game_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Noto Sans KR',sans-serif;background:#0d0d1a;color:#f0eeff;padding:.8rem;overflow-x:hidden;}}

/* 스탯 바 */
.stats-row{{display:flex;gap:.6rem;margin-bottom:.8rem;}}
.stat-box{{flex:1;background:#1a1a2e;border:1px solid #2a2a4a;border-radius:12px;padding:.6rem;text-align:center;}}
.stat-val{{font-family:'Black Han Sans',sans-serif;font-size:1.4rem;color:#a78bfa;}}
.stat-lbl{{font-size:.7rem;color:#6b6b9a;margin-top:.1rem;}}

/* 스테이지 뱃지 */
.stage-badge{{text-align:center;margin-bottom:.4rem;font-size:.8rem;color:#6b6b9a;letter-spacing:2px;text-transform:uppercase;}}

/* HP 바 */
.hp-wrap{{background:#1a1a2e;border-radius:12px;padding:.8rem 1rem;margin-bottom:.8rem;border:1px solid #2a2a4a;}}
.hp-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;}}
.hp-name{{font-family:'Black Han Sans',sans-serif;font-size:1rem;color:#f0eeff;}}
.hp-text{{font-size:.85rem;color:#a78bfa;font-weight:700;}}
.hp-bg{{height:18px;background:#0d0d1a;border-radius:9px;overflow:hidden;}}
.hp-fill{{height:100%;border-radius:9px;transition:width .25s ease;background:linear-gradient(90deg,#7c3aed,#a78bfa);}}
.hp-fill.danger{{background:linear-gradient(90deg,#dc2626,#ef4444);}}
.hp-fill.warning{{background:linear-gradient(90deg,#d97706,#f59e0b);}}

/* 몬스터 영역 */
.monster-arena{{position:relative;width:220px;height:220px;margin:0 auto .6rem;display:flex;align-items:center;justify-content:center;}}
.monster-ring{{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle,#1a1040 60%,transparent 100%);}}
.monster-glow{{position:absolute;inset:10px;border-radius:50%;box-shadow:0 0 40px rgba(167,139,250,0.3);animation:pulseGlow 2s ease-in-out infinite;}}
@keyframes pulseGlow{{0%,100%{{box-shadow:0 0 30px rgba(167,139,250,.2);}}50%{{box-shadow:0 0 60px rgba(167,139,250,.5);}}}}
.monster-body{{position:relative;z-index:3;width:150px;height:150px;border-radius:50%;background:#1a1040;border:3px solid #7c3aed;display:flex;align-items:center;justify-content:center;font-size:5rem;cursor:pointer;user-select:none;transition:transform .08s;overflow:hidden;}}
.monster-body:active{{transform:scale(.85);}}
.monster-body.boss-mode{{border-color:#dc2626;box-shadow:0 0 25px rgba(220,38,38,.5);}}

/* 데미지 숫자 */
.dmg-pop{{position:absolute;font-family:'Black Han Sans',sans-serif;font-size:1.6rem;font-weight:900;pointer-events:none;z-index:20;animation:dmgFloat .8s forwards;}}
.dmg-pop.crit{{font-size:2.2rem;color:#fbbf24;}}
.dmg-pop.normal{{color:#a78bfa;}}
@keyframes dmgFloat{{
  0%{{opacity:1;transform:translateY(0) scale(.8);}}
  40%{{opacity:1;transform:translateY(-40px) scale(1.2);}}
  100%{{opacity:0;transform:translateY(-80px) scale(.9);}}
}}

/* 몬스터 반응 */
.monster-say{{background:#1a1a2e;border-radius:12px;padding:.7rem 1rem;text-align:center;border-left:3px solid #7c3aed;min-height:44px;display:flex;align-items:center;justify-content:center;font-size:.9rem;margin-bottom:.8rem;color:#d4c8ff;}}

/* 스킬 버튼 */
.skills-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem;}}
.skill-btn{{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:.75rem .4rem;cursor:pointer;text-align:center;transition:all .15s;}}
.skill-btn:hover{{background:#25254a;border-color:#7c3aed;transform:scale(1.06);}}
.skill-btn:active{{transform:scale(.93);}}
.skill-icon{{font-size:1.7rem;display:block;margin-bottom:.2rem;}}
.skill-name{{font-size:.7rem;color:#6b6b9a;}}
.skill-dmg{{font-size:.75rem;color:#a78bfa;font-weight:700;margin-top:.1rem;}}

/* 클리어 오버레이 */
.clear-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:100;align-items:center;justify-content:center;flex-direction:column;gap:1rem;}}
.clear-overlay.show{{display:flex;animation:fadeIn .3s;}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
.clear-emoji{{font-size:5rem;animation:bounce .6s infinite alternate;}}
@keyframes bounce{{from{{transform:translateY(0)}}to{{transform:translateY(-20px)}}}}
.clear-title{{font-family:'Black Han Sans',sans-serif;font-size:2rem;color:#fbbf24;letter-spacing:3px;text-shadow:0 0 20px rgba(251,191,36,.6);}}
.clear-sub{{color:#a78bfa;font-size:1rem;}}
.next-btn{{background:#7c3aed;color:#fff;border:none;border-radius:14px;padding:.8rem 2.5rem;font-family:'Black Han Sans',sans-serif;font-size:1.1rem;cursor:pointer;letter-spacing:2px;transition:all .2s;margin-top:.5rem;}}
.next-btn:hover{{background:#6d28d9;transform:scale(1.05);}}

/* 쉐이크 */
@keyframes shakeAnim{{
  0%,100%{{transform:translateX(0) rotate(0);}}
  20%{{transform:translateX(-10px) rotate(-4deg);}}
  40%{{transform:translateX(10px) rotate(4deg);}}
  60%{{transform:translateX(-6px) rotate(-2deg);}}
  80%{{transform:translateX(6px) rotate(2deg);}}
}}
.shake{{animation:shakeAnim .35s ease-in-out;}}

/* 올클리어 */
.allclear{{display:none;position:fixed;inset:0;background:linear-gradient(135deg,#0d0d1a,#1a0a2e);z-index:200;align-items:center;justify-content:center;flex-direction:column;gap:1.2rem;text-align:center;}}
.allclear.show{{display:flex;animation:fadeIn .5s;}}
.allclear-stars{{font-size:3rem;letter-spacing:.5rem;}}
.allclear-title{{font-family:'Black Han Sans',sans-serif;font-size:2.5rem;color:#fbbf24;letter-spacing:4px;text-shadow:0 0 30px rgba(251,191,36,.8);}}
.allclear-score{{font-size:1.2rem;color:#a78bfa;}}
.replay-btn{{background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff;border:none;border-radius:16px;padding:1rem 3rem;font-family:'Black Han Sans',sans-serif;font-size:1.2rem;cursor:pointer;letter-spacing:2px;margin-top:.5rem;}}
</style>
</head>
<body>

<!-- 스탯 -->
<div class="stats-row">
  <div class="stat-box"><div class="stat-val" id="totalDmg">0</div><div class="stat-lbl">총 데미지</div></div>
  <div class="stat-box"><div class="stat-val" id="comboDisplay">0</div><div class="stat-lbl">콤보</div></div>
  <div class="stat-box"><div class="stat-val" id="caughtCount">0</div><div class="stat-lbl">처치 수</div></div>
</div>

<!-- HP 바 -->
<div class="hp-wrap">
  <div class="hp-header">
    <span class="hp-name" id="monsterName">로딩중...</span>
    <span class="hp-text"><span id="hpCur">0</span> / <span id="hpMax">0</span></span>
  </div>
  <div class="hp-bg"><div class="hp-fill" id="hpBar" style="width:100%"></div></div>
</div>

<!-- 스테이지 -->
<div class="stage-badge" id="stageBadge">STAGE 1 / 5</div>

<!-- 몬스터 -->
<div class="monster-arena" id="monsterArena">
  <div class="monster-ring"></div>
  <div class="monster-glow"></div>
  <div class="monster-body" id="monsterBody" onclick="attack(5)">
    <span id="monsterEmoji">👾</span>
  </div>
</div>

<!-- 반응 -->
<div class="monster-say" id="monsterSay">👆 탭해서 공격하거나 아래 스킬을 사용하세요!</div>

<!-- 스킬 -->
<div class="skills-grid">
  <div class="skill-btn" onclick="useSkill(15,'⚔️')"><span class="skill-icon">⚔️</span><span class="skill-name">참격</span><span class="skill-dmg">-15</span></div>
  <div class="skill-btn" onclick="useSkill(25,'🔥')"><span class="skill-icon">🔥</span><span class="skill-name">화염</span><span class="skill-dmg">-25</span></div>
  <div class="skill-btn" onclick="useSkill(20,'⚡')"><span class="skill-icon">⚡</span><span class="skill-name">번개</span><span class="skill-dmg">-20</span></div>
  <div class="skill-btn" onclick="useSkill(30,'❄️')"><span class="skill-icon">❄️</span><span class="skill-name">빙결</span><span class="skill-dmg">-30</span></div>
  <div class="skill-btn" onclick="useSkill(20,'☄️')"><span class="skill-icon">☄️</span><span class="skill-name">유성</span><span class="skill-dmg">-20</span></div>
  <div class="skill-btn" onclick="useSkill(35,'💥')"><span class="skill-icon">💥</span><span class="skill-name">폭발</span><span class="skill-dmg">-35</span></div>
  <div class="skill-btn" onclick="useSkill(25,'🌪️')"><span class="skill-icon">🌪️</span><span class="skill-name">회오리</span><span class="skill-dmg">-25</span></div>
  <div class="skill-btn" onclick="useSkill(50,'🌟')"><span class="skill-icon">🌟</span><span class="skill-name">필살기</span><span class="skill-dmg">-50</span></div>
</div>

<!-- 처치 오버레이 -->
<div class="clear-overlay" id="clearOverlay">
  <div class="clear-emoji" id="clearEmoji">✨</div>
  <div class="clear-title" id="clearTitle">처치!</div>
  <div class="clear-sub" id="clearSub"></div>
  <button class="next-btn" onclick="nextMonster()">다음 몬스터 ▶</button>
</div>

<!-- 올클리어 -->
<div class="allclear" id="allClear">
  <div class="allclear-stars">⭐⭐⭐</div>
  <div class="allclear-title">ALL CLEAR!</div>
  <div class="allclear-score">총 데미지: <span id="finalDmg">0</span></div>
  <div style="color:#6b6b9a;font-size:.9rem;">직장 스트레스가 100% 해소되었습니다 🎉</div>
  <button class="replay-btn" onclick="initGame()">🔄 다시 하기</button>
</div>

<script>
const BOSS_NAME = '{boss_name_safe}';
const BOSS_IMG  = `{boss_img_tag}`;

const MONSTERS = [
  {{ name:'잔업 요괴',   emoji:'👾', hp:80,  color:'#7c3aed', says:['으아악!','왜 공격해!','살살 해!'] }},
  {{ name:'꼰대 좀비',   emoji:'🧟', hp:130, color:'#059669', says:['으르르...','끄읍...','부하직원이!'] }},
  {{ name:'갑질 도깨비', emoji:'👹', hp:180, color:'#dc2626', says:['감히!!','이놈!','야근해!!'] }},
  {{ name:'초과근무 악마',emoji:'😈', hp:250, color:'#9333ea', says:['호호호...','도망 못 가!','야근 각오해!'] }},
  {{ name:BOSS_NAME||'최종 보스', emoji:'💀', hp:400, color:'#dc2626', says:['크아아!','이럴 수가!','나를 이겨?!'], isBoss:true }},
];

let stage=0, hp=0, maxHp=0, totalDmg=0, combo=0, caught=0, comboTimer=null, locked=false;

function initGame(){{
  document.getElementById('allClear').classList.remove('show');
  stage=0; totalDmg=0; combo=0; caught=0;
  loadMonster();
}}

function loadMonster(){{
  locked=false;
  const m = MONSTERS[stage];
  hp=m.hp; maxHp=m.hp;

  document.getElementById('monsterName').textContent = m.name;
  document.getElementById('hpCur').textContent = hp;
  document.getElementById('hpMax').textContent = maxHp;
  document.getElementById('hpBar').style.width = '100%';
  document.getElementById('hpBar').className = 'hp-fill';
  document.getElementById('stageBadge').textContent = `STAGE ${{stage+1}} / ${{MONSTERS.length}}`;
  document.getElementById('monsterSay').textContent = '👆 탭해서 공격하거나 아래 스킬을 사용하세요!';

  const body = document.getElementById('monsterBody');
  if(m.isBoss && BOSS_IMG){{
    body.innerHTML = BOSS_IMG;
    body.classList.add('boss-mode');
  }} else {{
    body.innerHTML = `<span id="monsterEmoji">${{m.emoji}}</span>`;
    body.classList.remove('boss-mode');
    body.style.borderColor = m.color;
    body.style.boxShadow = `0 0 20px ${{m.color}}44`;
  }}
  document.querySelector('.monster-glow').style.boxShadow = `0 0 50px ${{m.color}}44`;

  document.getElementById('clearOverlay').classList.remove('show');
  updateStats();
}}

function dealDamage(dmg){{
  if(locked) return;
  const isCrit = Math.random() < 0.15;
  const finalDmg = isCrit ? Math.floor(dmg*2) : dmg;

  hp = Math.max(0, hp - finalDmg);
  totalDmg += finalDmg;
  combo++;
  clearTimeout(comboTimer);
  comboTimer = setTimeout(()=>{{ combo=0; updateStats(); }}, 1800);

  spawnDmg(finalDmg, isCrit);
  shakeMonster();
  sayReaction();
  updateHp();
  updateStats();

  if(hp <= 0){{ locked=true; setTimeout(showClear, 400); }}
}}

function attack(dmg){{ dealDamage(dmg); }}
function useSkill(dmg, icon){{ dealDamage(dmg); }}

function updateHp(){{
  const pct = (hp/maxHp)*100;
  const bar = document.getElementById('hpBar');
  bar.style.width = pct+'%';
  bar.className = 'hp-fill' + (pct<25?' danger':(pct<50?' warning':''));
  document.getElementById('hpCur').textContent = hp;
}}

function updateStats(){{
  document.getElementById('totalDmg').textContent = totalDmg.toLocaleString();
  document.getElementById('comboDisplay').textContent = combo>1?combo+'x':combo;
  document.getElementById('caughtCount').textContent = caught;
}}

function spawnDmg(dmg, isCrit){{
  const arena = document.getElementById('monsterArena');
  const el = document.createElement('div');
  el.className = 'dmg-pop ' + (isCrit?'crit':'normal');
  el.textContent = (isCrit?'💥CRIT! ':'-') + dmg;
  el.style.left = (20+Math.random()*55)+'%';
  el.style.top  = (10+Math.random()*40)+'%';
  arena.appendChild(el);
  setTimeout(()=>el.remove(), 900);
}}

function shakeMonster(){{
  const b = document.getElementById('monsterBody');
  b.classList.remove('shake'); void b.offsetWidth; b.classList.add('shake');
  setTimeout(()=>b.classList.remove('shake'), 380);
}}

function sayReaction(){{
  const m = MONSTERS[stage];
  const s = m.says;
  document.getElementById('monsterSay').textContent = s[Math.floor(Math.random()*s.length)];
}}

function showClear(){{
  caught++;
  const isFinal = stage === MONSTERS.length-1;
  const overlay = document.getElementById('clearOverlay');
  document.getElementById('clearEmoji').textContent = isFinal ? '🏆' : '✨';
  document.getElementById('clearTitle').textContent  = isFinal ? '최종 보스 처치!' : '처치!';
  document.getElementById('clearSub').textContent    = isFinal
    ? `총 데미지: ${{totalDmg.toLocaleString()}} | ${{MONSTERS.length}}마리 전부 처치!`
    : `${{MONSTERS[stage].name}} 처치! 다음 몬스터 도전!`;

  if(isFinal){{
    overlay.querySelector('.next-btn').textContent = '🏆 결과 보기';
    overlay.querySelector('.next-btn').onclick = showAllClear;
  }} else {{
    overlay.querySelector('.next-btn').textContent = '다음 몬스터 ▶';
    overlay.querySelector('.next-btn').onclick = nextMonster;
  }}
  overlay.classList.add('show');
  updateStats();
}}

function nextMonster(){{
  stage++;
  loadMonster();
}}

function showAllClear(){{
  document.getElementById('clearOverlay').classList.remove('show');
  document.getElementById('finalDmg').textContent = totalDmg.toLocaleString();
  document.getElementById('allClear').classList.add('show');
}}

initGame();
</script>
</body>
</html>"""
        components.html(game_html, height=680, scrolling=False)

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
