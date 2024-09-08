dictionary="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
length = len(dictionary)
def int_to_string(x:int) -> str:
    res = ""
    while x > 0:
        res = dictionary[x % length] + res
        x //= length
    return res

def string_to_int(x:str) -> int:
    res = 0
    for i in range(len(x)):
        res += dictionary.index(x[i]) * (length**(len(x)-i-1))
    return res