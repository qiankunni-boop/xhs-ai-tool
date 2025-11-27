import streamlit as st
from openai import OpenAI
import random
import datetime

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="XHS Note AI",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏，聚焦主界面
)

# ==========================================
# 👇 填入你的 Key 👇
# ==========================================
MY_SECRET_KEY = "在这里粘贴你的DeepSeekKey"
# ==========================================

# --- 2. 核心 CSS 美化 (这是变好看的魔法) ---
st.markdown("""
<style>
    /* 全局字体与背景 */
    .stApp {
        background-color: #f8f9fa; /* 极浅的灰白背景 */
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}

    /* --- 左侧：输入卡片 --- */
    .input-card {
        background-color: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04);
        border: 1px solid #f0f0f0;
    }
    
    /* 标题样式 */
    .main-title {
        font-size: 32px; font-weight: 800; color: #333; margin-bottom: 10px; letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 16px; color: #666; margin-bottom: 30px; font-weight: 400;
    }

    /* 模拟输入框标签样式 */
    .custom-label {
        font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; display: block;
    }

    /* 美化 Streamlit 原生输入框 */
    .stTextInput input, .stTextArea textarea {
        background-color: #f5f7f9;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 12px;
        font-size: 15px;
        color: #333;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff2442;
        box-shadow: 0 0 0 2px rgba(255,36,66,0.1);
    }

    /* 美化按钮 (复刻截图中的红色大按钮) */
    .stButton button {
        width: 100%;
        background: linear-gradient(90deg, #ff2442 0%, #ff5c73 100%);
        color: white;
        border: none;
        border-radius: 50px; /* 大圆角 */
        padding: 16px 24px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 10px 20px rgba(255,36,66,0.2);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px rgba(255,36,66,0.3);
        color: white;
    }
    .stButton button:active {
        transform: scale(0.98);
    }

    /* --- 右侧：高保真手机预览 (HTML/CSS画出来的) --- */
    .phone-container {
        display: flex; justify-content: center; align-items: center;
        padding-top: 20px;
    }
    
    .iphone-mockup {
        width: 320px; /* 略微缩小适配屏幕 */
        height: 680px;
        background-color: white;
        border-radius: 40px;
        border: 10px solid #1f1f1f; /* 黑色边框 */
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        font-family: sans-serif;
    }
    
    /* 顶部状态栏 */
    .status-bar {
        height: 44px; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; font-size: 12px; color: #333; font-weight: 600;
        position: absolute; top: 0; width: 100%; z-index: 10; background: linear-gradient(to bottom, rgba(255,255,255,0.8), transparent);
    }
    
    /* 顶部导航栏 */
    .nav-bar {
        height: 44px; margin-top: 44px; display: flex; justify-content: space-between; align-items: center; padding: 0 15px;
        color: #333; z-index: 10; position: relative;
    }
    .user-profile { display: flex; align-items: center; gap: 8px; }
    .avatar { width: 32px; height: 32px; border-radius: 50%; background: #eee; object-fit: cover; }
    .username { font-size: 14px; font-weight: 600; color: #333; }
    .follow-btn { border: 1px solid #ff2442; color: #ff2442; border-radius: 14px; padding: 2px 10px; font-size: 12px; font-weight: 600; }

    /* 图片区域 (轮播图效果) */
    .image-area {
        width: 100%; height: 420px; position: relative;
    }
    .note-img { width: 100%; height: 100%; object-fit: cover; }
    .img-indicator {
        position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.5); color: white;
        padding: 2px 8px; border-radius: 10px; font-size: 10px;
    }

    /* 底部内容区 */
    .content-area { padding: 15px; }
    .note-title { font-size: 18px; font-weight: 700; color: #333; margin-bottom: 8px; line-height: 1.4; }
    .note-desc { font-size: 14px; color: #333; line-height: 1.6; white-space: pre-wrap; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
    .tags { color: #1c4c9e; font-size: 14px; margin-top: 8px; }
    .date-loc { font-size: 12px; color: #999; margin-top: 10px; display: flex; justify-content: space-between;}

    /* 底部互动栏 */
    .interaction-bar {
        position: absolute; bottom: 0; width: 100%; height: 50px;
        border-top: 1px solid #eee; background: white;
        display: flex; align-items: center; justify-content: space-between; padding: 0 15px;
    }
    .comment-input {
        background: #f5f5f5; color: #999; padding: 8px 15px; border-radius: 20px; font-size: 12px; width: 120px;
    }
    .icons { display: flex; gap: 15px; color: #333; font-size: 18px; }
    .icon-item { display: flex; align-items: center; gap: 4px; font-size: 12px; font-weight: 500;}
    
    /* 风格标签选择器优化 */
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border-color: #e1e4e8 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'generated_title' not in st.session_state: st.session_state.generated_title = "等待生成标题..."
if 'generated_content' not in st.session_state: st.session_state.generated_content = "输入主题，点击生成，AI 将为你撰写爆款笔记内容..."
if 'cover_url' not in st.session_state: st.session_state.cover_url = "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&q=80"

# --- 4. AI 逻辑 ---
def get_client():
    if not MY_SECRET_KEY or "sk-" not in MY_SECRET_KEY: return None
    return OpenAI(api_key=MY_SECRET_KEY, base_url="https://api.deepseek.com")

def generate_xhs(topic, keywords, vibe):
    client = get_client()
    if not client: 
        # 演示模式 (无Key时返回假数据，保证界面好看)
        time.sleep(1.5)
        return "🔥 30天逆袭！雅思7分不是梦", "家人们！👋 今天必须按头安利这个复习方法！\n\n😭 之前我也是个英语渣，四级考了三次才过，雅思更是想都不敢想。\n\n🌟 但是！自从用了这个【三维记忆法】，真的绝绝子！\n\n✅ 听力：每天坚持磨耳朵，不看字幕盲听。\n✅ 口语：对着镜子练习，自信最重要！\n\n坚持一个月，你也可以！冲鸭！🦆\n\n#雅思 #英语学习 #逆袭"
    
    prompt = f"""
    你是一个小红书爆款文案专家。风格：{vibe}。
    主题：{topic}。关键词：{keywords}。
    
    请输出两部分内容，用 === 分隔：
    1. 一个最具吸引力的标题（含表情）
    2. 正文内容（含表情、分段、标签）
    """
    
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.3
        )
        text = resp.choices[0].message.content
        if "===" in text:
            return text.split("===")[0].strip(), text.split("===")[1].strip()
        return text[:20], text
    except:
        return "生成失败", "请检查 Key 或网络连接"

# --- 5. 主界面布局 (左输入，右手机) ---
col_left, col_right = st.columns([1, 1], gap="large")

# === 左侧：高颜值输入卡片 ===
with col_left:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">打造爆款小红书笔记 🔥</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">输入你的灵感关键词，AI 帮你搞定标题、正文和 Emoji 排版。</div>', unsafe_allow_html=True)
    
    # 1. 笔记主题
    st.markdown('<span class="custom-label">笔记主题 / 关键词</span>', unsafe_allow_html=True)
    topic = st.text_input("topic", placeholder="例如：如何高效学习英语", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. 核心卖点
    st.markdown('<span class="custom-label">核心卖点 / 补充信息</span>', unsafe_allow_html=True)
    keywords = st.text_area("kw", placeholder="例如：碎片时间、坚持打卡、免费资源...", height=100, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. 语气风格 (使用 Streamlit 原生 Pills，如果版本支持，否则用 Radio)
    st.markdown('<span class="custom-label">语气风格</span>', unsafe_allow_html=True)
    
    # 尝试使用 st.pills (Streamlit 1.40+)，如果报错请改回 st.radio
    try:
        vibe = st.pills("vibe", ["真诚分享 ❤️", "情绪共鸣 😭", "干货科普 🎓", "种草带货 🛍️", "搞笑吐槽 🤣"], default="真诚分享 ❤️", label_visibility="collapsed")
    except:
        vibe = st.radio("vibe", ["真诚分享 ❤️", "情绪共鸣 😭", "干货科普 🎓", "种草带货 🛍️", "搞笑吐槽 🤣"], horizontal=True, label_visibility="collapsed")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 4. 红色大按钮
    if st.button("✨ 立即生成笔记"):
        if not topic:
            st.warning("请输入主题哦~")
        else:
            with st.spinner("🔴 AI 正在疯狂构思中..."):
                t, c = generate_xhs(topic, keywords, vibe)
                st.session_state.generated_title = t
                st.session_state.generated_content = c
                # 随机换个图增加新鲜感
                st.session_state.cover_url = f"https://images.unsplash.com/photo-{random.choice(['1497633762265-9d179a990aa6','1513258496098-916fae946a9e','1503676260728-1c00da094a0b'])}?w=600&q=80"
                
    st.markdown('</div>', unsafe_allow_html=True) # End input-card

# === 右侧：像素级复刻手机预览 ===
with col_right:
    # 准备数据
    title = st.session_state.generated_title
    content = st.session_state.generated_content
    # 简单处理一下换行，让 HTML 显示更自然
    content_html = content.replace("\n", "<br>")
    
    # 提取标签 (简单的正则)
    tags = " ".join(re.findall(r"#\w+", content))
    content_no_tags = re.sub(r"#\w+", "", content).strip().replace("\n", "<br>")

    st.markdown(f"""
    <div class="phone-container">
        <div class="iphone-mockup">
            <div class="status-bar">
                <span>19:54</span>
                <span style="display:flex; gap:5px;">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M12 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h8zM4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H4z"/><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg>
                    <span>5G</span>
                </span>
            </div>
            
            <div class="nav-bar">
                <span style="font-size:20px;">❮</span>
                <div class="user-profile">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" class="avatar">
                    <span class="username">XHS博主</span>
                </div>
                <div class="follow-btn">关注</div>
                <span style="font-size:20px;">➦</span>
            </div>
            
            <div class="image-area">
                <img src="{st.session_state.cover_url}" class="note-img">
                <div class="img-indicator">1/4</div>
            </div>
            
            <div class="content-area">
                <div class="note-title">{title}</div>
                <div class="note-desc">{content_no_tags}</div>
                <div class="tags">{tags}</div>
                <div class="date-loc">11-20 北京</div>
            </div>
            
            <div class="interaction-bar">
                <div class="comment-input">说点什么...</div>
                <div class="icons">
                    <div class="icon-item">❤️ <span style="font-size:10px">1.2w</span></div>
                    <div class="icon-item">⭐ <span style="font-size:10px">5201</span></div>
                    <div class="icon-item">💬 <span style="font-size:10px">340</span></div>
                </div>
            </div>
            
            <div style="position:absolute; bottom:5px; left:50%; transform:translateX(-50%); width:120px; height:4px; background:#000; border-radius:2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
