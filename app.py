import streamlit as st
from openai import OpenAI
import random
import time
import requests
import datetime
import re
from io import StringIO

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="英语内容工场 v29.0",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 填入你的 Key 👇
# ==========================================
MY_SECRET_KEY = "在这里粘贴你的DeepSeekKey"
# ==========================================

# --- 2. CSS 样式 ---
st.markdown("""
<style>
    .stApp {font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;}
    #MainMenu, footer, header {visibility: hidden;}

    /* 📱 仿真手机 */
    .iphone-frame {
        width: 360px; height: 720px;
        background-color: white; border: 12px solid #1a1a1a; border-radius: 45px;
        margin: 0 auto; position: relative; overflow: hidden;
        box-shadow: 20px 20px 50px rgba(0,0,0,0.15);
    }
    .notch {
        position: absolute; top: 0; left: 50%; transform: translateX(-50%);
        width: 140px; height: 30px; background-color: #1a1a1a;
        border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; z-index: 100;
    }
    .screen-content {
        height: 100%; overflow-y: auto; scrollbar-width: none;
        padding-bottom: 40px; background-color: #fff;
    }
    .screen-content::-webkit-scrollbar { display: none; }

    /* 🖼️ 封面容器 */
    .cover-container {
        width: 100%; aspect-ratio: 3 / 4; overflow: hidden; position: relative;
        border-bottom: 1px solid #f0f0f0;
    }
    .cover-img { width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(0.9); }
    
    .cover-overlay {
        position: absolute; bottom: 20px; left: 15px; right: 15px;
        color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); pointer-events: none;
    }
    .cover-main-title {
        font-size: 26px; font-weight: 900; line-height: 1.2; margin-bottom: 5px;
        color: #ffeb3b; font-family: "Impact", sans-serif;
    }
    .cover-sub-title {
        font-size: 14px; font-weight: 500; background-color: rgba(0,0,0,0.6);
        display: inline-block; padding: 2px 8px; border-radius: 4px;
    }

    /* 📝 文字内容 */
    .xhs-title { font-weight: 800; font-size: 17px; margin: 15px 18px 10px 18px; color: #333; line-height: 1.4; }
    .xhs-body { font-size: 15px; line-height: 1.7; color: #333; padding: 0 18px 20px 18px; white-space: pre-wrap; word-wrap: break-word; }
    .xhs-tag { color: #13386c; margin-right: 4px; }

    /* 📌 状态栏 */
    .status-box-ref {
        background-color: #fffbeb; border: 1px solid #fcd34d; color: #92400e;
        padding: 8px 12px; border-radius: 6px; font-size: 13px;
        margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between;
    }
    .status-box-free {
        background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534;
        padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 15px;
    }
    
    /* 💬 评论区 */
    .comment-card {
        background-color: #f8fafc; border-radius: 8px; padding: 12px;
        margin-top: 10px; border: 1px solid #e2e8f0; font-size: 14px;
    }
    .comment-user { font-weight: bold; color: #475569; }
    .comment-reply { margin-top: 5px; padding-left: 10px; border-left: 2px solid #ff2442; color: #64748b; font-size: 13px; }
    
    /* 🔍 SEO 卡片 */
    .seo-box { background-color: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 8px; padding: 15px; margin-top: 15px; color: #064e3b; }
    .keyword-tag { display: inline-block; background: #fff; border: 1px solid #a7f3d0; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }

    .stButton button { border-radius: 8px; transition: all 0.2s; }
</style>
""", unsafe_allow_html=True)

# --- 3. 状态管理 ---
if 'input_topic' not in st.session_state: st.session_state.input_topic = ''
if 'input_pain' not in st.session_state: st.session_state.input_pain = ''
if 'input_features' not in st.session_state: st.session_state.input_features = ''
if 'ref_content_buffer' not in st.session_state: st.session_state.ref_content_buffer = ''
if 'uploaded_doc_content' not in st.session_state: st.session_state.uploaded_doc_content = '' # 新增：文档内容

