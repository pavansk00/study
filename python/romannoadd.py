def roman_no_sum(nums):
    _map = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    result = 0
    priv_value = 0
    _lst = []

    for str in nums:
        curr_value = _map[str]
        if curr_value > priv_value:
            result += curr_value - 2 * priv_value
            _lst.append(curr_value - 2 * priv_value)
        else:
            result += curr_value
            _lst.append(curr_value)
        priv_value = curr_value
    return result, _lst

sum, _lst  = roman_no_sum("IX")
print(sum, _lst)

