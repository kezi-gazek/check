import streamlit as st
import pandas as pd
import datetime
import json
import os
from pathlib import Path

# 页面设置
st.set_page_config(
    page_title="任务线活动系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据存储路径
DATA_FILE = "task_submissions.json"

# 初始化数据
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

# 加载数据
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# 保存数据
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 初始化数据
init_data()

# 任务线选项
task_lines = {
    "走进真实线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"},
    "巴别塔线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"},
    "来硬的线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"},
    "健身线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"},
    "1+n团建线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"},
    "交友线": {"A": "任务A描述", "B": "任务B描述", "C": "任务C描述", "D": "任务D描述", "E": "任务E描述", "F": "任务F描述"}
}

# 主应用
def main():
    st.sidebar.title("导航")
    app_mode = st.sidebar.selectbox("选择模式", ["任务提交", "用户查询", "管理者模式"])
    
    if app_mode == "任务提交":
        task_submission()
    elif app_mode == "用户查询":
        user_query()
    elif app_mode == "管理者模式":
        admin_mode()

# 任务提交功能
def task_submission():
    st.title("任务线活动任务提交")
    
    with st.form("task_submission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("姓名")
            student_id = st.text_input("学号")
            team = st.selectbox("小分队", options=[f"第{i}小分队" for i in range(1, 11)])
        
        with col2:
            task_line = st.selectbox("任务线", options=list(task_lines.keys()))
            task = st.selectbox("任务", options=list(task_lines[task_line].keys()))
            submission_type = st.radio("提交方式", options=["文本", "图片"])
        
        # 根据提交类型显示不同的输入框
        if submission_type == "文本":
            submission_content = st.text_area("任务成果描述", height=150)
        else:
            submission_content = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
        
        submitted = st.form_submit_button("提交任务")
        
        if submitted:
            if not name or not student_id:
                st.error("请填写姓名和学号")
                return
                
            # 创建提交记录
            submission = {
                "id": len(load_data()) + 1,
                "name": name,
                "student_id": student_id,
                "team": team,
                "task_line": task_line,
                "task": task,
                "submission_type": submission_type,
                "submission_content": "文本内容" if submission_type == "文本" else "图片文件",
                "submission_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "待审核"
            }
            
            # 保存数据
            data = load_data()
            data.append(submission)
            save_data(data)
            
            st.success("您的任务成果已经进入审核阶段，请耐心等待")
            
            # 如果是图片，保存到本地
            if submission_type == "图片" and submission_content is not None:
                # 创建用户文件夹
                user_dir = f"submissions/{student_id}_{name}"
                os.makedirs(user_dir, exist_ok=True)
                
                # 保存图片
                file_ext = submission_content.name.split(".")[-1]
                file_name = f"{task_line}_{task}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
                with open(f"{user_dir}/{file_name}", "wb") as f:
                    f.write(submission_content.getbuffer())

# 用户查询功能
def user_query():
    st.title("任务提交记录查询")
    
    with st.form("user_query_form"):
        name = st.text_input("姓名")
        student_id = st.text_input("学号")
        submitted = st.form_submit_button("查询")
        
        if submitted:
            if not name or not student_id:
                st.error("请填写姓名和学号")
                return
                
            data = load_data()
            user_submissions = [s for s in data if s["name"] == name and s["student_id"] == student_id]
            
            if not user_submissions:
                st.info("未找到您的任务提交记录")
            else:
                st.subheader(f"{name} ({student_id}) 的任务提交记录")
                
                # 转换为DataFrame以便显示
                df = pd.DataFrame(user_submissions)
                df = df[["task_line", "task", "submission_time", "status"]]
                st.dataframe(df)

# 管理者模式
def admin_mode():
    st.title("管理者模式")
    
    password = st.text_input("请输入密码", type="password")
    
    if password != "lovehearter":
        st.warning("请输入正确的密码")
        return
        
    st.success("已进入管理者模式")
    
    data = load_data()
    
    if not data:
        st.info("尚无任务提交记录")
        return
        
    # 显示所有提交记录
    st.subheader("所有任务提交记录")
    
    df = pd.DataFrame(data)
    
    # 添加审核复选框
    for i, row in df.iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 2])
        
        with col1:
            st.write(row["name"])
        with col2:
            st.write(row["student_id"])
        with col3:
            st.write(row["team"])
        with col4:
            st.write(row["task_line"])
        with col5:
            st.write(row["task"])
        with col6:
            st.write(row["submission_time"])
        with col7:
            status = st.selectbox(
                f"状态_{row['id']}",
                options=["待审核", "审核通过", "审核不通过"],
                index=0 if row["status"] == "待审核" else 1 if row["status"] == "审核通过" else 2,
                key=f"status_{row['id']}"
            )
        with col8:
            if st.button("查看详情", key=f"detail_{row['id']}"):
                st.session_state[f"show_detail_{row['id']}"] = not st.session_state.get(f"show_detail_{row['id']}", False)
            
            if st.session_state.get(f"show_detail_{row['id']}", False):
                st.write(f"提交方式: {row['submission_type']}")
                if row['submission_type'] == "文本":
                    st.text_area("提交内容", value=row.get('submission_content', ''), height=100, key=f"content_{row['id']}")
                else:
                    # 尝试显示图片
                    user_dir = f"submissions/{row['student_id']}_{row['name']}"
                    if os.path.exists(user_dir):
                        files = os.listdir(user_dir)
                        matching_files = [f for f in files if f.startswith(f"{row['task_line']}_{row['task']}")]
                        if matching_files:
                            latest_file = sorted(matching_files)[-1]  # 获取最新的文件
                            st.image(f"{user_dir}/{latest_file}")
    
    # 保存审核结果
    if st.button("保存审核结果"):
        for i, row in df.iterrows():
            new_status = st.session_state.get(f"status_{row['id']}", row["status"])
            data[i]["status"] = new_status
        
        save_data(data)
        st.success("审核结果已保存")

if __name__ == "__main__":
    main()