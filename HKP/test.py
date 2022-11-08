class Test:
    def __init__(self):
        print("start")
        
    def __del__(self):
        print("del")
        
test = Test()
del test