if 'generated_result' not in st.session_state: st.session_state.generated_result = ''
if 'growth_advice' not in st.session_state: st.session_state.growth_advice = ''
if 'cover_design' not in st.session_state: st.session_state.cover_design = {"main": "", "sub": ""}
if 'comments_data' not in st.session_state: st.session_state.comments_data = []
if 'seo_score' not in st.session_state: st.session_state.seo_score = 0
if 'analysis_report' not in st.session_state: st.session_state.analysis_report = ''

if 'cover_url' not in st.session_state: st.session_state.cover_url = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80"
if 'active_template' not in st.session_state: st.session_state.active_template = None 
if 'topic_ideas' not in st.session_state: st.session_state.topic_ideas = []
if 'history_log' not in st.session_state: st.session_state.history_log = []

# --- 4. 辅助函数 ---
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
    html_out = ""
    lines = text.split('\n')
    title_found = False
    body_content = []
    for line in lines:
        line = line.strip()
        if not line: 
            body_content.append("<br>")
            continue
        if (line.startswith("###") or line.startswith("##")) and not title_found:
            clean_title = line.replace("#", "").strip()
            html_out += f'<div class="xhs-title">{clean_title}</div>'
            title_found = True
        elif line.startswith("- "):
            body_content.append(f"• {line[2:]}<br>")
        else:
            processed = line.replace("**", "<b>").replace("**", "</b>")
            if "#" in processed:
                parts = processed.split()
                new_parts = []
                for p in parts:
                    if p.startswith("#"): new_parts.append(f'<span class="xhs-tag">{p}</span>')
                    else: new_parts.append(p)
                processed = " ".join(new_parts)
            body_content.append(f"{processed}<br>")
    html_out += f'<div class="xhs-body">{"".join(body_content)}</div>'
    return html_out

def set_template_as_reference(name, topic, pain, features):
    st.session_state.active_template = {'name': name, 'topic': topic, 'pain': pain, 'feat': features}
    st.toast(f"✅ 已挂载参考：{name}", icon="🔗")

def clear_reference():
    st.session_state.active_template = None
    st.rerun()

def fetch_url_content(url):
    try:
        api_url = f"https://r.jina.ai/{url}"
        response = requests.get(api_url, timeout=10)
        return response.text[:2000] if response.status_code == 200 else None
    except: return None

def use_idea(idea_text):
    st.session_state.input_topic = idea_text
    st.toast(f"💡 选题已填入：{idea_text}", icon="✨")

def check_seo(text):
    keywords = ["雅思", "托福", "四六级", "考研英语", "口语", "听力", "单词", "背诵", "逆袭", "干货", "资源", "免费", "模版", "高效", "避坑", "测评", "红黑榜"]
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
        "advice": st.session_state.growth_advice,
        "cover": st.session_state.cover_url,
        "cover_txt": st.session_state.cover_design
    }
    st.session_state.history_log.insert(0, entry)
    if len(st.session_state.history_log) > 10: st.session_state.history_log.pop()

def restore_history(idx):
    entry = st.session_state.history_log[idx]
    st.session_state.generated_result = entry['result']
    st.session_state.comments_data = entry['comments']
    st.session_state.growth_advice = entry['advice']
    st.session_state.cover_url = entry['cover']
    st.session_state.cover_design = entry.get('cover_txt', {"main":"", "sub":""})
    st.session_state.input_topic = entry['topic']
    score, _ = check_seo(entry['result'])
    st.session_state.seo_score = score
    st.toast("✅ 已恢复")

