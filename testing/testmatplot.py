import matplotlib.pyplot as plt

if __name__ == "__main__":
    
    x = [0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]
    y = [2,4,6,8,10,12,14,16,18,20]

    plt.plot(x,y)
    # plt.axis([0, len(x), 0, len(y)])
    plt.xlabel('time')
    plt.ylabel('angle')
    plt.show()