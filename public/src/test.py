class Bar:
    def __init__(self, name, number, children=None):
        self.name = name
        self.number = number
        self.children = children

    def get_info(self):
        data = f"Number: {self.number}"
        if self.children is not None:
            data = ''.join(list(map(lambda child: child.get_info(), self.children)))
        return f"<{self.name}>{data}</{self.name}>"

b4 = Bar("b4", "4")
b3 = Bar("b3", "3")
b2 = Bar("b2", "2", [b4])
b1 = Bar("b1", "1", [b2, b3])

print(b1.get_info())

# from test import *