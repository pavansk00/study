def twosum(nums, tar):
    map ={}
    for index, num in enumerate(nums):
        diff = tar - num
        if diff in map:
            #return[diff, num]     #if you want numbers
            return[map[diff], index]      #if you want index
        map[num] = index
        print(type(map))
nums = [2, 7, 11, 15]
target = 9
print(twosum(nums, target)) 


"""
Step-by-Step Explanation
Let’s consider an example to illustrate this:

Example
Given nums = [2, 7, 11, 15] and target = 9, here’s what happens step-by-step:

Initial State:

num_map = {}
First Iteration (index = 0, num = 2):

Calculate diff = target - num = 9 - 2 = 7
Check if 7 is in num_map (it is not)
Store 2 and its index 0 in num_map: num_map[2] = 0
Now, num_map = {2: 0}
Second Iteration (index = 1, num = 7):

Calculate diff = target - num = 9 - 7 = 2
Check if 2 is in num_map (it is, and its index is 0)
Since we found the complement (2), return [num_map[2], index] which is [0, 1]
At the end of the second iteration, we have successfully found the indices of the two 
numbers that add up to the target. The key idea is that during each iteration, 
we store the current number and its index in the dictionary. 
This allows us to quickly check if the complement of the current number 
(the number needed to reach the target) has already been encountered.
"""






"""this is with without enum"""
# def two_sum(nums, tar):
#     map = {}
#     for i in range(len(nums)):
#         diff = tar - nums[i]
#         if diff in map:
#             return[map[diff], i]
#         map[nums[i]]=i

# # Example usage
# nums = [2, 7, 11, 15]
# target = 9
# print(two_sum(nums, target))










# def twoSum(nums, target):
#     # Create a hash map to store the difference and index
#     num_map = {}
    
#     # Iterate through the list
#     for index, num in enumerate(nums):
#         # Calculate the difference needed to reach the target
#         diff = target - num
        
#         # Check if the difference is already in the hash map
#         if diff in num_map:
#             # If it is, return the indices
#             return [num_map[diff], index]
        
#         # If it isn't, store the number and its index in the hash map
#         num_map[num] = index

# # Example usage
# nums = [2, 7, 11, 15]
# target = 9
# print(twoSum(nums, target))  # Output: [0, 1]
