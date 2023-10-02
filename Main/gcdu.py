import math

def prime_factors(n):
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

max_prime_factors = 0
number_with_max_prime_factors = 0

for i in range(1, int(math.pow(10, 9)) + 1):
    num_prime_factors = len(set(prime_factors(i)))
    if num_prime_factors > max_prime_factors:
        max_prime_factors = num_prime_factors
        number_with_max_prime_factors = i

print("Số có nhiều ước số nguyên tố nhất: ", number_with_max_prime_factors)
print("Số lượng ước số nguyên tố: ", max_prime_factors)

