#coding=gbk
'''
��ѧ����ʽ��ƽ��
@author: Pecco
'''

import functools as ft
import fractions as fr
import numpy as np
import re

class Element():
    def __init__(self,string):
        amountList = [i for i in re.findall("[-\d]*", string) if i!=""]
        self.amount = amountList and amountList[0] or "1"
        self.ele = string.replace(self.amount,"")
        if self.amount:self.amount = int(self.amount)
        else:self.amount = 1
    def __str__(self):
        if self.amount==1:return self.ele
        else:return self.ele+str(self.amount)
class Substance(Element):
    def __init__(self,string):
        if re.findall("[\(\[]",string):
            string=formatSubstance(string)
        self.amount = 1
        self.eles = list(set(re.findall('[A-Z][a-z]?',string)))#[N,H,O]
        self.elements_r = [Element(i) for i in re.findall("[A-Z][a-z]*[-\d]*",string)]#[N1,H4,N1,O3]
        self.elements = []
        for i in self.eles:
            e = Element(i)
            e.amount = sum([j.amount for j in self.elements_r if j.ele==i])
            self.elements.append(e)
    def __str__(self):
        string1=(self.amount != 1 and str(self.amount) or "")
        string2="".join([str(i) for i in self.elements])
        return string1+string2
    def count(self,ele):
        amountList=[i.amount for i in self.elements if i.ele==ele]
        return amountList and amountList[0] or 0
    def expanse(self):
        for i in self.elements:
            i.amount = i.amount * self.amount
        self.amount = 1
        return self
class Equation():
    def __init__(self,string):
        self.reactantsAmount = re.findall('[+=](?=[\w ])',string).index('=')+1
        #�õ���Ӧ�������
        #ԭ���ǣ�Ѱ�ң����������ĸ�����ֻ�ո�ģ��Ӻź͵Ⱥţ��ų���ɷ��ţ���Ȼ�󿴵Ⱥŵ�������
        self.substancesStringList = [i for i in re.findall('(?:[A-Za-z]\w*)?(?:\([A-Z]\w*\)\d*)?(?:[A-Za-z]\w*)?(?:\[\d*[\+-]?\])?',string) if i!=""]
        #�õ����з�Ӧ����ַ�������ɵ��б�
        #Ѱ�ҵ��ǣ���ĸ���������+��ĸ��������С�������+��ĸ���������+��ĸ�����֡�����������������ϣ�����ÿһ��ǿ�ѡ��
        self.substances = [Substance(i) for i in self.substancesStringList]
        #����Щ��Ӧ����ַ�������һϵ��Substance���ʵ��
        self.eles = []
        for i in self.substances:
            self.eles += i.eles
        self.eles = list(set(self.eles))
        #����ЩSubstance��eles����
        mat = list(set([tuple(self.countAll(ele)) for ele in self.eles]))
        if len(self.eles)>len(self.substances)-1:
            def significant(T):
                for i in range(len(T)):
                    if T[i]!=0:
                        if list(set([I[i]==0 for I in mat[:-1]]))[0]:
                            return True
            while significant(mat[-1]):
                mat = mat[1:]+mat[:1]
            mat = mat[:len(self.substances)-1]
        self.vector = np.array(mat,dtype=np.float32)[:,-1]
        mat2 = np.array(mat)[:,:-1]
        self.matrix = np.array([list(I)[:self.reactantsAmount]+[-i for i in list(I)[self.reactantsAmount:]] for I in list(mat2)],dtype=np.float32)
    def __str__(self):
        string1 = "+".join([str(i) for i in self.substances[:self.reactantsAmount]])
        string2 = "+".join([str(i) for i in self.substances[self.reactantsAmount:]])
        return string1+"=="+string2
    def countAll(self,ele):
        return [i.count(ele) for i in self.substances]

def removeBrackets(string):
    unit = [i for i in re.findall("[A-Za-z\-\d]*",string) if i!=""][0]
    amountList = re.findall("(?<=\))\d*",string)
    if not amountList:
        return Substance(unit)
    else:
        amount = amountList[0]
    radical = Substance(unit)
    radical.amount = int(amount)
    return radical
def solve(a,b):
    def lcm(l):
        return ft.reduce(lambda x,y:x*y/fr.gcd(x,y),l)
    I = np.linalg.inv(a)    #a����
    d = int(np.linalg.det(a))    #a������ʽ
    I2 = [fr.Fraction(int(i),d) for i in list(np.dot(I,b)*d)]+[fr.Fraction(1)]
    sn = [int(i*lcm([i.denominator for i in I2])) for i in I2]
    return sn        
def formatSubstance(string):
    if re.findall("\[\d*[+-]\]",string):
        I = re.findall("\[\d*[+-]\]",string)[0]
        if I[1] == "+":
            c = 1
        elif I[1] == "-":
            c = -1
        else:
            c = int(I[-2]+I[-3:0:-1])
        string = string.replace(I,"E"+str(c))
    if re.findall("\(", string):
        L = re.findall("\(*[A-Za-z\-\d]*\)*[\-\d]*", string)
        L = [removeBrackets(i) for i in L if i!=""]
        for i in L:i.expanse()
        string = "".join([str(i) for i in L])
    return string
def balance(string):
    string = string.replace("��","(")
    string = string.replace("��",")")
    #���û�������ַ����е����������滻ΪӢ������
    try:
        equation = Equation(string)
        #���û�������ַ�������һ��Equation���ʵ��
    except IndexError:
        return "����δ֪����"
        #TODO:�����������󵽵�����ô����
    except ValueError:
        return "�������õȺ����ӷ���ʽ��"
    if len(re.findall("=+",string))>1:
        return "�����벻Ҫ�ڷ���ʽ�г��ֶ���һ���Ⱥš�"
    try:
        coafList = solve(equation.matrix,equation.vector)
        coafList = ["" if i==1 else i for i in coafList]
        if list(set([i==0 for i in coafList[:equation.reactantsAmount]]))[0]:
            return "���󣺸÷���ʽ�޽⡣"
    except np.linalg.linalg.LinAlgError:
        return "���󣺸÷���ʽ�޽�������������ƽ��ʽ��"
    balanced = ""
    for i in range(equation.reactantsAmount):
        balanced = balanced+str(coafList[i])+equation.substancesStringList[i]+(i==equation.reactantsAmount-1 and "=" or "+")
    for i in range(equation.reactantsAmount,len(equation.substances)):
        balanced = balanced+(i==equation.reactantsAmount and "=" or "+")+str(coafList[i])+equation.substancesStringList[i]
    return balanced

EXAMPLES = ("H2+O2==H2O","Fe3O4+Al==Fe+Al2O3","Na+H2O==Na[+]+OH[-]+H2","CO2+Na2O2==Na2CO3+O2","Fe[3+]+Cu==Fe[2+]+Cu[2+]","Al+OH[-]+H2O==AlO2[-]+H2","Cu+HNO3==Cu(NO3)2+NO+H2O","SO2+Br2+H2O==H[+]+SO4[2-]+Br[-]","C6H12O6+O2==CO2+H2O","H[+]+Fe[2+]+MnO4[-]==Fe[3+]+Mn[2+]+H2O","NH4NO3+Ca(OH)2==Ca(NO3)2+NH3+H2O","KSCN+FeCl3==Fe(SCN)3+KCl","NO2+O2+H2O==HNO3","CH3COOH+ZnO==(CH3COO)2Zn+H2O")

if __name__ == "__main__":
    print(balance("CH3COOH + ZnO = (CH3COO)2Zn + H2O"))