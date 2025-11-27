import streamlit as st
from openai import OpenAI
import random
import time
import requests
import datetime
import re
from io import StringIO
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="英语内容工场 v29.1",
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
if 'uploaded_doc_content' not in st.session_state: st.session_state.uploaded_doc_content = ''

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
    st.caption("v29.1 修复版")
    
    with st.expander("📖 新手操作指南", expanded=False):
        st.markdown("1. 选模式：种草或经验\n2. 填内容：输入或选模板\n3. 传文档：种草模式可上传txt\n4. 看结果：右侧预览，下方看评论预设")
    
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

        # 🔥 策略逻辑
        if note_type == "种草/安利":
            doc_hint = f"\n【📄 产品文档参考】：{doc_content}\n(提取文档参数亮点)" if doc_content else ""
            if seeding_strategy == "⚖️ 竞品测评/拉踩":
                type_instruction = f"【模式：竞品测评】1.竞品分析[{field1}] 2.我的优势[{field2}] 3.结论避坑。{doc_hint}"
            else:
                type_instruction = f"【模式：单品体验】1.痛点[{field1}] 2.体验变化[{field2}] 3.相见恨晚。{doc_hint}"
        else:
            type_instruction = f"【模式：经验分享】1.背景[{field1}] 2.方法[{field2}] 3.真诚分享。"

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
        
        score, found = check_seo(st.session_state.generated_result)
        st.session_state.seo_score = score
        
        # 运营生成 (逻辑分离)
        strategy_prompt = f"""
        针对“{topic}”笔记，生成两部分内容，中间用 "===SPLIT===" 分隔：
        Part1:【运营建议】1.封面文案(主标+副标) 2.发布建议
        ===SPLIT===
        Part2:【评论剧本】JSON格式 [{{user:"", reply:""}}] 生成3条
        """
        resp2 = client.chat.completions.create(
            model="deepseek-chat", messages=[{"role": "user", "content": strategy_prompt}], temperature=1.0
        )
        full_res = resp2.choices[0].message.content
        
        if "===SPLIT===" in full_res:
            advice_part, comment_part = full_res.split("===SPLIT===")
        else:
            advice_part, comment_part = full_res, "[]"

        st.session_state.growth_advice = advice_part.strip()
        
        # 解析封面
        c_main, c_sub = "英语逆袭", "干货分享"
        for l in advice_part.split('\n'):
            if "主标题" in l: c_main = l.split("标题")[1].strip(":：")
            if "副标题" in l: c_sub = l.split("标题")[1].strip(":：")
        st.session_state.cover_design = {"main": c_main[:8], "sub": c_sub[:12]}

        # 解析评论
        try:
            json_match = re.search(r'\[.*\]', comment_part, re.DOTALL)
            comments = json.loads(json_match.group()) if json_match else []
        except: 
            comments = [{"user":"求资料","reply":"已私信"}]
        st.session_state.comments_data = comments[:3]
        
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
            
            seeding_strategy = "默认"
            if "种草" in note_type:
                seeding_strategy = st.radio("🛠️ 种草策略", ["❤️ 沉浸式单品体验", "⚖️ 竞品测评/拉踩"], horizontal=True)

            st.divider()
            topic = st.text_input("📌 笔记主题", value=st.session_state.input_topic, placeholder="例：百词斩APP")
            
            # 文档上传
            doc_content = ""
            if "种草" in note_type:
                uploaded_file = st.file_uploader("📂 上传产品文档 (TXT/MD)", type=['txt', 'md'])
                if uploaded_file:
                    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                    doc_content = stringio.read()
                    st.caption(f"✅ 已读取：{len(doc_content)}字")

            c1, c2 = st.columns(2)
            with c1:
                if "种草" in note_type:
                    if "竞品" in seeding_strategy:
                        label1, holder1 = "🆚 竞品名单", "例：墨墨/不背"
                    else:
                        label1, holder1 = "🎯 用户痛点", "例：背了忘"
                else:
                    label1, holder1 = "🏁 背景/现状", "例：四级420"
                field1 = st.text_input(label1, value=st.session_state.input_pain, placeholder=holder1)
                
            with c2:
                if "种草" in note_type:
                    if "竞品" in seeding_strategy:
                        label2, holder2 = "🏆 我的优势", "例：免费"
                    else:
                        label2, holder2 = "✨ 核心卖点", "例：记忆曲线"
                else:
                    label2, holder2 = "💡 核心方法", "例：影子跟读"
                field2 = st.text_input(label2, value=st.session_state.input_features, placeholder=holder2)
            
            if st.button("✨ 生成笔记", type="primary", use_container_width=True):
                if not topic: st.warning("请输入主题")
                else:
                    with st.spinner("AI 正在组织语言..."):
                        vocab = {"banned": banned_words, "required": required_words}
                        generate_all("write", note_type, seeding_strategy, topic, field1, field2, doc_content, selected_style_name, word_count, user_status, vocab, st.session_state.active_template)

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

        with st.expander("💬 评论互动预设", expanded=True):
            if st.session_state.comments_data:
                for c in st.session_state.comments_data:
                    st.markdown(f"<div class='comment-card'><div class='comment-user'>👤 {c.get('user','用户')}</div><div class='comment-reply'>↪️ {c.get('reply','')}</div></div>", unsafe_allow_html=True)
        
        with st.expander("📈 运营建议"):
            st.markdown(markdown_to_html_simple(st.session_state.growth_advice), unsafe_allow_html=True)

# === 👉 右侧：预览 ===
with col_right:
    html_content = markdown_to_html_simple(st.session_state.generated_result) if st.session_state.generated_result else "<div style='text-align:center;padding-top:50%;color:#ccc;'>👋 点击左侧生成</div>"
    c_main = st.session_state.cover_design.get("main", "")
    c_sub = st.session_state.cover_design.get("sub", "")
    st.markdown(f"""
    <div style="display:flex; justify-content:center; align-items:center; height:100%;">
        <div class="iphone-frame">
            <div class="notch"></div>
            <div class="screen-content">
                <div class="cover-container">
                    <img src="{st.session_state.cover_url}" class="cover-img">
                    <div class="cover-overlay">
                        <div class="cover-main-title">{c_main}</div>
                        <div class="cover-sub-title">{c_sub}</div>
                    </div>
                </div>
                {html_content}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
