import pandas as pd
import numpy as np

salaryData=pd.read_csv("data/salaries-basedata.csv", sep=',',encoding='utf-8')

salaryData['min-experience']=salaryData['experience'].replace(['Menos de 1 año','1+ año','2+ años','3 - 5 años','5 - 10 años','10 - 15 años','Más de 15 años'], [0,1,2,3,5,10,15]).astype(int)
salaryData['max-experience']=salaryData['experience'].replace(['Menos de 1 año','1+ año','2+ años','3 - 5 años','5 - 10 años','10 - 15 años','Más de 15 años'], [0,1,2,4,9,14,15]).astype(int)


salaryData['english-level']=salaryData['english-level'].replace(['Ninguno','Básico (puede leer documentación y código en inglés)','Intermedio (puede pasar una entrevista de programación en ingles cómodamente)','Avanzado (puede liderar una reunion de varias personas en ingles cómodamente)','Nativo'], [0,1,2,3,4]).astype(int)

salaryData['max-title']=salaryData['max-title'].replace(['Ninguno','Bachiller','Técnico','Tecnólogo','Pregrado','Especialista','Maestría','Doctorado'],[0,1,2,3,4,5,6,7]).astype(int)

salaryData['income-in-currency'] = salaryData['income-in-currency'].replace('[\$,]', '', regex=True).astype(float)
salaryData['main-programming-language']=salaryData['main-programming-language'].replace(["ninguno, por que soy manager 😭","no puedo decir, revelaría mi identidad secreta."],["Ninguno","Sin Respuesta"])
salaryData['main-programming-language']=salaryData['main-programming-language'].fillna("Sin Respuesta")
salaryData['workmode']=salaryData['workmode'].replace(['Presencial (ocupa más del 60% de su tiempo en una oficina)',
 'Remoto (ocupa más del 70% de su tiempo trabajando en casa, cowork o un Café)',
 'Teletrabajo (100% trabajo en casa, debido a que así lo indica el contrato)',
 'Flexible (va a la oficina, pero puede trabajar desde casa cuando quiera)'],['Presencial','Remoto','Remoto','Flexible'])
salaryData['workmode']=salaryData['workmode'].fillna("Sin Respuesta")
print(salaryData['main-programming-language'].unique())

salaryData.to_csv("data/salaries-proccesed.csv",index=False)
