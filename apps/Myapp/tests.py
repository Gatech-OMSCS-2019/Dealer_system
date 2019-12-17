from django.test import TestCase
import re
# # Create your tests here.
# PRICE_PATTERN = re.compile("^([0-9]+\.*[0-9]{,2})+(\/[0-9]+\.*[0-9]{,2})*$")
# result = PRICE_PATTERN.match("1234.1/123")
# print("12".split("/"))
var = ['a','b']
arr = ['a','c']
test = 'a/b/'
after = test.split('/')
if after[len(after) - 1] == '':
    print("i am here")
    after = after[0: len(after) - 1]
print(after)