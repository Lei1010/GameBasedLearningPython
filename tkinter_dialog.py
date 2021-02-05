class test:
    def __init__(self, value=False):
        self.value = value
        self._a = [[], []]

    @cached_property
    def a(self):
        if self.value:
            self._a[0].append(1)
        else:
            self._a[0].append(2)
        return self._a

    def try_test(self):
        n = 3
        for i in range(n):
            print(len(self.a[0]))


new = test(False)
new.try_test()