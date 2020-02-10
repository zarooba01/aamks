import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline

x = [x/10 for x in range(9)]
y = [57, 41, 28, 22, 18, 17, 16, 14,11]
y2 = [i/57*100 for i in y]
xnew = np.linspace(0,1, 300)
spl = make_interp_spline(x, y2, k=3)
y_smooth = spl(xnew)
plt.plot(xnew,y_smooth)
plt.axis([0, 0.9, 0, 100])
plt.xlabel("Density [m^2/m^2]")
plt.ylabel("Speed [%]")
plt.show()
#for x,y in zip(xnew, y_smooth):
    #print(x,y)
# Fave ludzi/s
# zmienna ilość ludzi ewakuowanych schodami
D = 10
Pf = [i for i in range(400)]
Fave = [0.42*(i/D)**(1/3) for i in Pf]
plt.plot(Pf,Fave)
plt.xlabel("Liczba ludzi")
plt.ylabel("Fave")
plt.show()
# zmienna odległość do wyjścia
Pf = 50
D = [i for i in range(1,400)]
Fave = [0.42*(Pf/i)**(1/3) for i in D]
plt.plot(D,Fave)
plt.xlabel("Odległość do wyjścia")
plt.ylabel("Fave")
plt.show()
