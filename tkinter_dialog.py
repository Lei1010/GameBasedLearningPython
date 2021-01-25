class Alphabet:
    def __init__(self, shield=False):
        self.shield = shield
        self._value = None
        self.test = self.value[1]

        # getting the values

    @property
    def value(self):
        if self.shield:
            self._value = [1,2,3]
        else:
            self._value = [4,5,6]
        return self._value
        # setting the values

    def ok(self):
        print(self.value[1])


x = Alphabet(True)
print(x.value)
print(x.test)
x.ok()
