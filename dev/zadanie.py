import math
import matplotlib.pyplot as plt
            #number, base
#print(round(math.log(1/2, 364/365))+1)

for x in range(270):
    y=(364/365)**x
    plt.plot(x,y, 'o')
plt.plot((0, 260),(0.5,0.5), linewidth=1)
#plt.show()
def s(n):
    if n>1:
        return n*s(n-1)
    else:
        return 1

def k(x=10):
    k=1
    while True:
        if (s(x)/s(x-k))/(x**k)<0.5:
            print(k)
            print(s(x)/s(x-k)/(x**k))
            break
        k+=1
#k --> 7/10*8/10*9/10*10/10 < 1/2
k()
