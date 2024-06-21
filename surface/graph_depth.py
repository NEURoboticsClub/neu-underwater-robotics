from matplotlib import pyplot as plt

with open('depth.csv', 'r') as f:
    data = f.readlines()

time = []
depth_numeric = []

for line in data:
    time.append(int(line.split(',')[1]))
    depth_numeric.append(float(line.split(',')[3].strip().split(' ')[0]))


plt.figure(figsize=(10, 6))
plt.plot(time, depth_numeric, marker='o', linestyle='-', color='b')
plt.title('Time vs Depth')
plt.xlabel('Time (milliseconds)')
plt.ylabel('Depth (meters)')
plt.grid(True)

plt.show()
