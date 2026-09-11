vibration_points = [22, 24, 45, 48, 30, 28, 52]
def analyze_vibration(points_list, danger_limit):
    danger_steps = []
    for i in range(len(points_list)):
        if points_list[i] > danger_limit:
            danger_steps.append(i)
    return danger_steps
print(analyze_vibration(vibration_points, 40))
