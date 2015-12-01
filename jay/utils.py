def memoize(f):
    memo = {}
    def helper(*x):
        key = str(x)
        if key not in memo:
            memo[key] = f(*x)
        return memo[key]
    return helper
