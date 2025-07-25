
import random

class Order:
    def __init__(self, order_id, value):
        self.order_id = order_id
        self.value = value

    def __repr__(self):
        return f"{self.order_id}: {self.value}"

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].value <= right[j].value:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]

def three_way_quicksort(arr, low, high):
    if low >= high:
        return
    pivot = arr[low].value
    lt, i, gt = low, low + 1, high
    while i <= gt:
        if arr[i].value < pivot:
            arr[i], arr[lt] = arr[lt], arr[i]
            lt += 1
            i += 1
        elif arr[i].value > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    three_way_quicksort(arr, low, lt - 1)
    three_way_quicksort(arr, gt + 1, high)

def generate_orders():
    orders = []
    for i in range(5000):
        orders.append(Order(f"ORD{10000 + i}", 1000 + i))
    for i in range(5000):
        orders.append(Order(f"ORD{15000 + i}", random.randint(1000, 9999)))
    return orders

def main():
    print("Sorting 10,000 Orders with Merge Sort and 3-way QuickSort:")
    orders = generate_orders()
    sorted_orders = merge_sort(orders.copy())
    print("First 5 sorted orders (MergeSort):", sorted_orders[:5])
    three_way_quicksort(orders, 0, len(orders) - 1)
    print("First 5 sorted orders (3-way QuickSort):", orders[:5])

if __name__ == "__main__":
    main()
