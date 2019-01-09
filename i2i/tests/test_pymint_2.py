from i2i.pymint import mint_of_instance_method, mint_many


class TestObj():
    constarg: str = ''

    def __init__(self, constarg: str):
        print(constarg)
        self.constarg = constarg

    def methodnum(self, methodarg1: int) -> int:
        print(methodarg1)
        return methodarg1 + 1

    def methodstr(self, methodarg2: str = 'hi') -> str:
        print(methodarg2)
        return methodarg2 + ' test ' + self.constarg


testobj = TestObj('value')

minted = mint_of_instance_method(TestObj, TestObj.methodnum)

print(minted)

class_mint = mint_many(TestObj)

print(class_mint)
