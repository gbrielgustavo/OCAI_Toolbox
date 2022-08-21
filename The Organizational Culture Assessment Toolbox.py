# #%%
# Processamento de dados do OCAI pelo método de Eijnatten (nome provisório)

# REQUISITOS:
# Os seguintes pacores e complementos precisam estar presentes do seu sistema:
# -Python 3.9
# -numpy - instalação: pip install numpy
# -pandas - instalação: pip install pandas
# -openpyxl - instalação: pip install openpyxl (para ler arquivos excel)
# -scipy - instalação: pip install scipy
# -matplotlib - instalação: pip install matplotlib
# -scikit-bio - instalação: pip install scikit-bio
# -math
# -tkinter

from os import stat
import string
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.reshape.concat import concat

from scipy import stats
from skbio.stats.composition import multiplicative_replacement

import matplotlib.pyplot as plt

import itertools
import operator
import math
import time
import threading
# Apenas para ignorar um aviso de performance que surge
import warnings
warnings.simplefilter("ignore", UserWarning)


import tkinter as tk
import os
from tkinter.filedialog import askopenfile


class guiInterface(tk.Tk):

    def __init__(self):
        super().__init__()
        
        
        self.geometry("640x710")
        self.title('The Organizational Culture Assessment Toolbox')
        self.resizable(0,0)

        self.textoLoad = tk.StringVar()
        self.textoLoad.set("Selecionar Arquivo")
        self.textoLoadOld = tk.StringVar()
        self.textoLoadOld.set("Selec. Arquiv. Passado")


        self.status = tk.StringVar()
        self.status.set("")



        self.calcGeom = tk.IntVar()
        self.calcArit = tk.IntVar()
        self.intervConf = tk.IntVar()
        self.testePermt = tk.IntVar()

        self.graficoAritm = tk.IntVar()
        self.graficoGeom = tk.IntVar()
        self.graficoCompGeomAritm = tk.IntVar()
        self.graficoCompAtualDesejAritm = tk.IntVar()
        self.graficoCompAtualDesejGeom = tk.IntVar()
        self.graficoIntervalos = tk.IntVar()
        self.transparencia = tk.IntVar()
                
        self.alfaBoot = tk.StringVar()
        self.alfaPerm = tk.StringVar()
        self.reamostragens = tk.StringVar()
        self.permutacoes = tk.StringVar()

        self.testeNowNow = tk.IntVar()
        self.testePrefNow = tk.IntVar()



        canvas = tk.Canvas(self,width=640, height=710)
        canvas.place(x=0,y=0)

        tk.Label(self, text="The Organizational Culture Assessment Toolbox", font=('bold', 20)).place(x=320, y=25, anchor="center")

        #tk.Label(self, text="Subtítulo e anotações", font=('bold', 12)).place(x=320, y=55, anchor="center")

        canvas.create_line(15, 80, 625, 80)
        # ###########################################
        tk.Label(self, text="Selecione o tipo de análise", font=('bold', 14)).place(x=7, y=100, anchor="w")

        guiCalcGeom = tk.Checkbutton(self, text='Geométrica', font=('bold', 12),onvalue=1, offvalue=1, variable=self.calcGeom)
        guiCalcGeom.place(x=240, y=135, anchor="w")

        guiCalcArit = tk.Checkbutton(self, text='Aritmética', font=('bold', 12),onvalue=1, offvalue=1, variable=self.calcArit)
        guiCalcArit.place(x=80, y=135, anchor="w")

        guiIntervConf = tk.Checkbutton(self, text='Intervalos de Confiança',onvalue=1, offvalue=1, font=('bold', 12), variable=self.intervConf)
        guiIntervConf.place(x=400, y=135, anchor="w")

        guiTestePermt = tk.Checkbutton(self, text='Teste de Permutação',onvalue=1, offvalue=1, font=('bold', 12), variable=self.testePermt)
        guiTestePermt.place(x=400, y=160, anchor="w")

        canvas.create_line(200, 120, 200, 170)

        canvas.create_line(15, 185, 625, 185)
        # ###########################################
        tk.Label(self, text="Parâmetros dos Testes", font=('bold', 14)).place(x=7, y=210, anchor="w")

        guiAlfaBoot = tk.Spinbox(self, from_=0.05, to=1, increment=0.05, width=7, textvariable=self.alfaBoot)
        guiAlfaBoot.place(x=270, y=245, anchor="w") 
        tk.Label(self, text="Alfa Intervalos de Confiança:", font=('bold', 12)).place(x=60, y=245, anchor="w")

        guiReamostragens = tk.Spinbox(self, from_=5000, to=100000, increment=250, width=7, textvariable=self.reamostragens)
        guiReamostragens.place(x=270, y=275, anchor="w") 
        tk.Label(self, text="Reamostragens:", font=('bold', 12)).place(x=60, y=275, anchor="w")

        canvas.create_line(350, 235, 350, 290)


        guiAlfaPerm = tk.Spinbox(self, from_=0.05, to=1, increment=0.01, width=7, textvariable=self.alfaPerm)
        guiAlfaPerm.place(x= 520, y=245, anchor="w") 
        tk.Label(self, text="Alfa Permutação:", font=('bold', 12)).place(x=380, y=245, anchor="w")

        guiPermutacoes = tk.Spinbox(self, from_=5000, to=100000, increment=250, width=7, textvariable=self.permutacoes)
        guiPermutacoes.place(x=520, y=275, anchor="w") 
        tk.Label(self, text="Permutações", font=('bold', 12)).place(x=380, y=275, anchor="w")

        canvas.create_line(15, 310, 625, 310)


        # ###########################################
        tk.Label(self, text="Gráficos para gerar", font=('bold', 14)).place(x=7, y=335, anchor="w")

        tk.Label(self, text="Apenas OCAI", font=('bold', 12)).place(x=40, y=365, anchor="w")
        tk.Label(self, text="Comparar Atual e Desej.", font=('bold', 12)).place(x=210, y=365, anchor="w")
        tk.Label(self, text="Intervalos de Confiança", font=('bold', 12)).place(x=430, y=365, anchor="w")


        

        guiGraficoAritm = tk.Checkbutton(self, text='Aritmético', font=('bold', 12), variable=self.graficoAritm)
        guiGraficoAritm.place(x=18, y=395, anchor="w")

        guiGraficoGeom = tk.Checkbutton(self, text='Geométrico', font=('bold', 12), variable=self.graficoGeom)
        guiGraficoGeom.place(x=18, y=425, anchor="w")

        guiGraficoCompGeomAritm = tk.Checkbutton(self, text='Comparar Geom. e Arit.', font=('bold', 12), variable=self.graficoCompGeomAritm)
        guiGraficoCompGeomAritm.place(x=18, y=455, anchor="w")


        guiGraficoCompAtualDesejAritm =  tk.Checkbutton(self, text='Aritmético', font=('bold', 12), variable=self.graficoCompAtualDesejAritm)
        guiGraficoCompAtualDesejAritm.place(x=188, y=395, anchor="w")

        guiGraficoCompAtualDesejGeom =  tk.Checkbutton(self, text='Geométrico', font=('bold', 12), variable=self.graficoCompAtualDesejGeom)
        guiGraficoCompAtualDesejGeom.place(x=188, y=425, anchor="w")



        guiGraficoIntervalos =  tk.Checkbutton(self, text='Geom. e Interv. de Conf.', font=('bold', 12), variable=self.graficoIntervalos)
        guiGraficoIntervalos.place(x=406, y=395, anchor="w")

        guiTransparencia =  tk.Checkbutton(self, text='Transparencia', font=('bold', 12), variable=self.transparencia)
        guiTransparencia.place(x=406, y=455, anchor="w")


        canvas.create_line(15, 485, 625, 485)

        canvas.create_line(170, 355, 170, 430)
        canvas.create_line(395, 355, 395, 450)

        canvas.create_line(430, 430, 550, 430)


        ###########################################
        tk.Label(self, text="Permutação para testar a Evolução Cultural", font=('bold', 14)).place(x=7, y=510, anchor="w")

        guitesteNowNow =  tk.Checkbutton(self, text='Cultura passada vs cultura atual', font=('bold', 12), variable=self.testeNowNow)
        guitesteNowNow.place(x=40, y=540, anchor="w")

        guitestePrefNow =  tk.Checkbutton(self, text='Cultura antes desejada vs cultura atual', font=('bold', 12), variable=self.testePrefNow)
        guitestePrefNow.place(x=40, y=565, anchor="w")

        abrirArquivoOld = tk.Button(self, textvariable=self.textoLoadOld, width=25, font=('bold', 11),command=lambda:self.openFileOld())
        abrirArquivoOld.place(x=390, y=552, anchor="w")


        canvas.create_line(15, 590, 625, 590)

        ###########################################
        abrirArquivo = tk.Button(self, textvariable=self.textoLoad, width=40, font=('bold', 12),command=lambda:self.openFile())
        abrirArquivo.place(x=40, y=620, anchor="w")

  

        start = tk.Button(self, text="Iniciar", width=10,font=('bold', 12),command=lambda:calculo.calc(self))
        start.place(x=460, y=620, anchor="w")


        self.guistatus = tk.Label(self, textvariable=self.status, font=('bold', 12))
        self.guistatus.place(x=20, y=670, anchor="w")

        tk.Label(self, text="Criado por Gabriel Gustavo Soares Santos", font=('bold', 8)).place(x=620, y=655, anchor="e")
        tk.Label(self, text="santos.gabrielg@usp.br", font=('bold', 8)).place(x=620, y=695, anchor="e")
        tk.Label(self, text="Sob a licença GPLv3", font=('bold', 8)).place(x=620, y=675, anchor="e")
   


    def openFile(self):
        self.textoLoad.set("Carregando...")
        self.file = askopenfile(mode='rb')
        if self.file:
            fileName = os.path.basename(self.file.name)
            self.textoLoad.set("%s foi carregado!" %(fileName))
            return(self.file)
            
    def openFileOld(self):
        self.textoLoadOld.set("Carregando...")
        self.fileOld = askopenfile(mode='rb')
        if self.fileOld:
            fileName = os.path.basename(self.fileOld.name)
            self.textoLoadOld.set("%s ok!" %(fileName))
            return(self.fileOld)
            


