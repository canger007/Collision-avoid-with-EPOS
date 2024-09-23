import os
import pandas as pd

# 1. 读取并解析 old-selected-plans.csv 文件
selected_plans_file = 'new-plan-selected.csv'  # 修改为实际路径
selected_plans_df = pd.read_csv(selected_plans_file)

# 2. 定义解析 agent_x.plans 文件的函数
def parse_agent_plans(plan_file_content):
    plans = {}
    for line in plan_file_content:
        cost, plan = line.split(':')
        cost = float(cost)
        plan_content = [float(num) for num in plan.strip().split(',')]
        plans[len(plans)] = (cost, plan_content)
    return plans

# 3. 设置 agent plans 文件夹路径
agent_plans_folder = 'agent-plans'  # 修改为实际的文件夹路径

# 4. 初始化存储所有 Run 结果的列表
runs_results = []

# 5. 遍历每个 Run
for run in selected_plans_df['Run'].unique():
    # 提取当前 Run 的最后一次迭代的所有 agent 计划编号
    last_iteration_df = selected_plans_df[(selected_plans_df['Run'] == run) & (selected_plans_df['Iteration'] == 39)]

    total_cost = 0.0
    total_plan = []

    # 6. 遍历所有 agent 的列
    for agent_column in last_iteration_df.columns:
        if "agent" in agent_column:  # 只处理 agent 列
            agent_number = agent_column.split('-')[1]  # 获取 agent 编号
            plan_number = last_iteration_df.iloc[0][agent_column]  # 获取该 agent 选中的计划编号

            # 构造对应 agent_x.plans 文件的路径
            agent_plan_file = os.path.join(agent_plans_folder, f'agent_{agent_number}.plans')

            # 读取并解析 agent_x.plans 文件
            with open(agent_plan_file, 'r') as file:
                agent_plans_content = file.readlines()

            agent_plans = parse_agent_plans(agent_plans_content)  # 解析该文件

            # 获取选定计划的 cost 和内容
            selected_plan_cost, selected_plan_content = agent_plans[int(plan_number)]

            # 累加 cost
            total_cost += selected_plan_cost

            # 累加计划内容
            if not total_plan:
                total_plan = selected_plan_content
            else:
                total_plan = [x + y for x, y in zip(total_plan, selected_plan_content)]

    # 将当前 Run 的结果添加到结果列表
    runs_results.append({
        'Run': run,
        'Total Cost': total_cost,
        'Total Plan': total_plan
    })

# 7. 创建 DataFrame 保存所有 Run 的结果
final_result_df = pd.DataFrame(runs_results)

# 8. 输出结果并保存为 CSV 文件
output_csv_file = 'NewPlan_result.csv'  # 修改为你希望保存的路径
final_result_df.to_csv(output_csv_file, index=False)

# 打印输出
print("Final result saved to:", output_csv_file)
print(final_result_df)
