import streamlit as st
from openai import OpenAI
import random
import time
import requests
import datetime
import re
import json
import sys
from io import StringIO

# 🔥 1. 基础配置
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except: pass

st.set_page_config(
    page_title="XHS Note AI v33.3",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 填入你的 Key 👇
# ==========================================
MY_SECRET_KEY = "sk-99458a2eb9a3465886f3394d7ec6da69"
# ==========================================

# --- 2. CSS 样式 (UI 修复核心) ---
st.markdown("""
<style>
    /* 全局设置 */
    .stApp { background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}

    /* 🔴 按钮美化 */
    .stButton button {
        background: linear-gradient(90deg, #ff2442 0%, #ff5c73 100%);
        color: white; border: none; border-radius: 20px;
        padding: 10px 24px; font-weight: 600; transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(255, 36, 66, 0.2);
    }
    .stButton button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 15px rgba(255, 36, 66, 0.3); color: white !important;
    }

    /* 📱 仿真手机预览 (布局修复版) */
    .iphone-mockup {
        width: 340px; height: 700px; background-color: white;
        border-radius: 40px; border: 12px solid #1f1f1f; /* 边框加粗 */
        margin: 0 auto; position: relative; overflow: hidden;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15); font-family: sans-serif;
    }
    
    /* 刘海屏 */
    .notch {
        position: absolute; top: 0; left: 50%; transform: translateX(-50%);
        width: 150px; height: 32px; background-color: #1f1f1f;
        border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; z-index: 999;
    }

    /* 顶部状态栏 (修复重叠) */
    .status-bar {
        position: absolute; top: 5px; width: 100%; height: 30px;
        display: flex; justify-content: space-between; align-items: center; 
        padding: 0 25px; /* 避开圆角 */
        font-size: 12px; color: #fff; font-weight: 600; z-index: 50;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }
    
    /* 顶部导航栏 (修复位置) */
    .nav-bar {
        position: absolute; top: 40px; width: 100%; height: 44px;
        display: flex; justify-content: space-between; align-items: center; 
        padding: 0 15px; color: #fff; z-index: 50;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }
    .user-profile { display: flex; align-items: center; gap: 8px; }
    .avatar { width: 32px; height: 32px; border-radius: 50%; border: 1px solid #fff; background: #ddd;}
    .username { font-size: 13px; font-weight: 600; color: #fff; }
    .follow-btn { 
        background: rgba(255,36,66,0.9); color: white; border-radius: 14px; 
        padding: 4px 12px; font-size: 12px; font-weight: 600; border:none;
    }

    /* 滚动内容区 (修复被顶部遮挡) */
    .screen-content {
        height: 100%; overflow-y: auto; scrollbar-width: none;
        padding-bottom: 60px; /* 底部留白 */
        background-color: #fff;
    }
    .screen-content::-webkit-scrollbar { display: none; }

    /* 封面与文字 */
    .cover-container { width: 100%; aspect-ratio: 3 / 4; position: relative; border-bottom: 1px solid #f0f0f0; }
    .cover-img { width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(0.85); }
    .cover-overlay {
        position: absolute; bottom: 15px; left: 15px; right: 15px; pointer-events: none;
        color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    .cover-main-title { font-size: 26px; font-weight: 900; line-height: 1.2; margin-bottom: 6px; color: #ffeb3b; }
    .cover-sub-title { font-size: 13px; background-color: rgba(0,0,0,0.6); padding: 4px 8px; border-radius: 4px; display: inline-block; }

    /* 正文样式 */
    .note-content { padding: 15px 18px 20px 18px; color: #333; line-height: 1.7; font-size: 15px; white-space: pre-wrap; word-wrap: break-word; }
    .date-loc { font-size: 12px; color: #999; margin: 0 18px 20px 18px; }

    /* 底部互动栏 */
    .interaction-bar {
        position: absolute; bottom: 0; width: 100%; height: 50px;
        border-top: 1px solid #eee; background: white; z-index: 60;
        display: flex; align-items: center; justify-content: space-between; padding: 0 15px;
    }
    .comment-input { background: #f5f5f5; color: #999; padding: 8px 15px; border-radius: 18px; font-size: 12px; width: 140px; }
    .icons { display: flex; gap: 15px; font-size: 18px; color: #333; }

    /* 功能组件 */
    .seo-box { background: #ecfdf5; border: 1px solid #10b981; border-radius: 10px; padding: 12px; margin-top: 15px; font-size: 14px; color: #064e3b; }
    .comment-card { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 10px; margin-top: 8px; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}
    .comment-user { font-weight: bold; color: #475569; display:flex; align-items:center; gap:5px;}
    .comment-reply { margin-top: 4px; padding-left: 8px; border-left: 2px solid #ff2442; color: #64748b; font-size: 13px; }
    .magic-box { background: #fff1f2; border: 1px solid #fda4af; padding: 10px; border-radius: 10px; margin-top: 15px; }
    .status-box-ref { background: #fffbeb; border: 1px solid #f59e0b; color: #b45309; padding: 8px 12px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;}
    .status-box-free { background: #eff6ff; border: 1px solid #3b82f6; color: #1d4ed8; padding: 8px 12px; border-radius: 8px; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'input_topic' not in st.session_state: st.session_state.input_topic = ''
if 'input_pain' not in st.session_state: st.session_state.input_pain = ''
if 'input_features' not in st.session_state: st.session_state.input_features = ''
if 'ref_content_buffer' not in st.session_state: st.session_state.ref_content_buffer = ''

# 文档相关
if 'uploaded_doc_content' not in st.session_state: st.session_state.uploaded_doc_content = '' 
if 'extracted_points' not in st.session_state: st.session_state.extracted_points = []

# 结果相关
if 'generated_result' not in st.session_state: st.session_state.generated_result = ''
if 'cover_design' not in st.session_state: st.session_state.cover_design = {"main": "", "sub": ""}
if 'comments_data' not in st.session_state: st.session_state.comments_data = [] # 评论数据
if 'seo_score' not in st.session_state: st.session_state.seo_score = 0
if 'analysis_report' not in st.session_state: st.session_state.analysis_report = ''

if 'cover_url' not in st.session_state: st.session_state.cover_url = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80"
if 'active_template' not in st.session_state: st.session_state.active_template = None 
if 'topic_ideas' not in st.session_state: st.session_state.topic_ideas = [] 
if 'history_log' not in st.session_state: st.session_state.history_log = []

# --- 4. 辅助函数 ---
def get_client():
    if not MY_SECRET_KEY or "sk-" not in MY_SECRET_KEY: return None
    return OpenAI(api_key=MY_SECRET_KEY, base_url="https://api.deepseek.com")

def get_random_cover():
    urls = [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80",
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600&q=80",
        "https://images.unsplash.com/photo-1513258496098-916fae946a9e?w=600&q=80",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=600&q=80",
        "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600&q=80",
        "https://images.unsplash.com/photo-1491841550275-ad7854e35ca6?w=600&q=80"
    ]
    return random.choice(urls)

def markdown_to_html_simple(text):
    if not text: return ""
    html = text.replace("\n", "<br>")
    html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'^###\s+(.*)', r'<div style="font-weight:bold;font-size:16px;margin:10px 0;">\1</div>', html, flags=re.MULTILINE)
    return html

def set_template_as_reference(name, topic, pain, features):
    st.session_state.active_template = {'name': name, 'topic': topic, 'pain': pain, 'feat': features}
    st.toast(f"✅ 已挂载参考：{name}", icon="🔗")

def clear_reference():
    st.session_state.active_template = None
    st.rerun()

def use_idea(idea_text):
    st.session_state.input_topic = idea_text
    st.toast(f"💡 选题已填入：{idea_text}", icon="✨")

def check_seo(text):
    keywords = ["雅思", "托福", "四六级", "考研英语", "口语", "听力", "单词", "背诵", "逆袭", "干货", "资源", "免费", "模版", "高效", "避坑", "测评", "红黑榜", "教程", "步骤"]
    found = []
    for kw in keywords:
        if kw in text: found.append(kw)
    score = min(100, len(found) * 10 + 40)
    return score, found

def save_to_history(topic):
    entry = {
        "timestamp": datetime.datetime.now().strftime("%m-%d %H:%M"),
        "topic": topic,
        "result": st.session_state.generated_result,
        "comments": st.session_state.comments_data,
        "cover": st.session_state.cover_url,
        "cover_txt": st.session_state.cover_design
    }
    st.session_state.history_log.insert(0, entry)
    if len(st.session_state.history_log) > 10: st.session_state.history_log.pop()

def restore_history(idx):
    entry = st.session_state.history_log[idx]
    st.session_state.generated_result = entry['result']
    st.session_state.comments_data = entry['comments']
    st.session_state.cover_url = entry['cover']
    st.session_state.cover_design = entry.get('cover_txt', {"main":"", "sub":""})
    st.session_state.input_topic = entry['topic']
    score, _ = check_seo(entry['result'])
    st.session_state.seo_score = score
    st.toast("✅ 已恢复")

def extract_points_from_doc(doc_text):
    client = get_client()
    if not client: return []
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "提取产品卖点，只输出列表，不要编号。"}, {"role": "user", "content": f"文档：{doc_text[:1000]}"}],
            temperature=1.0
        )
        points = [l.strip("- ").strip() for l in resp.choices[0].message.content.split('\n') if l.strip()]
        return points[:10]
    except: return ["提取失败，请重试"]

def fetch_url_content(url):
    try:
        api_url = f"https://r.jina.ai/{url}"
        response = requests.get(api_url, timeout=10)
        return response.text[:2000] if response.status_code == 200 else None
    except: return None

# 🔥 核心生成函数
def generate_all(mode, note_type, seeding_strategy, topic, field1, field2, doc_content, selected_points, vibe, length, status, vocab_dict, ref_template=None):
    client = get_client()
    if not client: 
        st.error("请先输入 API Key")
        return
    
    # 变量初始化
    vocab_instruction = ""
    if vocab_dict['banned']: vocab_instruction += f"\n- 禁止使用：{vocab_dict['banned']}"
    if vocab_dict['required']: vocab_instruction += f"\n- 必须使用：{vocab_dict['required']}"
    
    status_instruction = ""
    type_instruction = ""
    tone_instruction = ""
    ref_p = ""

    if mode == "write":
        base_prompt = f"""
        你是一个小红书英语教育博主。人设：{vibe}。
        【字数控制】：{length}字左右。
        任务：写一篇关于【{topic}】的笔记。
        """
        
        if "正在备考" in status: status_instruction = "【视角：备考中】体现发现感，禁止说已上岸。"
        else: status_instruction = "【视角：已上岸】体现权威感，展示高分结果。"

        doc_hint = ""
        if selected_points: doc_hint = f"\n必须包含卖点：{','.join(selected_points)}"
        elif doc_content: doc_hint = f"\n参考文档：{doc_content[:500]}"

        if "种草" in note_type:
            if seeding_strategy == "⚖️ 竞品测评/拉踩":
                type_instruction = f"【模式：竞品测评】1.竞品分析[{field1}] 2.我的优势[{field2}] 3.结论避坑。{doc_hint}"
            else:
                type_instruction = f"【模式：单品体验】1.痛点[{field1}] 2.体验变化[{field2}] 3.相见恨晚。{doc_hint}"
        elif "教程" in note_type:
            type_instruction = f"【模式：硬核教程】针对[{field1}]人群，分步骤讲解[{field2}]。干货说明书风格，调用知识库。{doc_hint}"
        else:
            type_instruction = f"【模式：经验分享】背景[{field1}] -> 方法[{field2}] -> 真诚复盘。去功利化。"

        if "朴实" in vibe: tone_instruction = "禁止流行语，语气平实。"
        else: tone_instruction = "多用'亲测/建议收藏'，有网感。"
        
        if ref_template: ref_p = f"\n参考《{ref_template['name']}》的叙事结构。"

        base_prompt += f"{status_instruction} {type_instruction} {ref_p}\n【要求】：分段(<3行)，多用空行。{tone_instruction} {vocab_instruction}\n输出格式：### [标题]\n[正文]\n#标签"
        sys_p = base_prompt; user_p = f"主题：{topic}"
    else:
        sys_p = f"仿写大师。{vocab_instruction}"; user_p = f"参考：\n{field1}\n\n新主题：{topic}"
        
    try:
        resp1 = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}], temperature=1.3
        )
        st.session_state.generated_result = resp1.choices[0].message.content
        st.session_state.cover_url = get_random_cover()
        
        score, found = check_seo(st.session_state.generated_result)
        st.session_state.seo_score = score
        
        # 🔥 优化：只生成 JSON 数据 (评论+封面)，不生成废话
        strategy_prompt = f"""
        针对笔记主题“{topic}”，请直接输出一个 JSON 对象，不要Markdown代码块，包含以下字段：
        {{
            "cover_main": "封面主标题(6字内)",
            "cover_sub": "封面副标题(10字内)",
            "comments": [
                {{"user": "用户A(模拟提问)", "reply": "博主回复(引导)"}},
                {{"user": "用户B(模拟质疑)", "reply": "博主回复(解释)"}},
                {{"user": "用户C(模拟求资料)", "reply": "博主回复(私信)"}}
            ]
        }}
        """
        resp2 = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": strategy_prompt}], temperature=1.0, response_format={ "type": "json_object" }
        )
        
        try:
            data = json.loads(resp2.choices[0].message.content)
            st.session_state.cover_design = {"main": data.get("cover_main",""), "sub": data.get("cover_sub","")}
            st.session_state.comments_data = data.get("comments", [])
        except:
            st.session_state.cover_design = {"main": topic[:6], "sub": "点击查看"}
            st.session_state.comments_data = [{"user":"求分享","reply":"已私信"}]
        
        save_to_history(topic)
        
    except Exception as e: st.error(f"Error: {e}")

# ... (Brainstorm, Analyze, Refine) ...
def brainstorm_topics(niche, angle):
    client = get_client()
    if not client: return
    sys_p = f"选题策划。当前{datetime.datetime.now().month}月。"
    if angle == "🔥 蹭热点/时效性": angle_p = "结合考试季/假期。"
    elif angle == "💡 冷门蓝海/差异化": angle_p = "反直觉观点。"
    else: angle_p = "直击焦虑痛点。"
    user_p = f"领域：{niche}。切角：{angle_p}。5个爆款标题。"
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}], temperature=1.4
        )
        st.session_state.topic_ideas = [l.strip() for l in resp.choices[0].message.content.split('\n') if l.strip()][:5]
    except: pass

def analyze_text(text):
    client = get_client()
    if not client: return
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "system", "content": "拆解爆款逻辑。"}, {"role": "user", "content": f"分析：\n{text}"}], temperature=1.0
        )
        st.session_state.analysis_report = resp.choices[0].message.content
    except: pass

def refine_text(instruction):
    client = get_client()
    if not client or not st.session_state.generated_result: return
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "文案编辑。保留Markdown。"}, {"role": "user", "content": f"原代码:\n{st.session_state.generated_result}\n修改指令:\n{instruction}"}],
            temperature=1.1
        )
        st.session_state.generated_result = resp.choices[0].message.content
        st.rerun()
    except: pass

# --- 7. 主界面布局 ---
col_left, col_right = st.columns([1.1, 1], gap="large")

# === 👈 左侧：创作中心 ===
with col_left:
    st.subheader("✍️ 创作中心")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💡 选题", "✨ 创作", "📚 逻辑", "🦜 仿写", "🔍 拆解"])
    
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1: niche_input = st.text_input("输入领域", placeholder="例：雅思口语")
        with c2: angle_input = st.selectbox("切入视角", ["🔥 蹭热点/时效性", "😭 极致痛点/焦虑", "💡 冷门蓝海/差异化"])
        
        c3, c4 = st.columns(2)
        with c3:
            if st.button("🧠 头脑风暴", use_container_width=True): brainstorm_topics(niche_input, angle_input)
        with c4:
            if st.button("🔄 换一批", use_container_width=True): brainstorm_topics(niche_input, angle_input)
            
        if st.session_state.topic_ideas:
            for idea in st.session_state.topic_ideas:
                if st.button(f"📌 {idea}", use_container_width=True): use_idea(idea)

    with tab2:
        if st.session_state.active_template:
            c_info, c_btn = st.columns([4, 1])
            with c_info: st.markdown(f"""<div class="status-box-ref"><span>🔗 <b>模式：融合参考</b>（{st.session_state.active_template['name']}）</span></div>""", unsafe_allow_html=True)
            with c_btn: st.button("❌ 清除", on_click=clear_reference)
        else:
            st.markdown(f"""<div class="status-box-free"><span>✨ <b>模式：自由创作</b></span></div>""", unsafe_allow_html=True)

        with st.container(border=True):
            # 🔥 笔记模式选择
            note_type_label = st.selectbox("📝 笔记模式", ["🔴 强力种草 (带货/引流)", "🔵 纯经验分享 (复盘/晒分)", "🟡 硬核科普/教程 (干货/说明书)"])
            
            note_type = "其他"
            if "种草" in note_type_label: note_type = "种草/安利"
            elif "教程" in note_type_label: note_type = "科普/教程"
            else: note_type = "纯经验分享"
            
            seeding_strategy = "默认"
            if "种草" in note_type:
                seeding_strategy = st.radio("🛠️ 种草策略", ["❤️ 沉浸式单品体验", "⚖️ 竞品测评/拉踩"], horizontal=True)

            st.divider()
            
            # 🔥 动态 Placeholder
            default_topic_ph = "例：百词斩APP怎么用"
            if "种草" in note_type: default_topic_ph = "例：百词斩APP安利"
            elif "经验" in note_type: default_topic_ph = "例：四六级备考复盘"
            elif "教程" in note_type: default_topic_ph = "例：Notion做笔记教程"
            
            topic = st.text_input("📌 笔记主题", value=st.session_state.input_topic, placeholder=default_topic_ph)
            
            # 文档上传
            doc_content = ""
            selected_points = []
            if note_type in ["种草/安利", "科普/教程"]:
                uploaded_file = st.file_uploader("📂 上传产品文档 (TXT/MD)", type=['txt', 'md'])
                if uploaded_file:
                    doc_content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
                    if doc_content != st.session_state.uploaded_doc_content:
                        st.session_state.uploaded_doc_content = doc_content
                        with st.spinner("🤖 正在提取卖点..."):
                            st.session_state.extracted_points = extract_points_from_doc(doc_content)
                    if st.session_state.extracted_points:
                        selected_points = st.multiselect("✅ 勾选核心要点", options=st.session_state.extracted_points, default=st.session_state.extracted_points[:3])

            c1, c2 = st.columns(2)
            with c1:
                if "种草" in note_type:
                    label1, holder1 = ("🆚 竞品名单", "例：墨墨") if "竞品" in seeding_strategy else ("🎯 用户痛点", "例：背了忘")
                elif "教程" in note_type:
                    label1, holder1 = "👥 适用人群", "例：考研党"
                else:
                    label1, holder1 = "🏁 背景/现状", "例：四级420"
                field1 = st.text_input(label1, value=st.session_state.input_pain, placeholder=holder1)
                
            with c2:
                if "种草" in note_type:
                    label2, holder2 = ("🏆 我的优势", "例：免费") if "竞品" in seeding_strategy else ("✨ 核心卖点", "例：记忆曲线")
                elif "教程" in note_type:
                    label2, holder2 = "🧠 核心功能", "例：艾宾浩斯"
                else:
                    label2, holder2 = "💡 核心方法", "例：影子跟读"
                field2 = st.text_input(label2, value=st.session_state.input_features, placeholder=holder2)
            
            if st.button("✨ 生成笔记", type="primary", use_container_width=True):
                if not topic: st.warning("请输入主题")
                else:
                    with st.spinner("AI 正在组织语言..."):
                        vocab = {"banned": banned_words, "required": required_words}
                        generate_all("write", note_type, seeding_strategy, topic, field1, field2, doc_content, selected_points, selected_style_name, word_count, user_status, vocab, st.session_state.active_template)

    with tab3:
        with st.expander("📖 备考/上岸", expanded=True):
            cols = st.columns(3)
            if cols[0].button("🚀 冲刺逆袭"): set_template_as_reference("四六级逆袭", "四六级最后30天", "单词背不完", "三色刷题法")
            if cols[1].button("🧩 万能模版"): set_template_as_reference("雅思口语万能素材", "雅思口语", "考试卡壳", "一个素材套所有")
            if cols[2].button("🎯 技巧蒙题"): set_template_as_reference("考研阅读蒙题", "考研英语阅读", "读不懂文章", "逻辑词定位")
        with st.expander("📱 资源/APP"):
            cols = st.columns(3)
            if cols[0].button("📂 资料引流"): set_template_as_reference("外刊PDF分享", "外刊阅读", "资源难找", "免费分享")
            if cols[1].button("🛠️ 工具安利"): set_template_as_reference("背单词神器", "背单词", "枯燥", "游戏化背词")
            if cols[2].button("💣 避雷拔草"): set_template_as_reference("网红产品避雷", "文具避雷", "智商税", "亲测踩雷")

    with tab4:
        url_input = st.text_input("🔗 粘贴链接", placeholder="https://...")
        if st.button("🔍 解析"):
            fetched = fetch_url_content(url_input)
            if fetched: st.session_state.ref_content_buffer = fetched
        ref = st.text_area("文案内容", value=st.session_state.ref_content_buffer, height=150)
        new_t = st.text_input("📌 新主题", key="mimic_topic")
        if st.button("🦜 开始仿写", type="primary", use_container_width=True):
            vocab = {"banned": banned_words, "required": required_words}
            generate_all("copy", "", "", new_t, ref, "", "", word_count, "", vocab) 

    with tab5:
        analyze_text_input = st.text_area("📄 粘贴爆款文案", height=150)
        if st.button("开始拆解"): analyze_text(analyze_text_input)
        if st.session_state.analysis_report:
            st.markdown(f"""<div class="analysis-card">{markdown_to_html_simple(st.session_state.analysis_report)}</div>""", unsafe_allow_html=True)

    # 结果展示区
    if st.session_state.generated_result:
        st.markdown("### 🎉 生成结果")
        st.text_area("📋 纯文案", value=st.session_state.generated_result, height=300)
        
        seo_color = "#10b981" if st.session_state.seo_score > 80 else "#f59e0b"
        st.markdown(f"""<div class="seo-box"><b>🔍 SEO 得分：<span style='color:{seo_color}'>{st.session_state.seo_score}</span></b><br>热词覆盖：{' '.join([f'<span class="keyword-tag">{k}</span>' for k in check_seo(st.session_state.generated_result)[1]])}</div>""", unsafe_allow_html=True)
        
        st.markdown('<div class="magic-box"><b>✨ 魔法润色：</b></div>', unsafe_allow_html=True)
        r_cols = st.columns(4)
        if r_cols[0].button("➕ 加Emoji"): refine_text("增加Emoji")
        if r_cols[1].button("🔪 精简"): refine_text("精简")
        if r_cols[2].button("🔥 强情绪"): refine_text("增强情绪")
        if r_cols[3].button("🗣️ 说人话"): refine_text("改口语")

        # 🔥 只保留评论预设，去掉运营建议
        with st.expander("💬 评论区互动预设", expanded=True):
            if st.session_state.comments_data:
                for c in st.session_state.comments_data:
                    st.markdown(f"<div class='comment-card'><div class='comment-user'>👤 {c.get('user','用户')}</div><div class='comment-reply'>↪️ {c.get('reply','')}</div></div>", unsafe_allow_html=True)
            else:
                st.caption("AI 正在思考评论...")

# === 👉 右侧：预览 ===
with col_right:
    html_content = markdown_to_html_simple(st.session_state.generated_result) if st.session_state.generated_result else "<div style='text-align:center;padding-top:50%;color:#ccc;'>👋 点击左侧生成</div>"
    c_main = st.session_state.cover_design.get("main", "")
    c_sub = st.session_state.cover_design.get("sub", "")
    st.markdown(f"""
    <div style="display:flex; justify-content:center; align-items:center; height:100%;">
        <div class="iphone-mockup">
            <div class="status-bar"><span>19:54</span><span>5G</span></div>
            <div class="nav-bar">
                <span>❮</span>
                <div class="user-profile"><div class="avatar"></div><span class="username">XHS博主</span></div>
                <button class="follow-btn">关注</button>
            </div>
            <div class="screen-content">
                <div class="cover-container">
                    <img src="{st.session_state.cover_url}" class="cover-img">
                    <div class="cover-overlay">
                        <div class="cover-main-title">{c_main}</div>
                        <div class="cover-sub-title">{c_sub}</div>
                    </div>
                </div>
                <div class="note-content">{html_content}</div>
                <div class="date-loc">11-20 北京</div>
            </div>
            <div class="interaction-bar">
                <div class="comment-input">说点什么...</div>
                <div class="icons"><span>❤️</span><span>⭐</span><span>💬</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