class calculo():
    def __init__(self):
        pass
    #guiInterface
        
    def calc(self):
            textostatus = "Preparado requisitos..."
            print(textostatus)
            self.status.set(textostatus)

            time0 = time.time() #para marcar o tempo de execução

            # Lendo informações da interface gráfica
            arquivo = self.file
            

            calcGeom = self.calcGeom.get()
            calcArit = self.calcArit.get()
            intervConf = self.intervConf.get()
            testePermt =self.testePermt.get()

            graficoAritm = self.graficoAritm.get()
            graficoGeom = self.graficoGeom.get()
            graficoCompGeomAritm = self.graficoCompGeomAritm.get()
            graficoCompAtualDesejAritm = self.graficoCompAtualDesejAritm.get()
            graficoCompAtualDesejGeom = self.graficoCompAtualDesejGeom.get()
            graficoIntervalos = self.graficoIntervalos.get()
                    
            self.alpha = float(self.alfaBoot.get())
            self.alphaPermutac = float(self.alfaPerm.get())
            self.numeroReam = int(self.reamostragens.get())
            self.numPemut = int(self.permutacoes.get())
            transparencia = self.transparencia.get()
            offset = 3
            testeNowNow = self.testeNowNow.get()
            testePrefNow = self.testePrefNow.get()


        # Preparação inicial

            # DEFINIMOS algumas tuplas e dicionários para facilitar o uso do multiindex
            # Para DataFrame "dados", usar na seguinte ordem: [estado[], dimensao[], cultura[]]
            # Para DataFrame "dados"usar na  ordem: [estado[], cultura[], dimensao[]] - Isso facilita certos procedimentos de seleção de dados.
            ##############################################################################################################################################################
            self.estado = ("Now", "Preferred")
            self.dimensao = (1, 2, 3, 4, 5, 6)
            self.cultura = ("A", "B", "C", "D")
            self.dicioCulturas = {"A":"Clã", "B":"Adhocracia", "C": "Mercado","D":"Hierarquia"}
            self.indexDistancias = ("distNow", "distPref")
            self.indexNowFref = (("A", "B", "C", "D", "distNow") , ("A", "B", "C", "D", "distPref"))
            self.namesIntv = ['Inf.','CFP','Sup.']
            self.est =(self.estado[1],self.estado[0]) # como em elimMaiorDist desejamos fazer a eliminação das maiores distancias primeiro Now e depois Pref, temos que eliminar primeiro Pref e depois Now do nosso DataFrame. Esta tupla ajuda nisso
            ##############################################################################################################################################################



            # Esses arrays são usados para a criação do índice multinível
            # Como eles devem geram uma estrutura fixa, os deixamos de fora da função calculoPerfil para evitar recalculo
            ##############################################################################################################################################################
            arraySuporte1 = []
            arraySuporte2 = []
            for i in range(len(self.estado)):
                for j in range(len(self.cultura)):
                    arraySuporte1.append(self.estado[i])
                    arraySuporte2.append(self.cultura[j])

            self.index = pd.MultiIndex.from_arrays([arraySuporte1, arraySuporte2]) # os arrays de suporte aqui são usados na construção de um índice multinível


            # Para a estrutura do bootstratp temos que usar uma outra estrutura de index multinível
            arraySuporte1 = []
            arraySuporte2 = []
            arraySuporte3 = []
            for i in range(len(self.estado)):
                for j in range(len(self.cultura)):
                    for k in range(len(self.dimensao)):
                        arraySuporte1.append(self.estado[i])
                        arraySuporte2.append(self.cultura[j])
                        arraySuporte3.append(self.dimensao[k])

            self.indexBootstap = pd.MultiIndex.from_arrays([arraySuporte1, arraySuporte2, arraySuporte3])

            del arraySuporte1
            del arraySuporte2
            del arraySuporte3

            #Gera um multiindex que usa o noma das culturas ao invés de A, B, C e D
            self.indexNomeCult = self.index
            self.indexNomeCult = self.indexNomeCult.to_frame()
            self.indexNomeCult = self.indexNomeCult.replace(self.dicioCulturas)
            self.indexNomeCult = pd.MultiIndex.from_frame(self.indexNomeCult)




            #Estruturas parecidas. Talvez criar uma função.
            #Gera um multiindex que Inverte o Now e o Preferred. Isso é usado durante a distantia de Aitchison dos dados permutados
            self.indexReverso = self.index
            self.indexReverso = self.indexReverso.to_frame()
            self.indexReverso = self.indexReverso.replace({"Now":"Preferred", "Preferred":"Now"})
            self.indexReverso = pd.MultiIndex.from_frame(self.indexReverso, names=['um','dois'])



            #Gera um multiindex que Inverte o Now e o Preferred, mas para uma a Isso é usado para na permutação dos dados
            self.indexRevBoot = self.indexBootstap
            self.indexRevBoot = self.indexRevBoot.to_frame()
            self.indexRevBoot = self.indexRevBoot.replace({"Now":"Preferred", "Preferred":"Now"})
            self.indexRevBoot = pd.MultiIndex.from_frame(self.indexRevBoot, names=['um','dois','três'])
            ##############################################################################################################################################################




            # IMPORTAÇÃO e pré-processamos os dados
            ##############################################################################################################################################################
            # faz a leitura dos dados de uma planilha excel e salva em um DataFrame um cabeçalho multidimensional (multiindex)
            
            textostatus = "Pré-processando planilha..."
            print(textostatus)
            self.status.set(textostatus)

            self.dados = pd.read_excel(arquivo, header=[0, 1, 2], dtype='int16')
            

            # Este trecho do código inverte os eixos do dataframe original
            # Isso é bastante útíl para a seleção de dados
            self.dados = self.dados.swaplevel(axis=1)
            self.dados.sort_index(axis=1, level=0, inplace=True)
            self.dadosCopia = self.dados
            self.dados.to_excel("Resultados/Intertido.xlsx")
            


            # Se algum elemento for Zero, a média geométrica também será zero.
            # Assim temos que fazer uma substituição para evitar que isso rebaixe muito a nota da pessoa N na cultura X
            # O Pacote scikit-bio apresenta algumas ferramentas para trabalharmos com dados composicionais, e dentre ela uma que trabalha com a substituição dos zeros pelo método multiplicativo
            self.dados = multiplicative_replacement(self.dados)
            self.dados = pd.DataFrame(self.dados, columns=self.indexBootstap)*1000
            self.dados = self.dados.astype(np.float32)

            self.dados.to_excel("Resultados/NoZeroes.xlsx")
      

            if testePrefNow == 1 or testeNowNow == 1: #para testar dois anos diferentes
                arquivoOld = self.fileOld
                self.dadosOld = pd.read_excel(arquivoOld, header=[0, 1, 2])
                self.dadosOld = self.dadosOld.swaplevel(axis=1)
                self.dadosOld.sort_index(axis=1, level=0, inplace=True)

                self.dadosOld = multiplicative_replacement(self.dadosOld)
                self.dadosOld = pd.DataFrame(self.dadosOld, columns=self.indexBootstap)*1000
                self.dadosOld = self.dadosOld.astype(np.uint8)                



            escMax = 0 # suporte para a plotagem dos gráficos

        # Calculos
            if calcArit==1:

                textostatus = "Calculando CFP Aritmético..."
                print(textostatus)
                self.status.set(textostatus)

                cfpAritm = calculo.calculoPerfil(self,1,1, self.dadosCopia, False) #aritmético
                cfpAritm.to_excel("Resultados/CFP Aritmético.xlsx")


                escMaxTeste = cfpAritm.max()
                escMaxTeste = escMaxTeste.max()        
                escMaxTeste = escMaxTeste+offset                 
                if escMaxTeste > escMax: escMax = escMaxTeste

                #print(cfpAritm)
            
            if calcGeom ==1:
                textostatus = "Calculando CFP Geométrico..."
                print(textostatus)
                self.status.set(textostatus)

                cfp = calculo.calculoPerfil(self, 1,1, self.dados, True)
                cfp.to_excel("Resultados/CFP Geométrico.xlsx")

                escMaxTeste = cfp.max()
                escMaxTeste = escMaxTeste.max()        
                escMaxTeste = escMaxTeste+offset                 
                if escMaxTeste > escMax: escMax = escMaxTeste

                #print(cfp)
            
            if intervConf == 1  and calcGeom == 0:
                print("Não é possível calcular os intervalos de confiança sem a média geométrica!")
            
            elif intervConf == 1  and calcGeom == 1:
                textostatus = "Calculando Intervalos de confiança..."
                print(textostatus)
                self.status.set(textostatus)
                # Chama a função que faz a reamostragem - Gera 'numeroReam' ocais de N elementos
                # Cada amostra (DataFrame do pandas) gerada é armazenada em um lista(dadosReamostragem)
                # Logo, dadosReamostragem[n] retorna o DataFrame que contém os dados do OCAI n, gerados a partir do bootstrap do OCAI original
                dadosReamostragem = calculo.reamostragem(self, self.numeroReam)
                
                # Aqui geramos calculamos o cfp dos dados reamostrados e geramos um Dataframe com eles
                cfpReamIndiv = calculo.cfpRPCalc(self,dadosReamostragem, self.numeroReam)

                del dadosReamostragem

                #Calcula as distâncias de Aitchison usando o cfp
                # O primeiro argumento é um dataframe contendo um único perfil OCAI (Ex. cfp da amostra original),
                # enquanto o segundo argumento pode possuir um ou mais perfis dentro do dataframe
                # O último argumento escolhe se calculamos a distância entre o "Now da amostra 1" e o "Now da amostra 2" (bastando deixar em zero)
                # ou se calculamos a distância entre o "Now e o Pref" de cada amostra. Para o teste de permutação as amostras 1 e 2 devem ser a mesma.
                aitchDist = calculo.Aitchison(self, cfp, cfpReamIndiv, 0)

                del cfpReamIndiv
                
                #Elimina as alpha% maiores distâncias
                ############################################
                aitchDistLimp = calculo.elimMaiorDist(self, aitchDist, self.alpha)

                del aitchDist


                #Calcula os intervalos de confiança
                ##########################################
                intv = calculo.intvConf(self,aitchDistLimp)

                del aitchDistLimp

                # Condensa os intervalos de confiança e o cfp em um único dataframe
                self.ocai = pd.concat([intv[1],cfp.transpose(),intv[0]], axis=1)
                self.ocai = self.ocai.set_axis(self.namesIntv, axis=1)
                self.ocai = self.ocai.set_axis(self.indexNomeCult, axis=0)
                self.ocai = self.ocai.round(decimals=2)

                del intv

                self.ocai.to_excel("Resultados/CFP Geom e Inter de Conf.xlsx")

                
                escMaxTeste = self.ocai.max()
                escMaxTeste = escMaxTeste.max() + offset

                if escMaxTeste > escMax: escMax = escMaxTeste



                #print(self.ocai)

            if testePermt == 1  and calcGeom == 0:
                print("Não é possível fazer o teste de permutação sem a média geométrica!")
            
            elif testePermt == 1  and calcGeom == 1:
                textostatus = "Realizando o Teste de permutação..."
                print(textostatus)
                self.status.set(textostatus)

                # TESTE DE PERMUTAÇÃO - Verifica se Now e Preferred são estatisticamente iguais
                # H0: São iguais H1: Não são iguais
                ################################################
                # Faz a permutação dos dados reamostrados
                #print("\npermutação")
                self.dados.to_excel("Resultados/DadosAntesPerm.xlsx")

                permutados = calculo.permutac(self, self.dados, self.numPemut)
                



                cfpPermt = calculo.calcMedPermt(self, permutados)

                del permutados
                # Calcula a distancia Aitchison dos dados permutados
                aitchDistPermt = calculo.AitchisonPermt(self, cfpPermt)

                # Distancia dos dados originais de Now e Pref
                aitchDistNowPrefOrig = calculo.Aitchison(self, cfp, cfp, 1)

                del cfpPermt

                # Calcula o p-valor e verifica se as sitiuações presente e desejada são iguais
                nowAndPrefDif = calculo.verifPerm(self, aitchDistPermt, aitchDistNowPrefOrig)

                del aitchDistNowPrefOrig
                del aitchDistPermt

                if nowAndPrefDif == "=":
                    nowAndPrefDif = "\nComparação entre estado atual e desejado:\np-valor = %.4f\nalfa = %.2f\np-valor > alfa\nAceitamos h0: Now e Preferred são estatisticamente iguais" %(self.pValue, self.alphaPermutac)
                elif nowAndPrefDif == "!=":
                    nowAndPrefDif = "\nComparação entre estado atual e desejado:\np-valor = %.4f\nalfa = %.2f\np-valor < alfa\nRejeitamos h0:  Now e Preferred são estatisticamente diferentes" %(self.pValue, self.alphaPermutac) 

                    

                text_file = open("Resultados/Resultado permutação.txt", "w")
                text_file.write(nowAndPrefDif)
                text_file.close()










            if testeNowNow == 1 or testePrefNow == 1:
                cfpAntigo = calculo.calculoPerfil(self, 1,1, self.dadosOld, True)
                cfpAntigo.to_excel("Resultados/CFP Old.xlsx")


            if testeNowNow == 1: #para testar dois anos diferentes
                
                textostatus = "Teste de Permutação: Cultura passada vs Cultura atual..."
                print(textostatus)
                self.status.set(textostatus)
                
                
                nowNowDf = pd.concat([self.dados['Now'],self.dadosOld['Now']], axis=1, ignore_index=True).to_numpy()
                
                nowNowDf = nowNowDf.transpose()
                nowNowDf = pd.DataFrame(nowNowDf, index=self.indexBootstap).transpose()

                cfptesteNowNow = calculo.calculoPerfil(self, 1,1, nowNowDf, True)

                nowAndPrefDif = calculo.permtPassadoPresente(self, nowNowDf, cfptesteNowNow)
                

                if nowAndPrefDif == "=":
                    nowAndPrefDif = "\nComparação entre cultura passada e cultura atual:\np-valor = %.4f\nalfa = %.2f\np-valor > alfa\nAceitamos h0: As culturas atual e passada são estatisticamente iguais" %(self.pValue, self.alphaPermutac)
                elif nowAndPrefDif == "!=":
                    nowAndPrefDif = "\nComparação entre cultura passada e cultura atual:\np-valor = %.4f\nalfa = %.2f\np-valor < alfa\nRejeitamos h0:  As culturas atual e passada são estatisticamente diferentes" %(self.pValue, self.alphaPermutac) 

                
                text_file = open("Resultados/Permutação passada&atual.txt", "w")
                text_file.write(nowAndPrefDif)
                text_file.close()




            if testePrefNow == 1: #para testar dois anos diferentes

                textostatus = "Teste de Permutação: Cultura anteriormente desejada vs Cultura atual..."
                print(textostatus)
                self.status.set(textostatus)                
                
                prefNowDf = pd.concat([self.dados['Now'],self.dadosOld['Preferred']], axis=1, ignore_index=True).to_numpy()
                prefNowDf = prefNowDf.transpose()
                prefNowDf = pd.DataFrame(prefNowDf, index=self.indexBootstap).transpose()
                

                cfptestePrefNow = calculo.calculoPerfil(self, 1,1, prefNowDf, True)

                nowAndPrefDif = calculo.permtPassadoPresente(self, prefNowDf, cfptestePrefNow)

                if nowAndPrefDif == "=":
                    nowAndPrefDif = "\nComparação entre cultura desejada no passado e cultura atual:\np-valor = %.4f\nalfa = %.2f\np-valor > alfa\nAceitamos h0: As culturas atual e a desejada no passado são estatisticamente iguais" %(self.pValue, self.alphaPermutac)
                elif nowAndPrefDif == "!=":
                    nowAndPrefDif = "\nComparação entre cultura desejada no passado e cultura atual:\np-valor = %.4f\nalfa = %.2f\np-valor < alfa\nRejeitamos h0:  As culturas atual e a desejada no passado são estatisticamente diferentes" %(self.pValue, self.alphaPermutac) 

                
                text_file = open("Resultados/Permutação passadaPref&atual.txt", "w")
                text_file.write(nowAndPrefDif)
                text_file.close()

           
        # Plotagem dos gráficos
            textostatus = "Plotando gráficos..."
            print(textostatus)
            self.status.set(textostatus)
            if transparencia == 1: transp = True
            elif transparencia == 0: transp = False

            # if testePrefNow == 1:
            #     legenda = False
                
            #     temp = cfptesteNowNow.to_numpy()
            #     print(temp)
            #     xx = input()
            #     temp = pd.DataFrame(temp, columns=["Now", "Preferred"], index=["Clã", "Adhocracia", "Mercado","Hierarquia"])
            #     xx = input()
            #     plot = calculo.plotagem(self,temp, transp, escMax, "Comparação Cultura Desejada no Passado e Atual", legenda)


            # if testeNowNow == 1:
            #     legenda = False
                
            #     temp = cfptestePrefNow.to_numpy()
            #     temp = pd.DataFrame(temp, columns=["Now", "Preferred"], index=["Clã", "Adhocracia", "Mercado","Hierarquia"])

            #     plot = calculo.plotagem(self,temp, transp, escMax, "Comparação Cultura Passada e Atual", legenda)

            if graficoAritm == 1:
                legenda = False
                for i in range(len(self.estado)):
                    nome = self.estado[i]
                    
                    ocaiPlot = cfpAritm[nome].transpose()
                    nome = "OCAI Aritm - " + nome
                    plot = calculo.plotagem(self,ocaiPlot, transp, escMax, nome, legenda)

            if graficoGeom == 1:
                legenda = False
                for i in range(len(self.estado)):
                    nome = self.estado[i]
                    
                    ocaiPlot = cfp[nome].transpose()
                    nome = "OCAI Geom - " + nome
                    plot = calculo.plotagem(self,ocaiPlot, transp, escMax, nome, legenda)

            if graficoCompAtualDesejAritm == 1:

                legenda = True
                temp = concat([cfpAritm["Now"],cfpAritm["Preferred"]], ignore_index=True).to_numpy()
                temp = temp.transpose()

                temp = pd.DataFrame(temp, columns=["Now.Aritm", "Preferred.Aritm"], index=["Clã", "Adhocracia", "Mercado","Hierarquia"])


                plot = calculo.plotagem(self,temp, transp, escMax, "Comparação Atual e Desejado - Aritm.", legenda)
   
            if graficoCompAtualDesejGeom == 1:
                legenda = True
                temp = concat([self.ocai['CFP']['Now'],self.ocai['CFP']['Preferred']], axis=1, ignore_index=True).to_numpy()

                temp = pd.DataFrame(temp, columns=["Now", "Preferred"], index=["Clã", "Adhocracia", "Mercado","Hierarquia"])

                plot = calculo.plotagem(self,temp, transp, escMax, "Comparação Atual e Desejado - Geom.", legenda)

            
            if graficoCompGeomAritm ==1:
                legenda = True
                aritGeom = pd.concat([cfp,cfpAritm], ignore_index=True).to_numpy() 
                aritGeom = pd.DataFrame(aritGeom, columns=self.index, index=["Geom.", "Aritm."]).transpose()

                for i in range(len(self.estado)):
                    nome = self.estado[i]
                    
                    ocaiPlot = aritGeom.loc[nome]
                    nome = "Comparação Geom e Aritm - " + nome
                    plot = calculo.plotagem(self, ocaiPlot, transp, escMax, nome, legenda)

            #ok
            if graficoIntervalos == 1:
                legenda = True
                if intervConf == 0 or calcGeom == 0:
                    print("Impossível plotar sem antes calcular o OCAI com a média geométrica e/ou sem calcular os Intervalos de confiança!!!")
                elif intervConf == 1 and calcGeom == 1:


                    for i in range(len(self.estado)):
        
                        nome = self.estado[i]
                        
                        ocaiPlot = self.ocai.loc[nome]
                        nome = "Intervalos - " + nome
                        plot = calculo.plotagem(self, ocaiPlot, transp, escMax, nome, legenda)
        

            
            tempoExec = ("%.2fs" %(time.time()-time0))
            textostatus = "Pronto!!! - Tempo de execução: "+tempoExec

            text_file = open("Tempo de execução.txt", "w")
            text_file.write(textostatus)
            text_file.close()

            print(textostatus)
            self.status.set(textostatus)

            

            ##############################################################################################################################################################
