from __future__ import division
import math
def median_of_three(arr, left, last):
    """
    # Get the median of three of the array, changing the array as you do.
# arr =
# left =
# right = Right most index into list to find MOT on
    :param arr: Data Structure (List)
    :param left: Left most index into list to find MOT on.
    :param last: The last index in the subarray
    :return:
    """
    mid = (left + last) // 2
    if arr[last] < arr[left]:
        swap(arr, left, last)
    if arr[mid] < arr[left]:
        swap(arr, mid, left)
    if arr[last] < arr[mid]:
        swap(arr, last, mid)
    return mid


def median_of_3(arr, left, last):
    mid = (left + last) / 2
    if arr[last] < arr[left]:
        left, last = last, left
    if arr[mid] < arr[left]:
        mid, left = left, mid
    if arr[last] < arr[mid]:
        mid, last = last, mid
    return mid


def swap(arr, x, y):
    # Generic Swap for manipulating list data.
    temp = arr[x]
    arr[x] = arr[y]
    arr[y] = temp


def partition(arr, left, last):
    pivot_pos = median_of_three(arr, left, last)
    pivot = arr[pivot_pos]
    swap(arr, left, pivot_pos)
    pivot_pos = left

    for position in range(left + 1, last + 1):
        if arr[position] < pivot:
            swap(arr, position, pivot_pos + 1)
            swap(arr, pivot_pos, pivot_pos + 1)
            pivot_pos += 1
    return pivot_pos


def quicksort(arr, left, last):
    if left < last:
        p = partition(arr, left, last)
        quicksort(arr, left, p - 1)
        quicksort(arr, p + 1, last)


def left_child(i):
    return 2 * i + 1


def percolate_down(arr, index, size, begin=0):
    """

    :param arr: the Array
    :param index: is the logical index from which to percolate down
    :param size: Is the logical array size
    :param begin: The real index of the beginning of the (sub)Array
    :return:
    """
    walkdown(arr, index, size, begin)


def walkdown(arr, index, size, begin=0):
    """
    exchange parent with > child until parent in place
    :param arr: the Array
    :param index: is the logical index from which to percolate down
    :param size: Is the logical array size
    :param begin: The real index of the beginning of the (sub)Array
    :return:
    """

    ref = arr[begin + index]
    while left_child(index) < size:
        child = left_child(index)
        if child != size - 1 and arr[child + begin] < arr[child + 1 + begin]:
            child += 1
        if ref < arr[child + begin]:
            swap(arr, (index + begin), (child + begin))
            index = child
        else:
            break
    arr[begin + index] = ref


def heapsort(arr, left, right):
    """

    :param arr:
    :param left: The logical beginning of the array
    :param right: The logical ending of the array
    :return:
    """

    y = ((right - left) // 2)
    size = (right - left + 1)
    # first form the heap
    # y starts at last node to have child
    while y >= 0:
        # Build heap(rearrange array)
        walkdown(arr, y, size, left)
        y -= 1
    # y will now point to current last logical array index
    y = size - 1
    while y > 0:
        # swap root & B.R. leaf
        # Move current root to end
        swap(arr, (0 + left), (y + left))

        # Call walkdown on reduced heap
        walkdown(arr, 0, y, left)
        y -= 1


def introsort(arr, left, right, depth=None):
    """

    :param arr:
    :param left:
    :param right:
    :param depth:
    :return:
    """

    if depth is None:
        depth = math.log((len(arr) ** 2), 10)
    depth -= 1
    if depth > 0:
        # If depth reaches 0 the subArray gets HeapSorted
        if left < right:
            # test for Base Case Left == right.
            # Partition the array and get pivot
            p = partition(arr, left, right)

            # Sort the portion before the pivot point.
            introsort(arr, left, (p - 1), depth)

            # Sort the portion after the pivot point.
            introsort(arr, (p + 1), right, depth)
        else:
            if left < right:
                heapsort(arr, left, right)