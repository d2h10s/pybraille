import numpy as np

a = np.identity(n=2, dtype=np.float32)
b = np.eye(N=2, M=2, k=1, order='C')
c = np.hstack((a,b))
d = np.vstack((a,b))
print(a)
print(b)
print(c)
print(d)