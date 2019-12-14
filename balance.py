import functools as ft
import fractions as fr
import numpy as np
import re
import random

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
        self.reactantsAmount = re.findall(r'[+=](?=[(\w ])',string).index('=')+1
        #得到反应物的数量
        #原理是，寻找（后面紧跟字母、数字或空格的）加号和等号（排除电荷符号），然后看等号的索引。
        self.substancesStringList = [i for i in re.findall(r'(?:[A-Za-z]\w*)?(?:\([A-Z]\w*\)\d*)?(?:[A-Za-z]\w*)?(?:\[\d*[\+-]?\])?',string) if i!=""]
        #得到所有反应物的字符串所组成的列表
        #寻找的是，字母与数字组合+字母、数字与小括号组合+字母与数字组合+字母、数字、中括号与正负号组合，其中每一项都是可选的
        self.substances = [Substance(i) for i in self.substancesStringList]
        #用那些反应物的字符串创建一系列Substance类的实例
        self.eles = []
        for i in self.substances:
            self.eles += i.eles
        self.eles = list(set(self.eles))
        #将这些Substance的eles汇总
        mat = list(set([tuple(self.countAll(ele)) for ele in self.eles]))
        if len(self.eles)>len(self.substances)-1:
            def significant(T):
                for i in range(len(T)):
                    if T[i]!=0:
                        if list(set([I[i]==0 for I in mat[:-1]]))[0]:
                            return True
            cnt = 0     # 强行修bug，强行跳出死循环
            while significant(mat[-1]):
                mat = mat[1:] + mat[:1]
                cnt += 1
                if cnt>20:
                    break
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
    unit = [i for i in re.findall(r"[A-Za-z\-\d]*",string) if i!=""][0]
    amountList = re.findall(r"(?<=\))\d*",string)
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
    I = np.linalg.inv(a)    #a的逆
    d = int(np.linalg.det(a))    #a的行列式
    I2 = [fr.Fraction(int(i),d) for i in list(np.dot(I,b)*d)]+[fr.Fraction(1)]
    sn = [int(i*lcm([i.denominator for i in I2])) for i in I2]
    return sn        
def formatSubstance(string):
    if re.findall(r"\[\d*[+-]\]",string):
        I = re.findall(r"\[\d*[+-]\]",string)[0]
        if I[1] == "+":
            c = 1
        elif I[1] == "-":
            c = -1
        else:
            c = int(I[-2]+I[-3:0:-1])
        string = string.replace(I,"E"+str(c))
    if re.findall(r"\(", string):
        L = re.findall(r"\(*[A-Za-z\-\d]*\)*[\-\d]*", string)
        L = [removeBrackets(i) for i in L if i!=""]
        for i in L:i.expanse()
        string = "".join([str(i) for i in L])
    return string
def balance(string):
    string = string.replace("（","(")
    string = string.replace("）",")")
    #将用户输入的字符串中的中文括号替换为英文括号
    try:
        equation = Equation(string)
        #用用户输入的字符串创建一个Equation类的实例
    except IndexError:
        return "错误：未知错误。"
        #TODO:搞清楚这个错误到底是怎么回事
    except ValueError:
        if "=" in string or "->" in string:
            return "错误：请不要输入多余的字符串"
        else:
            return "错误：请用等号或箭头连接方程式。"
    if len(re.findall("=+",string))>1:
        return "错误：请不要在方程式中出现多于一个等号。"
    try:
        coafList = solve(equation.matrix,equation.vector)
        coafList = ["" if i==1 else i for i in coafList]
        if list(set([i==0 for i in coafList[:equation.reactantsAmount]]))[0]:
            return "错误：该方程式无解。"
    except np.linalg.linalg.LinAlgError:
        return "错误：该方程式无解或有无穷多种配平方式。"
    balanced = ""
    for i in range(equation.reactantsAmount):
        balanced = balanced+str(coafList[i])+equation.substancesStringList[i]+(i==equation.reactantsAmount-1 and "=" or "+")
    for i in range(equation.reactantsAmount,len(equation.substances)):
        balanced = balanced+(i==equation.reactantsAmount and "=" or "+")+str(coafList[i])+equation.substancesStringList[i]
    return balanced

def getExample():
    EXAMPLES = ("H2+O2==H2O","Fe3O4+Al==Fe+Al2O3","Na+H2O==Na[+]+OH[-]+H2","CO2+Na2O2==Na2CO3+O2","Fe[3+]+Cu==Fe[2+]+Cu[2+]","Al+OH[-]+H2O==AlO2[-]+H2","Cu+HNO3==Cu(NO3)2+NO+H2O","SO2+Br2+H2O==H[+]+SO4[2-]+Br[-]","C6H12O6+O2==CO2+H2O","H[+]+Fe[2+]+MnO4[-]==Fe[3+]+Mn[2+]+H2O","NH4NO3+Ca(OH)2==Ca(NO3)2+NH3+H2O","KSCN+FeCl3==Fe(SCN)3+KCl","NO2+O2+H2O==HNO3","CH3COOH+ZnO==(CH3COO)2Zn+H2O")
    return random.choice(EXAMPLES)

if __name__ == "__main__":
    print(balance("CH3COOH + ZnO = (CH3COO)2Zn + H2O"))