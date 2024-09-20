def reverse_no(num):
    negative = num < 0
    if negative:
        num = -num
    reverse = 0
    while num!=0:
        x= num%10
        reverse = x * 10 + 1
        x //= 10
    if negative:
        reverse = -reverse
    if reverse < -2**31 or reverse >2**31 -1:
        return 0
    return reverse

print(reverse_no(123))
print(reverse_no(-321))
print(reverse_no(-777))


# def reverse(x):
#     # Handle negative sign
#     negative = x < 0
#     if negative:
#         x = -x
    
#     reversed_num = 0
#     while x != 0:
#         # Extract the last digit
#         digit = x % 10
#         # Build the reversed number
#         reversed_num = reversed_num * 10 + digit
#         # Move to the next digit
#         x //= 10
    
#     # Handle negative and overflow cases
#     if negative:
#         reversed_num = -reversed_num
    
#     # Check for 32-bit overflow
#     if reversed_num < -2**31 or reversed_num > 2**31 - 1:
#         return 0
    
#     return reversed_num

# print(reverse(123))
# print(reverse(-321))
# print(reverse(-777))