import streamlit as st
import pandas as pd
import datetime
import json
import os
from pathlib import Path
import uuid

# 页面设置
st.set_page_config(
    page_title="任务线活动系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据存储路径
DATA_FILE = "task_submissions.json"
SUBMISSIONS_DIR = "submissions"

# 确保提交目录存在
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)

# 初始化数据
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# 加载数据
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 保存数据
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 删除记录
def delete_record(record_id):
    data = load_data()
    # 找到要删除的记录
    record_to_delete = None
    for record in data:
        if record["id"] == record_id:
            record_to_delete = record
            break
    
    if record_to_delete:
        # 如果是图片提交，删除图片文件
        if record_to_delete["submission_type"] == "图片" and "file_path" in record_to_delete:
            try:
                if os.path.exists(record_to_delete["file_path"]):
                    os.remove(record_to_delete["file_path"])
            except Exception as e:
                st.error(f"删除文件时出错: {e}")
        
        # 从数据中删除记录
        data = [record for record in data if record["id"] != record_id]
        save_data(data)
        return True
    return False

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
                
            # 生成唯一ID
            submission_id = str(uuid.uuid4())
            
            # 创建提交记录
            submission = {
                "id": submission_id,
                "name": name,
                "student_id": student_id,
                "team": team,
                "task_line": task_line,
                "task": task,
                "submission_type": submission_type,
                "submission_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "待审核"
            }
            
            # 处理提交内容
            if submission_type == "文本":
                submission["submission_content"] = submission_content
            else:  # 图片
                if submission_content is not None:
                    # 创建文件名
                    file_ext = submission_content.name.split(".")[-1]
                    file_name = f"{student_id}_{name}_{task_line}_{task}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
                    file_path = os.path.join(SUBMISSIONS_DIR, file_name)
                    
                    # 保存图片
                    with open(file_path, "wb") as f:
                        f.write(submission_content.getbuffer())
                    
                    submission["file_path"] = file_path
                    submission["submission_content"] = f"图片已上传: {file_name}"
                else:
                    st.error("请上传图片文件")
                    return
            
            # 保存数据
            data = load_data()
            data.append(submission)
            save_data(data)
            
            st.success("您的任务成果已经进入审核阶段，请耐心等待")

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
                
                for submission in user_submissions:
                    with st.expander(f"{submission['task_line']} - {submission['task']} ({submission['submission_time']}) - {submission['status']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"小分队: {submission['team']}")
                            st.write(f"任务线: {submission['task_line']}")
                            st.write(f"任务: {submission['task']}")
                        
                        with col2:
                            st.write(f"提交时间: {submission['submission_time']}")
                            st.write(f"状态: {submission['status']}")
                            st.write(f"提交方式: {submission['submission_type']}")
                        
                        # 显示提交内容
                        st.write("提交内容:")
                        if submission["submission_type"] == "文本":
                            st.text_area("", value=submission.get("submission_content", "无内容"), height=100, disabled=True)
                        else:  # 图片
                            if "file_path" in submission and os.path.exists(submission["file_path"]):
                                st.image(submission["file_path"])
                            else:
                                st.warning("图片文件不存在或已被删除")
                        
                        # 删除按钮
                        if st.button("删除此记录", key=f"delete_user_{submission['id']}"):
                            if delete_record(submission["id"]):
                                st.success("记录已删除")
                                st.experimental_rerun()
                            else:
                                st.error("删除记录失败")

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
    
    # 创建两个标签页：待审核和已通过
    tab1, tab2 = st.tabs(["待审核任务记录", "已审批通过任务记录"])
    
    with tab1:
        st.subheader("待审核任务记录（包括审批不通过的任务）")
        
        # 筛选待审核和审核不通过的记录
        pending_data = [record for record in data if record["status"] != "审核通过"]
        
        if not pending_data:
            st.info("暂无待审核任务")
        else:
            # 按提交时间排序
            pending_data.sort(key=lambda x: x["submission_time"], reverse=True)
            
            for record in pending_data:
                with st.expander(f"{record['name']} - {record['task_line']} - {record['task']} ({record['submission_time']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"姓名: {record['name']}")
                        st.write(f"学号: {record['student_id']}")
                        st.write(f"小分队: {record['team']}")
                        st.write(f"任务线: {record['task_line']}")
                    
                    with col2:
                        st.write(f"任务: {record['task']}")
                        st.write(f"提交时间: {record['submission_time']}")
                        st.write(f"提交方式: {record['submission_type']}")
                        st.write(f"当前状态: {record['status']}")
                        
                        # 状态选择
                        new_status = st.selectbox(
                            "审核状态",
                            options=["待审核", "审核通过", "审核不通过"],
                            index=0 if record["status"] == "待审核" else 1 if record["status"] == "审核通过" else 2,
                            key=f"status_{record['id']}"
                        )
                    
                    # 显示提交内容
                    st.write("提交内容:")
                    if record["submission_type"] == "文本":
                        st.text_area("", value=record.get("submission_content", "无内容"), height=100, disabled=True)
                    else:  # 图片
                        if "file_path" in record and os.path.exists(record["file_path"]):
                            st.image(record["file_path"])
                        else:
                            st.warning("图片文件不存在或已被删除")
                    
                    # 审核按钮和删除按钮
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("保存审核结果", key=f"save_{record['id']}"):
                            data = load_data()
                            for d in data:
                                if d["id"] == record["id"]:
                                    d["status"] = new_status
                                    break
                            save_data(data)
                            st.success("审核结果已保存")
                            st.experimental_rerun()
                    
                    with col_btn2:
                        if st.button("删除此记录", key=f"delete_{record['id']}"):
                            if delete_record(record["id"]):
                                st.success("记录已删除")
                                st.experimental_rerun()
                            else:
                                st.error("删除记录失败")
    
    with tab2:
        st.subheader("已审批通过任务记录")
        
        # 筛选已审核通过的记录
        approved_data = [record for record in data if record["status"] == "审核通过"]
        
        if not approved_data:
            st.info("暂无已审核通过的任务")
        else:
            # 按小队分组，小队内部按姓名分组
            teams = sorted(set(record["team"] for record in approved_data))
            
            for team in teams:
                st.subheader(f"{team}")
                
                # 获取该小队的记录
                team_records = [record for record in approved_data if record["team"] == team]
                # 按姓名排序
                team_records.sort(key=lambda x: x["name"])
                
                for record in team_records:
                    with st.expander(f"{record['name']} - {record['task_line']} - {record['task']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"姓名: {record['name']}")
                            st.write(f"学号: {record['student_id']}")
                            st.write(f"任务线: {record['task_line']}")
                        
                        with col2:
                            st.write(f"任务: {record['task']}")
                            st.write(f"提交时间: {record['submission_time']}")
                            st.write(f"提交方式: {record['submission_type']}")
                        
                        # 显示提交内容
                        st.write("提交内容:")
                        if record["submission_type"] == "文本":
                            st.text_area("", value=record.get("submission_content", "无内容"), height=100, disabled=True)
                        else:  # 图片
                            if "file_path" in record and os.path.exists(record["file_path"]):
                                st.image(record["file_path"])
                            else:
                                st.warning("图片文件不存在或已被删除")
                        
                        # 删除按钮
                        if st.button("删除此记录", key=f"delete_approved_{record['id']}"):
                            if delete_record(record["id"]):
                                st.success("记录已删除")
                                st.experimental_rerun()
                            else:
                                st.error("删除记录失败")

if __name__ == "__main__":
    main()
