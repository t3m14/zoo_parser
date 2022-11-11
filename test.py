class A():
    def __init__(self) -> None:
        self.afa = 1
class B(A):
    def __init__(self) -> None:
        super().__init__()
    def aaa(self):
        print(self.afa)
B().aaa()