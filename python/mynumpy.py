import numpy as np

a = np.array([1, 2, 3, 4, 5, 6])
#print(type(a))

b= np.array([[3,5],[99,4,53],[8,3,74,99]], dtype=object)

"""Key Points
Flexibility: Using dtype=object provides the flexibility to have arrays with elements of different types or shapes.
Performance: Arrays with dtype=object generally perform slower than arrays with a specific data type (like int or float) because they lose some of the low-level optimizations available to homogenous arrays.
Usage: dtype=object is particularly useful when dealing with data that cannot be easily represented as a standard NumPy array, such as nested lists of varying lengths.
When to Use dtype=object
Use dtype=object when you need to handle complex or heterogeneous data that doesn't fit neatly into NumPy's usual array constraints. For example:

Handling arrays with sublists of different lengths.
Combining elements of different types (e.g., numbers and strings).
Managing more complex data structures within a single array.
However, if you can structure your data to be homogeneous and of consistent shape, it is generally better to avoid dtype=object to leverage NumPy's performance optimizations.
"""
#print(b.shape)
# print(b[2][1])


c = np.array([[442,442,55,2],[3,5,2,44],[1,53,45,64]])
#print(c.shape)


#print(c[2,1])

#print(c.ndim)

d1= np.ones(2)
#print(d1)

d2 = np.empty(2)
#print(d2)  #[5.e-324 4.e-323]

d3  = np.arange(6)
print(d3)  #[0 1 2 3 4 5]

print(np.arange(1,10,2)) #[1 3 5 7 9]
x= np.array([[1,3,4],[4,5,2],[4,7,6]])
y= np.array([[8,9,7],[7,8,6],[6,5,4]])
d4 = np.concatenate((x,y))

print(d4)
