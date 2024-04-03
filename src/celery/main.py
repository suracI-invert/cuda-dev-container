from tasks import add, matmul
result = add.delay(4, 4)

print(result.get())

result = matmul(
    [[1.0] * 100 for _ in range(500)],
    [[5.0] * 300 for _ in range(100)]
)

c = result.get()

print(len(c))
print(len(c[0]))