# Começam as funções
    ##############################################################################################################################################################
    #compara a cultura passada com a atual
    def permtPassadoPresente(self, df, cfpOld):
        
      

        #cfpOld.to_excel("Resultados/CFP Geométrico Old.xlsx")

        permutados = calculo.permutac(self, df, self.numPemut)
        

        cfpPermt = calculo.calcMedPermt(self, permutados)

        del permutados
        # Calcula a distancia Aitchison dos dados permutados
        aitchDistPermt = calculo.AitchisonPermt(self, cfpPermt)

        # Distancia dos dados originais de Now e Pref
        aitchDistNowPrefOrig = calculo.Aitchison(self, cfpOld, cfpOld, 1)

        del cfpPermt

        # Calcula o p-valor e verifica se as sitiuações presente e desejada são iguais
        nowAndPrefDif = calculo.verifPerm(self, aitchDistPermt, aitchDistNowPrefOrig)

        del aitchDistNowPrefOrig
        del aitchDistPermt
        
        return(nowAndPrefDif)

    # OBJETIVO 1: Calcular o IFP - Individual full profile
    # OBJETIVO 2: Calcular o CDP - Collective Dimensional Profile
    # OBJETIVO 3: Calcular o cfp - Collective Full Profile
    # Como o código é extremamente similar tanto para calcular o IFP quanto o CDF (só o valor de uma variável muda) optamos por criar uma função
    # A variável eixo em qual eixo calcularemos a média geométrica. Com um eixo=1 calculamos o IFP e com eixo=0 calculamos o CDP
    # O cógido para calcular o cfp também não é tão diferente assim dos outros, então implementamostambém nesta função. A variável "sel" controla esta escolha.
    # quando sel = 1 e eixo = 1 o CDP é calculado; Com sel = 0 e eixo = 1 o IFP é calculado, com sel = 0 e eixo = 0, o CDP é calculado
    ##############################################################################################################################################################
    def calculoPerfil(self, eixo, sel, dadosFunc, geom): #ok
        # quando sel = 1 e eixo = 1 o CDP é calculado; Com sel = 0 e eixo = 1 o IFP é calculado, com sel = 0 e eixo = 0, o CDP é calculado

        Profile = []
        tempSuporte =[]
        
        # Este laço de repetição é responsável por calcular a média geométrica da cultura X da Pessoa N
        # A média geométrica calculada é salva em Profile

        for i in range(len(self.estado)):
            for j in range(len(self.cultura)):
                
                dataTemp = dadosFunc[self.estado[i],self.cultura[j]] #Seleciona a cultura j dentro do Estado i

                dataTemp = dataTemp.dropna()

                if int(sel) == 0:

                    # este trecho é usado no calculo do cfp e IDP.
                    # Ele á calcula a média geométria das diferentes dimensões culturais (para o caso do IDP) ou a média geométrica das respostas de cada cultura isolada
                    # A variável eixo altera o eixo em que a média geométrica é calculada, e portanto faz esta alteração entre o IDP e o cfp
                    if geom == True: #para alterar entre a média geométria e a aritmética
                        Profile.append(stats.gmean(dataTemp, axis=eixo))
                    else:
                        Profile.append(dataTemp.mean(axis=eixo))
                    
                elif int(sel) == 1:
                    # Para o cálculo do cfp precisamos agregar as respostas das diferentes dimensões de cada cultura, e este é o trecho de código responsável por isso.
                    Profile.append(dataTemp) #Profile é uma lista contendo o dataframe das 6 dimensões de cada cultura em cada estado

        
        
        # este trecho só é executado no calculo do IFP e CDP
        if int(sel) == 0:

            # Como os dados de perfil são armazenados em uma lista, precisamos converte-los de volta para um dataframe para facilitar a manipulação posterior
            # Mas antes fazemos transpomos a lista para um array do numpy, isto é feito para o array ficar no formato adequado para aplicarmos o multiindex ao dataframe
            
            Profile = np.transpose(Profile) #Transpomos a o array no numpy
    
            Profile = pd.DataFrame(Profile,columns=self.index)  # E então convertemos para um DataFrame


                
        # este trecho só é executado no calculo do cfp
        elif int(sel) == 1 and int(eixo) == 1:
    
            for i in range(len(Profile)):
                
                dataTemp = Profile[i] #extrai dados referentes a cultura i armazenados na lista Profile

                dataTemp = dataTemp.to_numpy() #converte para um array do numpy
                
                dataTemp = dataTemp.flatten() #Elimina as dimensões

                if geom == True:          
                    tempSuporte.append(stats.gmean(dataTemp)) #Calcula e adiciona a média geométrica daquela cultura e salva na lista tempSuporte
                else:
                    tempSuporte.append(np.mean(dataTemp)) #Calcula e adiciona a média aritmética daquela cultura e salva na lista tempSuporte

            Profile = pd.Series(tempSuporte, index=self.index) #Como a lista tempSuporte possui apenas uma dimensão não é possível criarmos diretamente um Dataframe, assim criamos primeiro uma série do pandas
            Profile = Profile.to_frame() # depois a convertemos para um DataFrame
            Profile = Profile.transpose() # E fazemos a transposição



        #Este trecho torna escala a média geométrica calculada para a base 100
        #Ele é necessário pois a soma das médias geométricas pode gerar valores diferentes da base 100, e estamos trabalhado com a média geométrica fechada
        if geom == True:
            for i in range(len(self.estado)):
                
                soma = pd.DataFrame(Profile[self.estado[i]]) #Encontramos a soma total do OCAI no Estado i
                mult = pd.DataFrame(100/(soma.sum(axis=1))) #Calculamos o fator multiplicativo
                
                for j in  range(len(self.cultura)): # E multiplicamos todas as cultura do estado i por esse fator
                    soma[self.cultura[j]] = soma[self.cultura[j]]*mult[0]
                
                Profile[self.estado[i]] = soma #Por fim substituimos os valores do dataframe original pelos convertidos para a base 100
            
        # Por fim a função retorna um DataFrame contendo o perfil calculado
        return(Profile)    
    ##############################################################################################################################################################

