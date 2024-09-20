from functools import lru_cache



def febonacci(num):
    if num > 2:
        return num
    return febonacci(num-1) + febonacci(num -2)


def main():
    result = febonacci(122)
    print(result)

if __name__ ==  "__main__":
    main()