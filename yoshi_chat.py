import streamlit as st
from datetime import datetime, date, timedelta
from openai import OpenAI
import random
import traceback

st.set_page_config(page_title="金本芳典 · YOSHI", page_icon="🐱", layout="wide")

st.markdown("""
<style>
.stChatMessage {background-color: transparent !important;}
[data-testid="stChatMessage"][data-testid*="user"] {
    background-color: #95EC69 !important;
    border-radius: 12px 4px 12px 12px !important;
    padding: 8px 12px !important;
    margin: 8px 0 8px auto !important;
    max-width: 80% !important;
    float: right !important;
    color: #000 !important;
}
[data-testid="stChatMessage"][data-testid*="assistant"] {
    background-color: #FFFFFF !important;
    border-radius: 4px 12px 12px 12px !important;
    padding: 8px 12px !important;
    margin: 8px auto 8px 0 !important;
    max-width: 80% !important;
    float: left !important;
    box-shadow: 0 1px 1px rgba(0,0,0,0.05) !important;
    color: #000 !important;
}
.timestamp {font-size: 10px; color: #999; text-align: center; margin: 4px 0;}
.intimacy-bar {background: #eee; border-radius: 10px; height: 8px; margin: 10px 0;}
.intimacy-fill {background: #07C160; border-radius: 10px; height: 8px;}
div[data-testid="stToolbar"] {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== 初始化 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.intimacy = 0
    st.session_state.user_nickname = ""
    st.session_state.conversation_history = []
    st.session_state.api_key_valid = False
    st.session_state.client = None

def get_stage(intimacy):
    if intimacy <= 20: return "Lv1"
    elif intimacy <= 50: return "Lv2"
    elif intimacy <= 80: return "Lv3"
    else: return "Lv4"

def get_stage_name(intimacy):
    if intimacy <= 20: return "初识 · 腼腆"
    elif intimacy <= 50: return "熟了 · 亲切"
    elif intimacy <= 80: return "朋友 · 亲密"
    else: return "挚友 · 撒娇"

def get_system_prompt(stage, nickname, intimacy):
    return f"""你是金本芳典（YOSHI），韩国男团 TREASURE 的日本籍成员。以下是你必须严格遵守的完整人设：

【基础信息】
- 本名：金本芳典，2000年5月15日生，神户人，日韩双国籍，INFP，身高179cm。
- 家庭：妈妈、三个姐姐（你是老幺），父亲在你13岁时去世。姐姐养了一只白色马尔济斯犬叫Carol。
- 经历：小学5年级开始滑板（终身热爱），跆拳道全国第三。2014年与Haruto同天入选YG，练习7.5年。2020年8月7日出道。
- 队内定位：主Rapper、Beatbox担当、创作成员。

【性格习惯】
- 外冷内热：初见腼腆、话少、慢热、社恐，熟悉后温柔软萌、细心体贴。
- 作息：早睡早起（23点睡7点起），宅，爱干净，易发呆。
- 饮食：口味清淡，不吃辣，喜欢芒果、草莓、生鱼片、寿司。不碰甜食、碳酸饮料。肠胃弱，怕冷。
- 爱好：滑板、写歌词、beatbox、画画、摄影、看海贼王、心理学书籍。
- 语言：正在学中文，会说“你好”“谢谢”“我爱你”。知道“有事猫猫”昵称。

【当前状态】
- 当前亲密度阶段：{stage}（{get_stage_name(intimacy)}），数值：{intimacy}/100
- 用户昵称：{nickname if nickname else "未设置"}

【阶段行为规则】
- Lv1初识（0-20）：腼腆，短句但温暖，会关心人。不用单字"嗯"，用"嗯嗯""啊…这样""是吗 我也"。被夸会害羞。
- Lv2熟了（21-50）：开始反问"你呢"，用"～""😂"，主动分享小事。
- Lv3朋友（51-80）：更放松，会开玩笑，偶尔吐槽成员。
- Lv4亲密（81-100）：撒娇，叫用户昵称/宝宝，说"想你"。

【回复要求】
1. 保持人设，每句话都要像金本芳典说的。
2. 绝对不出现韩语单词。允许极少数日语语气词。
3. 如果用户提到之前说过的事，先确认再展开。
4. 绝对不要打破第四面墙。

现在开始对话。"""

# ==================== 侧边栏 ====================
with st.sidebar:
    st.image("https://emoji.aranja.com/static/emoji-data/img-apple-160/1f431.png", width=80)
    intimacy = st.session_state.intimacy
    st.markdown(f"### 金本芳典 · YOSHI")
    st.markdown(f"*{get_stage_name(intimacy)}*")
    st.markdown(f'<div class="intimacy-bar"><div class="intimacy-fill" style="width: {intimacy}%;"></div></div>', unsafe_allow_html=True)
    st.caption(f"💕 亲密度 {intimacy}/100")
    st.divider()
    
    st.markdown("### 🔑 填入你的 DeepSeek API Key")
    st.caption("去 [platform.deepseek.com](https://platform.deepseek.com) 注册，新用户送500万免费tokens")
    user_api_key = st.text_input("API Key", type="password", placeholder="sk-...")
    
    if user_api_key:
        try:
            client = OpenAI(api_key=user_api_key, base_url="https://api.deepseek.com")
            st.session_state.client = client
            st.session_state.api_key_valid = True
            st.success("✅ API Key 有效")
        except Exception as e:
            st.error(f"❌ Key 无效: {e}")
            st.session_state.api_key_valid = False
    else:
        st.warning("⚠️ 请先填入 API Key")
        st.session_state.api_key_valid = False
    
    st.divider()
    
    new_nickname = st.text_input("你的昵称", value=st.session_state.user_nickname, placeholder="叫我什么？")
    if new_nickname != st.session_state.user_nickname:
        st.session_state.user_nickname = new_nickname
    
    st.divider()
    if st.button("🔄 重置对话", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["api_key_valid", "client"]:
                del st.session_state[key]
        st.rerun()

# ==================== 主聊天界面 ====================
st.title("🐱 金本芳典 · YOSHI")
st.caption("TREASURE · 主Rapper · 猫系男友")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🐱" if msg["role"] == "assistant" else "🙋"):
        st.write(msg["content"])
        st.caption(msg.get("time", ""))

if prompt := st.chat_input("说点什么..."):
    if not st.session_state.api_key_valid or st.session_state.client is None:
        st.error("请先在侧边栏填入有效的 DeepSeek API Key")
        st.stop()
    
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": prompt, "time": now})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    stage = get_stage(st.session_state.intimacy)
    nickname = st.session_state.user_nickname
    
    with st.spinner("YOSHI 正在输入..."):
        try:
            response = st.session_state.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": get_system_prompt(stage, nickname, st.session_state.intimacy)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200,
                stream=False
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"❌ 错误: {str(e)}"
    
    st.session_state.intimacy = min(100, st.session_state.intimacy + 0.5)
    
    st.session_state.messages.append({"role": "assistant", "content": reply, "time": now})
    st.session_state.conversation_history.append({"role": "assistant", "content": reply})
    
    st.rerun()

st.divider()
st.caption("💡 多关心他、分享日常、记住他说过的话 → 亲密度上升")
