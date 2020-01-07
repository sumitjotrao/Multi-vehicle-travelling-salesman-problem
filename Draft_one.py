from random import seed

from random import random

import math
D=250

seed(1)

a=[]
b=[]
order_co_ord={}
n=15
node=[i for i in range(1,n+1)]
#Tour=[i for i in range(1,6)]
Tour=[1,2,3]

for i in range(1,n+1):
    a.append((random())*100)
    b.append((random())*100)

for i in range(n):
    order_co_ord.update({i+1:(a[i],b[i])})


dist={}
for i in node:
    for j in node:
        dist.update({(i,j):math.sqrt(((order_co_ord[i][0]-order_co_ord[j][0])*(order_co_ord[i][0]-order_co_ord[j][0]))+((order_co_ord[i][1]-order_co_ord[j][1])*(order_co_ord[i][1]-order_co_ord[j][1])))})

print(dist)
from gurobipy import *


def subtourelim(model, where):
    if where == GRB.callback.MIPSOL:
      selected = []
        # for i in range(n):
      sol = model.cbGetSolution(model._y)
      for e in Tour:
        selected = tuplelist((i, j) for i, j,k in model._y.keys() if sol[i, j,k] > 0.5 if k==e)
        adjList = [[] for i in range(n+1)]
        for i, j in selected:
            adjList[i].append(j)
        # find the shortest cycle in the selected edge list
        components = subtour(adjList)
        print(components)
        count = 0
        if len(components) > 1:
            # add a subtour elimination constraint
            for component in components:

                if len(component) >= 2:
                    count += 1
            if count > 1:
                for component in components:
                    if (len(component) >= 2):
                        print('Add constraint for component: {}'.format(component))
                        m.cbLazy(
                            quicksum(t[i, j] for i in component for j in component if i != j ) <= len(component) - 1)
#
#
# # arcs = dist.keys()
# # print(arcs)
#
def subtour(adjList):
    discover = [0 for i in range(n+1)]
    components = []
    for i in range(n+1):
        component = []
        queue = []
        if discover[i] == 0:
            discover[i] = 1
            component.append(i)
            queue.append(i)
            while queue:
                v = queue.pop(0)
                for u in adjList[v]:
                    if discover[u] == 0:
                        discover[u] = 1
                        component.append(u)
                        queue.append(u)
            components.append(component)
    return components


m=Model()


#x[i,j]=1 if node i is assigned to tour j
x={}
for i in node:
    for j in Tour:
        x[i,j]=m.addVar(vtype=GRB.BINARY,name='x'+str(i)+str(j))


#y[i,j,k]=1 if arc(i,j) is assigned to tour k
y={}
for i in node:
    for j in node:
        for k in Tour:
            y[i,j,k]=m.addVar(vtype=GRB.BINARY,name='y'+str(i)+str(j)+str(k))

t={}
for i in node:
    for j in node:
        t[i,j]=m.addVar(vtype=GRB.BINARY,name='t'+str(i)+str(j))


z={}

z=m.addVar(vtype=GRB.CONTINUOUS,name='z',obj=1)

m.update()
m.modelsense=GRB.MINIMIZE

m.addConstr(quicksum(y[i,j,k]*dist[i,j] for i in node for j in node for k in Tour)<=z)

#Every node should be assigned to atleast one tour

for i in range(2,len(node)+1):
    m.addConstr(quicksum(x[i,j] for j in Tour)==1)

#Total distance of a particular trip shall be less than D

for k in Tour:
    m.addConstr(quicksum(dist[i,j]*y[i,j,k] for i in node for j in node)<=D)


#Every node should have exactly one edge leaving

for i in range(2,len(node)+1):
    m.addConstr(quicksum(y[i,j,k] for j in node for k in Tour)==1)

#Every node should have exactly one edge entering

for i in range(2,len(node)+1):
    m.addConstr(quicksum(y[j,i,k] for j in node for k in Tour)==1)


#Linking variable x and y
#
# for i in node:
#     for j in node:
#         for k in Tour:
#             m.addConstr((x[i,k]+x[j,k]-1)<=y[i,j,k])
#             m.addConstr(x[i,k]>=y[i,j,k])
#             m.addConstr(x[j,k] >= y[i, j, k])

#(y[i,i,k]=0
for i in node:
    m.addConstr(quicksum(y[i,i,k] for k in Tour)==0)

#for every node i the previous and next node shall be in same route
for i in range(2,len(node)+1):
    for k in Tour:
     m.addConstr(quicksum(y[i,j,k] for j in node)==quicksum(y[j,i,k] for j in node))

#linking x and y
for i in range(2,len(node)+1):
 for k in Tour:
    m.addConstr(x[i,k]==quicksum(y[i,j,k] for j in node))

#linking y and t
for i in node:
    for j in node:
        m.addConstr(quicksum(y[i,j,k] for k in Tour)==t[i,j])
#node 1 should appear in all route
for k in Tour:
  m.addConstr(x[1,k]==1)

#number of edges entering is equal to number of edges leaving
m.addConstr(quicksum(y[1,i,k] for i in node for k in Tour)==quicksum(y[i,1,k] for i in node for k in Tour))

#atleast one edge outgoing from node 1 in every tour
for k in Tour:
    m.addConstr(quicksum(y[1,j,k] for j in node)==1)

#atleast one edge incoming to node 1 in every tour
for k in Tour:
    m.addConstr(quicksum(y[j,1,k] for j in node)==1)


def print_sol():
    if m.status==GRB.status.OPTIMAL:
        for i in node:
            for k in Tour:
                if x[i,k].x>0.5:
                    print('x[%d,%d]=1'%(i,k))

        for i in node:
            for j in node:
                for k in Tour:
                    if y[i,j,k].x>0.5:
                        print('y[%d,%d,%d]=1'%(i,j,k))
        for i in node:
            for j in node:
                if t[i,j].x>0.5:
                    print('t[%d,%d]=1'%(i,j))
m._y = y
m.params.LazyConstraints = 1
m.optimize(subtourelim)

#m.optimize()
print_sol()





