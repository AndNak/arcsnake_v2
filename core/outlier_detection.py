import numpy as np

class detectOutlier:
    counter = 0
    firstFill = False

    def __init__(self, arrlen, sigmamult):
        self.sigmamult = sigmamult
        self.arrlen = arrlen
        self.arr = np.array([])

    def add(self, value):
        if self.arr.size < self.arrlen and self.firstFill is False:
            self.arr = np.append(self.arr, value)
        else:
            firstFill = True
            mean = np.mean(self.arr)
            std = np.std(self.arr)

            if (value < mean + self.sigmamult * std) and (value > mean - self.sigmamult * std):
                if (self.counter > self.arrlen-1):
                    self.counter = 0
                self.arr[self.counter] = value
                self.counter+=1
                # print("added to array!")
                print(f"array: {self.arr} , mean: {mean}, std: {std}")
                return True
            else:
                print("disregarded number...")
                return False
        
            

    
