Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import random
import math
import time
import matplotlib.pyplot as plt

# توليد 1000 نقطة عشوائية
def generate_random_points(n=1000, x_range=(-100, 100), y_range=(-100, 100)):
    points = []
    for _ in range(n):
        x = random.uniform(x_range[0], x_range[1])
        y = random.uniform(y_range[0], y_range[1])
        points.append((x, y))
    return points

# حساب المسافة بين نقطتين
def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

# حساب جميع المسافات بين كل زوج من النقاط
def calculate_all_distances(points):
    distances = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = distance(points[i], points[j])
            distances.append((points[i], points[j], dist))
    return distances

# رسم النقاط مع إبراز أقرب زوج
def plot_points(points, closest_pair=None):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    
    plt.scatter(x, y, c='blue', s=10, label='النقاط')
    
    if closest_pair:
        p1, p2 = closest_pair
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-', label='أقرب زوج')
        plt.scatter([p1[0], p2[0]], [p1[1], p2[1]], c='red', s=50, label='أقرب نقاط')
...     
...     plt.xlabel('X')
...     plt.ylabel('Y')
...     plt.legend()
...     plt.title('توزيع 1000 نقطة عشوائية مع أقرب زوج')
...     plt.grid(True)
...     plt.show()
... 
... # البرنامج الرئيسي
... def main():
...     start_time = time.time()
...     
...     # توليد النقاط
...     points = generate_random_points()
...     
...     # حساب جميع المسافات
...     distances = calculate_all_distances(points)
...     
...     # إحصائيات
...     if distances:
...         print(f"عدد المسافات المحسوبة: {len(distances)}")
...         min_distance = min(distances, key=lambda x: x[2])
...         print(f"أقصر مسافة: {min_distance[2]:.2f} بين النقطتين {min_distance[0]} و {min_distance[1]}")
...         max_distance = max(distances, key=lambda x: x[2])
...         print(f"أطول مسافة: {max_distance[2]:.2f} بين النقطتين {max_distance[0]} و {max_distance[1]}")
...         avg_distance = sum(d[2] for d in distances) / len(distances)
...         print(f"متوسط المسافات: {avg_distance:.2f}")
...         
...         # رسم النقاط مع إبراز أقرب زوج
...         plot_points(points, closest_pair=(min_distance[0], min_distance[1]))
...     
...     # زمن التنفيذ
...     execution_time = time.time() - start_time
...     print(f"زمن التنفيذ: {execution_time:.4f} ثانية")
... 
... if __name__ == "__main__":
