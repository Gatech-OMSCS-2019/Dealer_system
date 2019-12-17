class Person:

    def __init__(self, age,name=None):
        self.name = name
        self.age = age

class Yang(Person):
    pass

# def dict_to_tuple(dict):
#     return tuple(list(dict.values()))


# person = Person('Yang', None)
# temp = 'name'
# # print(person.temp)
# # print(dir(person))
# print(person.__dict__)
# field_values = person.__dict__
# for key, value in field_values.items():
#     if value is None and key != 'email':
#         print(f" {key} Cannot be Empty")
#
# print(dict_to_tuple(person.__dict__))

string = '''
hello world, I am {}
'''.format("yang")

print(string)