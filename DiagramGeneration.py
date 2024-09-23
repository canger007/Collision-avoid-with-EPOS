import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error

# 1. 读取结果文件和 sensing.target 文件
result_file = 'NewPlan_result.csv'  # 修改为你的结果文件路径
sensing_target_file = 'sensing.target'  # 修改为你的 sensing.target 文件路径

# 读取结果文件
results_df = pd.read_csv(result_file)

# 读取 sensing.target 文件
with open(sensing_target_file, 'r') as file:
    sensing_target = [float(num) for num in file.read().strip().split(',')]

# 将 sensing.target 转换为 8x8 的二维数组，表示 64 个区域的二维地图
sensing_target_map = np.array(sensing_target).reshape(8, 8)

# 生成 sensing.target 的热力图
plt.figure(figsize=(8, 6))
sns.heatmap(sensing_target_map, cmap='YlGnBu', annot=True, cbar=True)
plt.title('Sensing Target Heatmap')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')

# 保存 sensing.target 的热力图
plt.savefig('sensing_target_heatmap.png')
plt.show()

# 2. 遍历每个 Run 的结果，生成热力图并计算 MSE
for index, row in results_df.iterrows():
    run_number = row['Run']
    total_cost = row['Total Cost']
    total_plan = eval(row['Total Plan'])  # 将字符串形式的列表转换为实际列表

    # 将 total_plan 转换为 8x8 的二维数组
    plan_map = np.array(total_plan).reshape(8, 8)

    # 计算均方误差 (MSE)
    mse = mean_squared_error(sensing_target_map, plan_map)

    # 3. 生成热力图
    plt.figure(figsize=(8, 6))
    sns.heatmap(plan_map, cmap='YlGnBu', annot=True, cbar=True)
    plt.title(f'Run {run_number} - Total Cost: {total_cost:.2f} - MSE: {mse:.4f}')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')

    # 保存热力图为图片文件
    plt.savefig(f'heatmap_run_{run_number}.png')

    # 显示热力图
    plt.show()

    # 输出 MSE
    print(f'Run {run_number}: MSE = {mse:.4f}, Total Cost = {total_cost:.2f}')

