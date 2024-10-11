

class RawMemBlockData:

    def __init__(self):
        self.one = [0, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.two = [0, 0, 0, 0, 69, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0]
        self.three = [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.four = [0, 0, 0, 0, 97, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.five = [0, 0, 0, 0, 136, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0]
        self.six = [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.seven = [0, 0, 0, 0, 180, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.eight = [1, 0, 0, 0, 255, 255, 255, 255, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.nine = [0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.total = self.one + self.two + self.three + self.four + self.five + self.six + self.seven + self.eight + self.nine
        self.one_ptr = 0
        self.two_ptr = len(self.one)
        self.three_ptr = self.two_ptr + len(self.two)
        self.four_ptr = self.three_ptr + len(self.three)
        self.five_ptr = self.four_ptr + len(self.four)
        self.six_ptr = self.five_ptr + len(self.five)
        self.seven_ptr = self.six_ptr + len(self.six)
        self.eight_ptr = self.seven_ptr + len(self.seven)
        self.nine_ptr = self.eight_ptr + len(self.eight)
