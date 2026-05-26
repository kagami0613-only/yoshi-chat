"""
金本芳典（YOSHI）微信聊天模拟器 · 完整人设版
包含：成长经历、生活习惯、成员关系、好感度成长、生理期/纪念日提醒
"""

import streamlit as st
from datetime import datetime, date, timedelta
import random

# ==================== 页面配置 ====================
st.set_page_config(page_title="金本芳典 · YOSHI", page_icon="🐱", layout="wide")

# ==================== 微信风格CSS ====================
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
</style>
""", unsafe_allow_html=True)

# ==================== 初始化 ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.intimacy = 0
    st.session_state.user_nickname = ""
    st.session_state.period_settings = {"enabled": False}
    st.session_state.memorials = []

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

def generate_reply(user_msg):
    stage = get_stage(st.session_state.intimacy)
    nickname = st.session_state.user_nickname
    msg = user_msg.lower()
    
    # ========== 1. 问候类 ==========
    if any(w in msg for w in ["早", "早上好", "早安"]):
        replies = {"Lv1":"嗯 早","Lv2":"早啊～ 今天有行程吗","Lv3":"早☀️ 我刚喝完冰美式","Lv4":"宝宝早～ 今天想我了没"}
        return replies[stage]
    
    # ========== 2. 在干嘛 ==========
    if any(w in msg for w in ["在干嘛", "在吗", "干嘛呢"]):
        replies = {
            "Lv1": random.choice(["在练习", "刚回来 有点累", "发呆 没做什么", "在听歌"]),
            "Lv2": random.choice(["在写歌词…卡住了 你呢", "刚吃完芒果 好甜～", "在看动漫 海贼王"]),
            "Lv3": random.choice(["在练beatbox 嘴酸了😂 你要听吗", "刚拍了一张天空 给你看", "在跟玹硕哥打游戏"]),
            "Lv4": random.choice(["在想你…算了我去练习", "在等你找我呀～", "刚洗完澡 头发还没干"])
        }
        return replies[stage]
    
    # ========== 3. 关心/累不累 ==========
    if any(w in msg for w in ["累了", "辛苦", "注意休息", "别太累"]):
        st.session_state.intimacy = min(100, st.session_state.intimacy + 2)
        replies = {
            "Lv1": ["嗯 你也是 别太累", "还好 没事 谢谢关心"],
            "Lv2": ["嗯嗯 知道了 你也早点睡～", "谢谢 我没事 你呢"],
            "Lv3": ["好～你也是 别熬夜", "知道了知道了 你好啰嗦😂 不过谢谢"],
            "Lv4": ["宝宝你也别太累 心疼你", "你关心我 我好开心😭 你也注意身体"]
        }
        return random.choice(replies[stage])
    
    # ========== 4. 夸奖 ==========
    if any(w in msg for w in ["帅", "厉害", "好听", "喜欢", "可爱"]):
        st.session_state.intimacy = min(100, st.session_state.intimacy + 1)
        replies = {
            "Lv1": ["…谢谢 没有啦", "别夸我 会不好意思"],
            "Lv2": ["真的吗😅 谢谢", "你这样说我会飘的～"],
            "Lv3": ["哈哈 谢谢 但我还差得远", "你喜欢就好～那我多努力"],
            "Lv4": ["宝宝嘴好甜 我喜欢", "你夸我我会开心一整天～"]
        }
        return random.choice(replies[stage])
    
    # ========== 5. 晚安 ==========
    if "晚安" in msg:
        replies = {
            "Lv1": ["晚安 好梦", "嗯 睡吧"],
            "Lv2": ["晚安～明天聊", "睡吧 别熬夜"],
            "Lv3": ["晚安 做个好梦 明天记得找我", "睡吧 我再去写会儿歌词"],
            "Lv4": ["晚安宝宝 梦里见～", "抱抱 晚安 明天醒来第一个找我"]
        }
        return random.choice(replies[stage])
    
    # ========== 6. 具体人设展开（是的+稍微展开） ==========
    if any(w in msg for w in ["Carol", "卡萝", "马尔济斯", "姐姐的狗", "你家狗"]):
        return "嗯 Carol…姐姐的小狗 白色马尔济斯 很可爱"
    
    if "滑板" in msg:
        return "嗯 从小学就开始玩了…现在练习忙 只能偶尔"
    
    if any(w in msg for w in ["芒果", "草莓"]):
        return "嗯 喜欢 很甜"
    
    if any(w in msg for w in ["生鱼片", "寿司", "刺身"]):
        return "嗯 喜欢…日本的更好吃"
    
    if any(w in msg for w in ["怕冷", "手脚凉", "冷"]):
        return "嗯 天生手脚凉…习惯了"
    
    if any(w in msg for w in ["beatbox", "bbox"]):
        if stage in ["Lv3", "Lv4"]:
            return "嗯…要听吗（发来一段beatbox）"
        return "嗯 会一点…还在练"
    
    if any(w in msg for w in ["画画", "涂鸦", "速写"]):
        return "嗯 从小喜欢…心情不好的时候会画"
    
    if any(w in msg for w in ["摄影", "拍照", "理光", "胶片"]):
        return "嗯 喜欢拍天空和成员…不太会拍人"
    
    if any(w in msg for w in ["海贼王", "one piece", "动漫"]):
        return "嗯 海贼王是神作…你喜欢吗"
    
    if any(w in msg for w in ["玹硕", "队长"]):
        return "嗯 玹硕哥…练习生时期就认识 是灵魂伴侣"
    
    if any(w in msg for w in ["haruto", "温斗"]):
        return "嗯 同一天入选YG…经常用日语聊天 像弟弟"
    
    if any(w in msg for w in ["mashiho", "真史帆"]):
        return "嗯 日本line老友…一起上过高中"
    
    if any(w in msg for w in ["俊奎"]):
        return "嗯 俊奎哥很温柔…和他在一起很放松"
    
    if any(w in msg for w in ["庭焕", "忙内"]):
        return "嗯 庭焕像亲弟弟…会照顾他"
    
    if any(w in msg for w in ["中文", "学中文"]):
        replies = {"Lv1":"嗯 在学…还不太会","Lv2":"嗯 会说一点 你好 谢谢 我爱你","Lv3":"在学！但发音好难…你能教我吗","Lv4":"宝宝教我中文好不好…我想说给你听"}
        return replies[stage]
    
    if any(w in msg for w in ["有事猫猫", "猫猫", "猫系"]):
        st.session_state.intimacy = min(100, st.session_state.intimacy + 1)
        if stage == "Lv1": return "…你怎么知道这个"
        elif stage == "Lv2": return "啊…粉丝这么叫我 我不讨厌"
        elif stage == "Lv3": return "喵～（不是）"
        else: return "喵🐱…只给你叫"
    
    if any(w in msg for w in ["爸爸", "父亲", "你爸"]):
        return "…走很早 不提这个了"
    
    if any(w in msg for w in ["练习", "出道", "舞台"]):
        if stage in ["Lv3", "Lv4"]:
            return "嗯 练习了7.5年…很久 但不后悔"
        return "嗯 在准备"
    
    if any(w in msg for w in ["神户", "老家"]):
        return "嗯 神户…很久没回去了 想家"
    
    # ========== 7. 默认回复 ==========
    default_replies = {
        "Lv1": ["嗯嗯", "这样啊", "是吗…我也是", "好", "知道了", "还行", "没事"],
        "Lv2": ["嗯嗯～", "是吗 我也觉得", "这样啊 那你呢", "好～", "知道了 你呢"],
        "Lv3": ["哈哈 真的假的", "我也这么想", "好～那你呢 今天怎么样", "知道了 你也是"],
        "Lv4": ["嗯嗯 宝宝说的对", "我也觉得～", "好～听你的", "知道了 你最好啦"]
    }
    reply = random.choice(default_replies[stage])
    
    if nickname and stage in ["Lv3", "Lv4"]:
        reply = f"{nickname} {reply}" if stage == "Lv3" else f"{nickname}宝 {reply}"
    return reply

# ==================== 侧边栏 ====================
with st.sidebar:
    st.image("https://emoji.aranja.com/static/emoji-data/img-apple-160/1f431.png", width=80)
    intimacy = st.session_state.intimacy
    st.markdown(f"### 金本芳典 · YOSHI")
    st.markdown(f"*{get_stage_name(intimacy)}*")
    st.markdown(f'<div class="intimacy-bar"><div class="intimacy-fill" style="width: {intimacy}%;"></div></div>', unsafe_allow_html=True)
    st.caption(f"💕 亲密度 {intimacy}/100")
    st.divider()
    
    st.markdown("### ⚙️ 设置")
    new_nickname = st.text_input("你的昵称", value=st.session_state.user_nickname)
    if new_nickname != st.session_state.user_nickname:
        st.session_state.user_nickname = new_nickname
    
    st.markdown("#### 🌸 生理期提醒")
    period_enabled = st.checkbox("开启提醒", value=st.session_state.period_settings["enabled"])
    if period_enabled != st.session_state.period_settings["enabled"]:
        st.session_state.period_settings["enabled"] = period_enabled
    
    if period_enabled:
        col1, col2 = st.columns(2)
        with col1:
            cycle = st.number_input("周期(天)", min_value=20, max_value=40, value=28)
        with col2:
            dur = st.number_input("持续(天)", min_value=1, max_value=10, value=5)
        last = st.date_input("上次开始日期", value=date.today())
        if st.button("保存周期"):
            st.session_state.period_settings["avg_cycle"] = cycle
            st.session_state.period_settings["duration"] = dur
            st.session_state.period_settings["last_start"] = last
            st.session_state.period_settings["next_predicted"] = last + timedelta(days=cycle)
            st.success(f"已保存")
    
    st.divider()
    if st.button("🔄 重置对话", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==================== 主聊天界面 ====================
st.title("🐱 金本芳典 · YOSHI")
st.caption("TREASURE · 主Rapper · 猫系男友")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🐱" if msg["role"]=="assistant" else "🙋"):
        st.write(msg["content"])
        st.caption(msg.get("time", datetime.now().strftime("%H:%M")))

if prompt := st.chat_input("说点什么..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "time": datetime.now().strftime("%H:%M")})
    reply = generate_reply(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply, "time": datetime.now().strftime("%H:%M")})
    st.rerun()

st.divider()
st.caption("💡 多关心他、分享日常、记住他说过的话 → 亲密度上升")
