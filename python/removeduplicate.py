def removeDuplicates(nums):
    if not nums:
        return 0
    i = 0

    for j in  range(1, len(nums)):
        if nums[i] != nums[j]:
            i +=1
            nums[i] = nums[j]
    return i +1










# def removeDuplicates(nums):
#     if not nums:
#         return 0
    
#     i = 0  # slow pointer
    
#     for j in range(1, len(nums)):
#         if nums[j] != nums[i]:
#             i += 1
#             nums[i] = nums[j]
    
#     return i + 1

# Example usage
nums1 = [1, 1, 2]
print(removeDuplicates(nums1))  # Output: 2, nums1 will be [1, 2]

nums2 = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
print(removeDuplicates(nums2))  # Output: 5, nums2 will be [0, 1, 2, 3, 4]