# --- 5. 侧边栏 ---
with st.sidebar:
    st.title("🎓 英语内容工场")
    st.caption("v29.0 文档喂养版")
    
    # 🔥 新增：操作指南
    with st.expander("📖 新手操作指南 (点我)", expanded=False):
        st.markdown("""
        **1. 选模式**：想带货选“种草”，想晒分选“经验”。
        **2. 填内容**：输入主题，或在【📚 逻辑库】选一个模板。
        **3. 传文档**：如果有产品说明书，可在“种草模式”下上传TXT，AI会自动读。
        **4. 看结果**：右侧预览，左侧复制文案。
        **5. 搞运营**：查看下方的“评论区预设”和“运营建议”。
        """)
    
    if len(MY_SECRET_KEY) > 10:
        api_key = MY_SECRET_KEY
        st.success("✅ Key 已内置")
    else:
        api_key = st.text_input("🔑 输入 Key", type="password")
    
    if st.session_state.history_log:
        st.divider()
        st.markdown("### 📂 历史草稿")
        options = [f"{i+1}. {e['timestamp']} - {e['topic'][:6]}..." for i, e in enumerate(st.session_state.history_log)]
        selected_hist = st.selectbox("选择记录", range(len(options)), format_func=lambda x: options[x])
        if st.button("🔄 恢复此版本"): restore_history(selected_hist)

    st.divider()
    st.markdown("### 👱‍♀️ 博主身份")
    user_status = st.radio("选择状态", ["✅ 已上岸/高分大神", "🏃‍♀️ 正在备考/小白"])
    
    st.divider()
    st.markdown("### 🎭 人设风格")
    style_map = {
        "🎒 朴实学生党": {"desc": "无网感、不浮夸。语气平和实在。", "icon": "🎒"},
        "🎓 雅思/考研学霸": {"desc": "权威、高分。语气冷静，常用“底层逻辑”。", "icon": "🎓"},
        "🔥 逆袭特种兵": {"desc": "热血、鸡血。喜欢用感叹号！", "icon": "🔥"},
        "🗣️ 纯正英音党": {"desc": "优雅、高级。强调“腔调”、“氛围感”。", "icon": "🗣️"},
        "📝 极简笔记控": {"desc": "清爽、治愈。喜欢分点罗列。", "icon": "📝"},
        "👯‍♀️ 留学/考研搭子": {"desc": "亲切、陪伴感。用“宝子们”。", "icon": "👯‍♀️"}
    }
    selected_style_name = st.selectbox("选择风格", list(style_map.keys()))
    st.info(style_map[selected_style_name]['desc'])

    word_count = st.slider("📏 预估篇幅", 100, 1000, 400, 50)

    st.divider()
    with st.expander("🚫 私有词库", expanded=False):
        banned_words = st.text_area("🚫 禁用词", placeholder="首先 其次 总之")
        required_words = st.text_area("✅ 必用词", placeholder="绝绝子 闭眼冲")