#apenas para facilitar a edição
    # OBJETIVO DA FUNÇÃO: fazer a reamostragem bootstrap com base nos dados originais
    # Gera K amostras de N elementos - N elementos é igual a quantidade de respondentes do ocai original
    # o argumento repetições indica quantas amostras (k) serão geradas
    # performance ainda pode melhorar. Não foi otimizado por termos que dar prioridade para outros aspectos
    ##############################################################################################################################################################
    def reamostragem(self, repeticoes): #ok

        #aqui lemos o numero de itens (pessoas) no questionário. Isso é importante para definir o tamanho das amostras que serão geradas
        tamanho = np.array(self.dados[self.estado[0]][self.cultura[0]][self.dimensao[0]]).size

        tamanho = tamanho * repeticoes

        resample = [] # criamos a lista resample para ser usada para guardar temporiariamente a amostra gerada da dimensão k, na cultura j e estado x
        bootstrap = [] # a lista bootstrap guarda todas as amostras geradas


        #Estamos usando um laço de repetição para gerar as novas amostras      
        # A dimensão j da cultura j no estado i será armazenada em uma coluna
        # implementação de multithreading pode melhorar performance
        for i in range(len(self.estado)): 
            for j in range(len(self.cultura)):
                for k in range(len(self.dimensao)):

                    # A cada novo ciclo redefinimos a nossa amostra base como a dimensão k da cultura j no estado i                    
                    sample = np.array(self.dados[self.estado[i]][self.cultura[j]][self.dimensao[k]]) 


                    resample.append(np.random.choice(sample, size=tamanho)) #aqui fazemos a reamostragem, gerando uma coluna com dados da dimensão k da cultura j no estado i, e com tamanho igual ao tamanho da amotra original x o numero de reamostragens desejado
                    
                            
        resample = np.array(resample).transpose() # Como seria difícil aplicar gerar um dataframe com multiindex a a partir de uma lista de listas (resample), primeiro convertemos para um array do numpy e fazemos a transposição
            
        resample = pd.DataFrame(resample, columns=self.indexBootstap) # Então basta criarmos o Dataframe desta reamostragem


        # Precisamos agora dividir o dataframe gerado de acordo com o numero de amostras desejado
        tamanho = int(tamanho/repeticoes) # redefinimos a variavel tamanho
        inicio = 0 #para ajudar no passo d split

        for i in range(repeticoes):
        
            corte = resample.iloc[inicio:(inicio+tamanho)] #faz o corte do dataframe indo de início até (início + tamanho)
            
            bootstrap.append(corte) #Salvamos o corte dentro de uma lista

            inicio = inicio + tamanho # e incluímos o passo do próximo corte

        del resample
        del sample
        del corte

        return bootstrap # no final a função retorna uma lista com todas as funções geradas
    ##############################################################################################################################################################


    # OBJETIVO DA FUNÇÃO: calcular as distâncias de Aitchison
    # Para o cálculo preferimos usar a equação descrita no trabalho de Fossaluza (2012, p.20) e no de Aitchison e Egozcue (2005, p.832)
    # Raiz do Somatório do quadrado das diferenças entre o logaritimo natural da razão entre a cultura Xj e a média geométrica das culturas de X e o logaritimo natural da razão entre a cultura Yj e a média geométrica das culturas de Y
    # δ(q_1,q_2 )=√(∑_(j=1)^R▒(ln⁡〖q_1j/(g(q_1))〗-ln⁡〖q_2j/(g(q_2))〗 )^2 )

    # O primeiro argumento é um dataframe contendo um único perfil OCAI (Ex. cfp da amostra original),
    # enquanto o segundo argumento pode possuir um ou mais perfis dentro do dataframe
    # O último argumento escolhe se calculamos a distância entre o "Now da amostra 1" e o "Now da amostra 2" (bastando deixar em zero)
    # ou se calculamos a distância entre o "Now e o Pref" de cada amostra (com switch = 1). Para o teste de permutação as amostras 1 e 2 devem ser a mesma.
    ##############################################################################################################################################################
    def Aitchison(self, am1, am2, switch):
                
        distancias = [] # Armazenaremos as distâncias nesta lista

        # Quando switch igual a 1 invertemos o index para calcular a distancia entre o Now e o Preferred
        if switch == 1:   
            am2 = am2.set_axis(self.indexReverso, axis=1)

        # Temos que calcular a distancia para ambos os estados: Atual e desejado
        for h in range(len(self.estado)):

            # Calcula a Média Geométrica da amostra 1. gMean 1 é constante durante o Estado 1
            gMean1 = stats.gmean(am1[self.estado[h]], axis=1)

            arr = [] #lista para armazenar as distâncias calculadas

            # am2 possui o perfis dos dados reamostrados, sendo assim temos que calcular a distancia para cada uma destes perfis 
            for i in range(len(am2)):
                
                # Calcula a Média Geométrica da amostra 2
                #gMean muda apenas para o próximo Perfil da gerado a partir da reamostragem
                gMean2 = stats.gmean(am2.iloc[i][self.estado[h]], axis=0)
                
                
                soma = 0 #reinicia o valor da variável soma, que armazena a soma dos quadrados -> usado para o somatório
                for j in range(len(self.cultura)):

                    # Os dividendos são qnj, ou seja o score da cultura N dentro daquele perfil
                    # Eles mudam a cada repetição para podermos calcular o logaritmo da razão entre qnj e g(qn)
                    dividendo2 = am2.iloc[i][self.estado[h]][self.cultura[j]]      
                                    
                    dividendo1 = am1[self.estado[h]][self.cultura[j]]
                    
                    # Calculamos então os logaritmos naturais das razões entre qnj e g(qn)
                    ln1 = np.log(dividendo1/gMean1)
                    ln2 = np.log(dividendo2/gMean2)
                    
                    quadr = np.square(ln1 - ln2) # E então o quadrado da diferença dos logatimos

                    # A soma dos quadrados dos logaritmos é armazenada na variável soma
                    soma = soma + quadr
                
                # Após terminar o somatório, extraimos a raiz quadrada e temos a distancia de Aitchison entre am1 e am2 no estado N, que é salva em arr
                dist = np.sqrt(soma)
                arr.append(dist[0])

            # Após calcular todas as distancias do Estado N calculadas são salvas na lista distancia
            distancias.append(np.array(arr))


        #Estes passos servem para agregar as distâncias calculadas aos dados reamostrados
        indx = pd.MultiIndex.from_arrays([list(self.estado), [self.indexDistancias[0],self.indexDistancias[1]]]) #criamos um novo index
            
        distancias = pd.DataFrame(distancias,index=indx) # um dataframe com as distâncias
        distancias = distancias.transpose() #que é então transposto
        
        # depois fazemos a concatenação do bootstrap e das distancias
        distancias = pd.concat([am2, distancias], axis=1)

        # e após concatenar basta reordenar
        distancias = distancias.sort_index(axis=1, inplace=False)

        #retorna um dataframe com os dados reamostrados e as suas respectivas distancias de Aitchison
        return(distancias)
    ##############################################################################################################################################################


    # OBJETIVO DA FUNÇÃO: eliminar as alfa maiores distâncias
    # Recebe como argumentos o dataframe que contém as distâncias calculadas e o alfa desejado
    ##############################################################################################################################################################
    def elimMaiorDist(self, dist, alph):

        df = [] # df armazena o dataframe com as distâncias já eliminadas

        for i in range(len(self.indexDistancias)): #usamos um laço para eliminar as maiores distâncias tanto de Now quanto de Pref
            
            dt = dist.drop(labels=self.est[i], axis=1) #eliminamos o estado indesejado do dataframe
            
            dt = dt.sort_values((self.estado[i],self.indexDistancias[i]), ascending = False, ignore_index = True) #depois ordenamos em ordem decrescente
            
            
            if i == 0: #Aqui construimos uma lista com os indexes que queremos eliminar precisamos executar uma única vez pois a lista não muda
                elim = math.ceil(alph*len(dt))  # Calculamos quantas distancias precisamos eliminar
                drop = list(range(0,elim)) # Criamos a lista com os indexes destas distancias. Observem que as distancias foram ordenadas em ordem decrecente, então eliminamos as 'elim' primeiras

            dt = dt.drop(index=drop, axis=self.index) # Fazemos a elmininação das maiore distâncias
            
            dt = dt.sort_values((self.estado[i],self.indexDistancias[i]), ascending = False, ignore_index = True) # E depois reconstruimos o índice
            
            
            df.append(dt) # após reconstrução do índice, os perfis são armazenados em df
        
        df = pd.concat([df[0],df[1]], axis=1) #por fim concatenamos os perfis da situação presente e da desejada. observem que df é do tipo dataframe

        del dt

        # por fim a função retorna df
        return(df)
    ##############################################################################################################################################################


    # OBJETIVO DA FUNÇÃO: Calcular dos intervalos de confiança
    # Ela recebe como função a amostra gerada pelo bootstratp já com as maiores distancias eliminadas
    # os intervalos de confiança são definidos como os valores máximo e mínimo de cada cultura dentro das amostras geradas no bootstrap, isto após a eliminação das amostras com maiores distancias
    ##############################################################################################################################################################
    def intvConf(self, amsLimp):
    
        # Estas são listas de apoio
        suporteMax = []
        suporteMin = []
        Max = []
        Min = []
    
        for i in range(len(self.estado)): # temos que ler o valor máximo e mínimo de cada cultura em ambos os estados
            for j in range(len(self.cultura)):

                coluna = amsLimp[self.estado[i]][self.cultura[j]] # Lemos os valores da cultura j no estado i
                
                # E então lemos o máximo e o mínimo
                max = coluna.max() 
                min = coluna.min()
                
                # Eles são então armazenados nas listas de apoio
                # cada lista de apoio vai salvar os valores máximo e mínimo das culturas do estado i
                suporteMax.append(max)
                suporteMin.append(min)

            # Após isso armazenamos os valores máximo e mínimo nas listas Max e Min
            Max.append(suporteMax)
            Min.append(suporteMin)

            #então limpamos as listas de apoio para a proxima execução do laço de repetição
            suporteMax = []
            suporteMin = []

        # por fim geramos séries do panda contendo os intervalos de confiança
        Max = np.array(Max).flatten()
        Max = pd.Series(Max, index=self.index)
        Min = np.array(Min).flatten()
        Min = pd.Series(Min, index=self.index)
        
        intervalo = [Max, Min] # Salvamos as series dos intervalos em uma lista

        del suporteMax
        del suporteMin
        del Max
        del max
        del Min
        del min


        return(intervalo) # E então retornamos essa lista
    ##############################################################################################################################################################





    # OBJETIVO DA FUNÇÃO: calcular o *cfp* dos dados reamostrados/permutados e gera um Dataframe com eles
    # faz uso da função calculoPerfil
    # usa a lsita de dados e o numero de amostras geradas como argumento
    ##############################################################################################################################################################
    def cfpRPCalc(self, lista, qtd):

        temp =[] #Usado para armazenar o perfil ocai calculado

        for i in range(0,int(qtd)): # Calcula o "ocai" de todos os perfis gerados no bootstrap
        
            cfpCalc = calculo.calculoPerfil(self,1,1, lista[i], True) # Faz uso da função CFPBootstrap para o cálculo

            temp.append(cfpCalc) # Os perfis calculados são armazenados neste array temporário

        #concatena os cfp das amostras geradas
        temp = pd.concat(temp, ignore_index=True)


        return(temp)
    ##############################################################################################################################################################

    # OBJETIVO DA FUNÇÃO: Calcular a média geométrica das amostras permutadas
    # Já calcula a média geométrica
    def calcMedPermt(self, permt):

        perfil =[] #Usado para armazenar o perfil ocai calculado
        perfilTemp = []

        for i in range(len(permt)): # Calcula o "ocai" de todos os perfis gerados no bootstrap
        
            #cfpCalc = calculoPerfil(1,1, lista[i], True) # Faz uso da função CFPBootstrap para o cálculo

            dataTemp = permt[i]

            for j in range(len(self.estado)):
                for k in range(len(self.cultura)):
                
                    temp = (dataTemp[self.estado[j],self.cultura[k]]).to_numpy()
                    perfilTemp.append(stats.gmean(temp))
                    
            perfilTemp = pd.Series(perfilTemp, index=self.index)
            perfil.append(perfilTemp)        
            perfilTemp=[]

        del dataTemp
        del permt
        
        #concatena os cfp das amostras geradas
        perfil = pd.concat(perfil, axis=1, ignore_index=True).transpose()


        for i in range(len(self.estado)):
                
                soma = pd.DataFrame(perfil[self.estado[i]]) #Encontramos a soma total do OCAI no Estado i
                mult = pd.DataFrame(100/(soma.sum(axis=1))) #Calculamos o fator multiplicativo
                
                for j in  range(len(self.cultura)): # E multiplicamos todas as cultura do estado i por esse fator
                    soma[self.cultura[j]] = soma[self.cultura[j]]*mult[0]
                
                perfil[self.estado[i]] = soma #Por fim substituimos os valores do dataframe original pelos convertidos para a base 100

        return(perfil)


    # OBJETIVO DA FUNÇÃO: Gerar n amostras Permutadas
    ##############################################################################################################################################################
    def permutac(self, amostra, repeticoes):
        
        cultSortear =[]

        sorteioNow = []
        sorteioPref = []

        nowTemp2 = []
        prefTemp2 = []


        nowAndPref = pd.concat([amostra[self.estado[0]], amostra[self.estado[1]]], ignore_index=1) # Une Now and Pref em uma única amostra

        nowAndPref = nowAndPref.dropna()
        

        for i in self.cultura:                   # Une todas as dimensões de cada cultura em uma lista para serem posteriormente sortedas
            temp = nowAndPref[i].to_numpy()
            temp = temp.flatten()
            temp = temp.tolist()

            cultSortear.append(temp)

        cultSortear = pd.DataFrame(cultSortear, index=self.cultura).transpose() #cria um dataframe com o que iremos sortear. Contém todas as respostas de cada cultura
            

        tamanho = np.array(cultSortear[self.cultura[0]]).size #verifica o tamanho do dataframe do sorteio (usado para divdir)

        intSortear = list(range(0,tamanho)) #indice que será usado no sorteio
    
