import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Simulated weekly data for 6 weeks
weeks = [datetime.today() - timedelta(weeks=5-i) for i in range(6)]
week_labels = [week.strftime("%b %d") for week in weeks]

# Training stats for each level (example values)
beginner_accuracy = [40, 45, 50, 55, 60, 65]
intermediate_treble20 = [10, 12, 14, 16, 18, 20]
advanced_checkout = [20, 25, 30, 35, 40, 45]

# Create the chart
plt.figure(figsize=(12, 6))
plt.plot(week_labels, beginner_accuracy, marker='o', label='Beginner: 20 Accuracy (%)')
plt.plot(week_labels, intermediate_treble20, marker='s', label='Intermediate: Treble 20 Accuracy (%)')
plt.plot(week_labels, advanced_checkout, marker='^', label='Advanced: Checkout Success (%)')

# Chart details
plt.title("Darts Training Progress Over 6 Weeks")
plt.xlabel("Week")
plt.ylabel("Performance (%)")
plt.ylim(0, 100)
plt.grid(True)
plt.legend()
plt.tight_layout()

# Show the chart
plt.show()
