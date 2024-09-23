import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 读取文件
drone_data = pd.read_csv('drone_positions.csv')
plan_data = pd.read_csv('old-selected-plans.csv')

# 遍历每个Run，找到最后一次迭代，并处理数据
collision_count_per_run = []

for run in plan_data['Run'].unique():
    # 1. 获取每次Run最后一次迭代的计划
    last_iteration = plan_data[plan_data['Run'] == run].sort_values(by='Iteration').iloc[-1]

    # 2. 根据agent选择的计划index从drone_positions中提取计划的01字符串
    selected_plans = []
    for agent in [col for col in plan_data.columns if 'agent-' in col]:
        plan_index = last_iteration[agent]

        # 在 drone_data 的第一列中找到匹配的无人机和计划
        agent_plan_row = drone_data[drone_data.iloc[:, 0] == f'drone_{agent.split("-")[-1]}_plan_{plan_index}']

        if not agent_plan_row.empty:
            # 提取计划的 01 字符串 (从第2列到倒数第二列，因为第一列是无人机/计划名称，最后一列是cost)
            plan = agent_plan_row.iloc[0, 1:-1]
            selected_plans.append([list(map(int, region)) for region in plan.values])  # 转换为二维列表

    # 3. 对所有agent的01字符串逐位相加，确保得到二维数组
    summed_plans = np.sum(np.array(selected_plans, dtype=np.float64), axis=0)

    # 4. 统计可能发生碰撞的次数（无人机数量大于1的格子）
   
    collisions = np.sum(summed_plans > 1)

    # 将Run和对应的碰撞次数添加到列表中
    collision_count_per_run.append((run, collisions))

    # 5. 生成热力图，确保输入是二维数组
    plt.figure(figsize=(10, 8))
    sns.heatmap(summed_plans, cmap="YlOrRd", cbar=True)
    plt.title(f'Map - Run {run}')
    plt.xlabel('Time point')
    plt.ylabel('Area')

    # 6. 在图上添加碰撞次数标注
    plt.text(0.5, -0.1, f'Collision Number: {collisions}', fontsize=12, color='black',
             ha='center', va='center', transform=plt.gca().transAxes)

    # 7. 保存图像为文件
    plt.savefig(f'Run_{run}_heatmap_with_collisions.png', bbox_inches='tight')

    # 显示图像
    plt.show()

# 输出每次Run的碰撞统计
collision_df = pd.DataFrame(collision_count_per_run, columns=['Run', 'Collisions'])
print("Collision Number：")
print(collision_df)

# # 如果需要，显示碰撞统计结果
# import ace_tools as tools;
#
# tools.display_dataframe_to_user(name="碰撞统计", dataframe=collision_df)