###################################################################################################################### It is fast
        print("\nSorteio dos Indices")
        time1 = time.time()
        for i in range(len(self.cultura)): # Faz o sorteio dos índices
                    
            
            for j in range(repeticoes):
                
                nowTemp = np.random.choice(intSortear, size=int(tamanho/2), replace=False).tolist() #Como não tem como sortearmos arrays, sorteamos sem reposição os indexes destes arrays
        
                prefTemp = list(set(intSortear) - set(nowTemp)) #eliminamos os numeros já sorteados
        
                prefTemp = np.random.choice(prefTemp, size=int(tamanho/2), replace=False).tolist() #para aleatorizar prefTemp
                
                #Cada repetição gera a coluna da cultura i que será usada na construção de um novo dataframe
                nowTemp2.append(nowTemp)          
                prefTemp2.append(prefTemp)

            # Unificamos as colunas geradas
            # e depois geramos uma lista com elas

            
            nowTemp2 = list(itertools.chain.from_iterable(nowTemp2))
            prefTemp2 = list(itertools.chain.from_iterable(prefTemp2))


            sorteioNow.append(nowTemp2) # todos os sorteios gerados ficam salvos em sorteioNow e sorteioPref
            #print(len(sorteioNow))
            #print(len(sorteioNow[0]))
            sorteioPref.append(prefTemp2) #Cada sorteio corresponde a uma cultura. Todos as permutações daquela cultura são geradas
        

        
            # Temos que limpar as listas nowTemp2 prefTemp2 antes de sortear a próxima cultura
            nowTemp2 = [] 
            prefTemp2 = []
            
   
 
        nowTemp2 = [] 
        prefTemp2 = []
        #print("Sorteio")
        #print(cultSortear)
        #print("print")
        #print(self.cultura[0])
        #print("print2")
        #print(max(sorteioNow[0]))
        #print(sorteioNow[0])


        for i in range(len(self.cultura)):

            # geramos um dataframes com todos os itens sorteados na cultura i        
            nowTemp = cultSortear[self.cultura[i]][sorteioNow[i]].tolist()
            prefTemp = cultSortear[self.cultura[i]][sorteioPref[i]].tolist()
            #print(nowTemp)
            #print("\nIndexesSorteio")
            nowTemp2.append(nowTemp)
            #print(nowTemp2)
            prefTemp2.append(prefTemp)



        nowTemp2 = pd.DataFrame(nowTemp2)
        #print("\Maluco")
        #print(nowTemp2)
        prefTemp2 = pd.DataFrame(prefTemp2)

        df = pd.concat([nowTemp2, prefTemp2], ignore_index=True)
        df = df.set_index(self.index).transpose()
        #print(df)

        nowAndPref =[]

        inicio = 0 #para ajudar no passo d split

        for i in range(repeticoes):
        
            corte = df.iloc[inicio:(inicio+int(tamanho/2))] #faz o corte do dataframe indo de início até (início + tamanho)

            nowAndPref.append(corte) #Salvamos o corte dentro de uma lista

            inicio = inicio + int(tamanho/2) # e incluímos o passo do próximo corte

        del corte
        del df
        del nowTemp2
        del prefTemp2
        del nowTemp
        del prefTemp
        del cultSortear


        return(nowAndPref)
    ##############################################################################################################################################################


    # DISTANCIA AITCHISON dos dados Permutados
    ##############################################################################################################################################################
    def AitchisonPermt(self, amPermt):
        
        distancias = []

        #df = amPermt.drop(amPermt.index, inplace=True)

        for i in range(len(amPermt)):
            y = amPermt.iloc[i]
            y = y.to_frame()
            y = y.transpose()
            y = y.reset_index(drop=True)
            
            dist = calculo.Aitchison(self,y,y,1)

            distancias.append(dist)

        distancias = concat(distancias, ignore_index=True)
        
        del y
        del dist
        del amPermt
        
        return(distancias)
    ##############################################################################################################################################################

    # Verifica se Now e Preferred são iguais
    ##############################################################################################################################################################
    def verifPerm(self,permut, origDist):
        
        permut = permut[self.estado[0]][self.indexDistancias[0]]

        origDist = origDist[self.estado[0]][self.indexDistancias[0]]
        origDist = origDist.to_numpy()

        k = permut[permut >= origDist[0]].count()
    
        self.pValue = (k+1)/(self.numPemut+1)

        del permut
        del origDist

        if self.pValue > self.alphaPermutac: 
            verific = "="
        else:
            verific = "!="
        



        return(verific)
    ##############################################################################################################################################################

    # Salva a situação presente e a desejada em dois arquivos PNG
    ##############################################################################################################################################################
    def plotagem(self, ocai, transp, escMax, nome, legenda):
        
        rng = len(ocai.iloc[0].to_list()) # usado para definir quantas linhas são plotadas - precisa vir antes do transpose

        #Transpõe a matriz para facilitar seu uso posterior
        ocai = ocai.transpose()
        
        
        ind = ocai.index.to_list()
        

        # Define os ângulos em que a informação será plotada
        # O ângulo é medido no sentido anti-horário, com o zero localizado às 3 horas
        # No OCAI temos as culturas são apresentadas nos seguintes ângulos:
        # Adocracia = 45° / Clã = 135° / Hierarquia = 225° / Mercado = 315°
        # Como nosso DataFrame está organizado na ordem "Clã, "Adocracia", "Mercado" e "Hieraquia", e a plotagem é feita na ordem que os ângulos aparecem
        # Temos que indicar os ângulos considerando a organização do dataframe, assim: Angulos = 135, 45, 315, 225, sendo que o último se repete para o polígono não ficar aberto
        theta = np.array([135, 45, 315, 225, 135])
        theta = theta* np.pi / 180    


        # A lista toPlot é usada para armazenar os dados que foram extraidos do dataframe e que serão usados na plotagem
        toPlot = []
        for j in range(rng):
            # namesIntv é usada para localizar o ocai e os intervalos de confiança dentro do dataframe
            temp = ocai.loc[ind[j]].to_list()
            
            temp.append(temp[0])
            toPlot.append(temp)



        # Este trecho controla as linhas de referencia do gráfico
        x=0
        tick=[]
        while x < escMax:
            tick.append(x)

            #alterando o numero que é somado a variável X conseguimos alterar o distanciamento das linhas de referencia
            x = x+5

        # Definimos o gráfico como Polar. A biblioteca matplot tem suporte específico ao gráfico do tipo Radar,
        # entretando para o nosso caso achamos o Polar mais simples e versátil para programar
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Ajustamos para fazer a postagem do OCAI juntamente dos limites inferior e superior
        for i in range(rng):
            ax.plot(theta, toPlot[i], linewidth=1)

        #Definind os nomes e posição da legenda
        if legenda == True:
            ax.legend(ind, loc=8)

        ax.set_rmax(np.max(escMax)) #define o limite do grid
        ax.set_rticks(tick)  # Cria o grid
        ax.set_rlabel_position(-22.5)  # Define a posição dos numeros do grid
        ax.set_xticklabels(['', 'Adhocracia', '', 'Clã', '', 'Hierarquia', '', 'Mercado']) # defindindo o nome dos quadrantes
        ax.grid(linewidth=0.25) #Deixa o grid visível

        
        ax.set_title(nome) #cria o título do gráfico
        
        save = ("Gráficos/" + nome)
        #plt.show() #Desativado por padrão, apenas mostra a imagem
        plt.savefig(save, dpi=600, transparent=transp)
        plt.close()


if __name__ == "__main__":
    gui = guiInterface()
    gui.mainloop()