# --- 6. AI 逻辑 ---
def get_client():
    if not api_key: return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def generate_all(mode, note_type, seeding_strategy, topic, field1, field2, doc_content, vibe, length, status, vocab_dict, ref_template=None):
    client = get_client()
    if not client: return
    
    vocab_instruction = ""
    if vocab_dict['banned']: vocab_instruction += f"\n- 禁止使用：{vocab_dict['banned']}"
    if vocab_dict['required']: vocab_instruction += f"\n- 必须使用：{vocab_dict['required']}"

    if mode == "write":
        base_prompt = f"""
        你是一个小红书英语教育博主。人设：{vibe}。
        【字数控制】：{length}字左右。
        任务：写一篇关于【{topic}】的笔记。
        """
        
        if "正在备考" in status:
            status_instruction = "【视角：备考中】禁止说已上岸，体现发现感和救命感。"
        else:
            status_instruction = "【视角：已上岸】展示高分结果，体现权威感。"

        # 🔥 策略逻辑分支 (加入文档内容)
        if note_type == "种草/安利":
            # 如果有文档，优先参考文档
            doc_hint = f"\n【📄 产品核心文档】：{doc_content}\n(请从中提取具体参数和功能亮点融入文案)" if doc_content else ""
            
            if seeding_strategy == "⚖️ 竞品测评/拉踩":
                type_instruction = f"""
                【模式：竞品测评】
                1. 结构：红黑榜/对比。
                2. 竞品分析：[{field1}]的缺点。
                3. 我的优势：自然引出[{topic}]。{doc_hint}
                """
            else:
                type_instruction = f"""
                【模式：单品沉浸体验】
                1. 痛点：[{field1}]。
                2. 体验：使用前后变化。{doc_hint}
                3. 共鸣：相见恨晚。
                """
        else:
            type_instruction = f"""
            【模式：纯经验分享】
            1. 背景：[{field1}]。
            2. 方法：[{field2}]。
            3. 去功利化：真诚分享。
            """

        if "朴实" in vibe: tone_instruction = "禁止流行语，语气平实像日记。"
        else: tone_instruction = "多用“亲测/建议收藏”，有网感。"
        
        if ref_template:
            base_prompt += f"\n【参考逻辑】：参考《{ref_template['name']}》的叙事结构。"

        base_prompt += f"""
        {status_instruction}
        {type_instruction}
        【通用要求】：
        1. 排版：分段(<3行)，多用空行，关键点列表化。
        2. {tone_instruction}
        3. {vocab_instruction}
        
        输出格式：### [标题]\n[正文]\n#标签
        """
        sys_p = base_prompt
        user_p = f"主题：{topic}"
        
    else: # 仿写
        sys_p = f"仿写大师。{vocab_instruction}"
        user_p = f"参考文本：\n{field1}\n\n新主题：{topic}"
        
    try:
        resp1 = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}], temperature=1.3
        )
        st.session_state.generated_result = resp1.choices[0].message.content
        st.session_state.cover_url = get_random_cover()
        
        # SEO
        score, found = check_seo(st.session_state.generated_result)
        st.session_state.seo_score = score
        
        # 🔥 优化：运营生成 (彻底解决内容冲突)
        # 使用明确的分隔符，分别请求 "建议" 和 "评论"
        strategy_prompt = f"""
        针对“{topic}”笔记，生成两部分内容，中间用 "===SPLIT===" 分隔：
        
        第一部分：【运营建议】
        1. 封面文案：主标题(6字内)+副标题(10字内)
        2. 3条简短发布建议(时间/话题)
        
        ===SPLIT===
        
        第二部分：【评论区剧本】(JSON格式)
        生成3个对象，包含user和reply。例如：
        [
            {{"user": "求资料", "reply": "私信了"}},
            {{"user": "好用吗", "reply": "亲测有效"}}
        ]
        """
        resp2 = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": strategy_prompt}], temperature=1.0
        )
        full_response = resp2.choices[0].message.content
        
        # 解析逻辑分离
        if "===SPLIT===" in full_response:
            parts = full_response.split("===SPLIT===")
            advice_part = parts[0].strip()
            comment_part = parts[1].strip()
        else:
            advice_part = full_response
            comment_part = "[]"

        # 1. 处理建议与封面
        st.session_state.growth_advice = advice_part
        cover_main, cover_sub = "英语逆袭", "干货分享"
        try:
            for l in advice_part.split('\n'):
                if "主标题" in l: cover_main = l.split("标题")[1].strip(":：")
                if "副标题" in l: cover_sub = l.split("标题")[1].strip(":：")
        except: pass
        st.session_state.cover_design = {"main": cover_main[:8], "sub": cover_sub[:12]}

        # 2. 处理评论 (尝试解析JSON，失败则正则)
        comments = []
        try:
            # 尝试清洗 JSON 字符串
            json_str = re.search(r'\[.*\]', comment_part, re.DOTALL)
            if json_str:
                comments = json.loads(json_str.group())
        except: 
            # 兜底
            comments = [{"user": "蹲后续", "reply": "关注不错过"}, {"user": "求分享", "reply": "已私信"}]
            
        st.session_state.comments_data = comments[:3]
        save_to_history(topic)
        
    except Exception as e: st.error(f"Error: {e}")

# ... (Brainstorm, Analyze, Refine 保持不变) ...
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
            model="deepseek-chat", messages=[{"role": "system", "content": "拆解爆款。"}, {"role": "user", "content": f"分析：\n{text}"}], temperature=1.0
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
            note_type_label = st.selectbox("📝 笔记模式", ["🔴 强力种草 (带货/引流)", "🔵 纯经验分享 (复盘/晒分)"])
            note_type = "种草/安利" if "强力种草" in note_type_label else "纯经验分享"
            
            # 🔥 策略选择
            seeding_strategy = "默认"
            if "种草" in note_type:
                seeding_strategy = st.radio("🛠️ 种草策略", ["❤️
