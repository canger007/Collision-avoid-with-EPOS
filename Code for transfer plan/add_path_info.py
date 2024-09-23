import numpy as np
import pandas as pd

class Drone:
    def __init__(self, start_position, speed, tasks, drone_id):
        self.start_position = start_position
        self.current_position = start_position
        self.speed = speed
        self.tasks = tasks
        self.task_index = 0
        self.time_in_current_task = 0
        self.drone_id = drone_id
        self.current_pos_float = np.array(self.start_position, dtype=np.float64)

    def _to_float_coords(self, position):
        row, col = divmod(position, 8)
        return np.array([col * 200 + 100, row * 200 + 100], dtype=np.float64)

    def _to_grid_position(self, coords):
        col, row = coords // 200
        return int(row) * 8 + int(col)

    def move(self, time_step):
        if self.task_index < len(self.tasks):
            target, wait_time = self.tasks[self.task_index]
            wait_time *= 60  # Convert wait time from minutes to seconds
            target_coords = self._to_float_coords(target)
            direction = target_coords - self.current_pos_float
            distance = np.linalg.norm(direction)

            if distance > self.speed * time_step:
                direction = direction / distance
                self.current_pos_float += direction * self.speed * time_step
            else:
                self.current_pos_float = target_coords
                self.time_in_current_task += time_step
                if self.time_in_current_task >= wait_time:
                    self.task_index += 1
                    self.time_in_current_task = 0

            self.current_position = self._to_grid_position(self.current_pos_float)
            return self.current_position, self.drone_id
        return self.start_position, self.drone_id

def simulate(drones, grid_size, duration, time_step):
    num_steps = int(duration / time_step)
    drone_history = {drone.drone_id: np.zeros((num_steps, grid_size * grid_size), dtype=int) for drone in drones}
    for step in range(num_steps):
        current_time = step * time_step
        for drone in drones:
            position, drone_id = drone.move(time_step)
            if current_time % time_step < 1e-6:
                drone_history[drone_id][step, position] = 1  # Mark position at this time step
    return drone_history

def generate_csv(drone_histories, time_step, duration, costs):
    num_steps = int(duration / time_step)
    data = {}
    cost_data = []

    for drone_id, histories in drone_histories.items():
        for plan_id, history in enumerate(histories):
            key = f'drone_{drone_id}_plan_{plan_id}'
            data[key] = [''.join('0' for _ in range(num_steps)) for _ in range(64)]
            for region in range(64):
                region_data = np.zeros(num_steps, dtype=int)
                for step in range(min(num_steps, history.shape[0])):  # Ensure not to exceed history bounds
                    if history[step, region] == 1:
                        region_data[step] = 1
                data[key][region] = ''.join(map(str, region_data))
            cost_data.append([key, costs[plan_id][drone_id]])

    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = [f'region_{i}' for i in range(64)]
    df['cost'] = [item[1] for item in cost_data]
    df.to_csv('drone_positions.csv')

# 解析新的输入文件格式
file_path = 'generated-plans-execution.csv'
new_plans_execution = pd.read_csv(file_path)

# 定义网格大小和时间步长
grid_size = 8
time_step = 20

# 四个固定的起降站点坐标
stations = {
    0: (400, 400),
    1: (1200, 400),
    2: (400, 1200),
    3: (1200, 1200)
}

# 初始化任务和起始位置
station_indices = new_plans_execution.iloc[0, 1:].values.astype(int)

plans = []
orders = []
costs = []
for i in range(1, len(new_plans_execution), 3):
    plans.append(new_plans_execution.iloc[i, 1:].values)
    orders.append(new_plans_execution.iloc[i+1, 1:].values)
    costs.append(new_plans_execution.iloc[i+2, 1:].values.astype(float))

# 计算最长任务持续时间
max_duration = 0
drone_histories = {}
for i in range(32):
    histories = []
    for j in range(len(plans)):
        selected_plan = list(map(float, plans[j][i][1:-1].split(',')))
        cells_order = list(map(int, orders[j][i][1:-1].split(',')))
        station_index = station_indices[i]
        start_position = stations[station_index]
        tasks = [(cell, selected_plan[cell]) for cell in cells_order]
        total_task_time = sum([t[1] * 60 for t in tasks])
        max_duration = max(max_duration, total_task_time)
        drones = [Drone(start_position, 6.94, tasks, i)]
        histories.append(simulate(drones, grid_size, total_task_time, time_step)[i])
    drone_histories[i] = histories

# 模拟无人机
duration = max_duration + 300  # Add 5 minutes buffer

# 生成CSV文件
generate_csv(drone_histories, time_step, duration, costs)
