import datetime
import configparser
import os

def printList(lst, title = ''):
	if title:
		print(title)
	for l in lst:
		print(str(l)[1:-1])

def HtoM(H):
	h = H.split(":")
	return(int(h[0])*60+int(h[1]))

def MtoH(M):
	h = str(M//60)
	if(len(h) == 1):
		h = "0" + h
	m = str(M%60)
	if(len(m) == 1):
		m = "0" + m
	return(h + ':' + m)

def type1toList(From, To): #функції занесення даних із стрічок по файлу у списки та їх форматування
	counter = 0
	for s in From:
		To.append(s.split(" "))
		To[counter][3] = HtoM(To[counter][3])
		To[counter][4] = HtoM(To[counter][4])
		To[counter][0] = int(To[counter][0])
		To[counter][5] = int(To[counter][5])
		counter += 1

def type2toList(From, To):
	counter = 0
	for s in From:
		To.append(s.split(" "))
		To[counter][2] = HtoM(To[counter][2])
		To[counter][0] = int(To[counter][0])
		To[counter][3] = int(To[counter][3])
		counter += 1

def createMatrix(n): #функція створення матриці суміжності
	matrix = []*0
	for c in range(n):
		matrix.append([1000000] * n)
		matrix[c][c] = 0
	return matrix

def addifmin(a, b, new, matrix): #функція що додає ребро у матрицю суміжності якщо воно менше за існуюче
	if matrix[a][b] > new:
		matrix[a][b] = matrix[b][a] = new
		return True
	return False

def fillMatrixTime(trains, stops, MList, matrix): #функції для заповнення матриць суміжності
	for l in trains:
		addifmin(MList.index(l[1]), MList.index(l[2]), l[4], matrix)
		buf = [l[1], 0]
		f = 0
		for li in stops:
			if li[0] == l[0]:
				addifmin(MList.index(buf[0]), MList.index(li[1]), (li[2] - buf[1]), matrix)
				buf[0] = li[1]
				buf[1] = li[2]
				f = 1
			elif f != 0:
				addifmin(MList.index(buf[0]), MList.index(l[2]), (l[4] - buf[1]), matrix)

def fillMatrixPrice(trains, stops, MList, matrix):
	for l in trains:
		addifmin(MList.index(l[1]), MList.index(l[2]), l[5], matrix)
		buf = [l[1], 0]
		f = 0
		for li in stops:
			if li[0] == l[0]:
				addifmin(MList.index(buf[0]), MList.index(li[1]), (li[3] - buf[1]), matrix)
				buf[0] = li[1]
				buf[1] = li[3]
				f = 1
			elif f != 0:
				addifmin(MList.index(buf[0]), MList.index(l[2]), (l[5] - buf[1]), matrix)

def Dijkstra(N, S, matrix): #алгоритм Дейкстри
	valid = [True]*N        
	weight = [1000000]*N
	weight[S] = 0
	for i in range(N):
		min_weight = 1000001
		ID_min_weight = -1
		for i in range(len(weight)):
			if valid[i] and weight[i] < min_weight:
				min_weight = weight[i]
				ID_min_weight = i
		for i in range(N):
			if weight[ID_min_weight] + matrix[ID_min_weight][i] < weight[i]:
				weight[i] = weight[ID_min_weight] + matrix[ID_min_weight][i]
		valid[ID_min_weight] = False
	return weight

def dispFindbyTransPoint(point): #функції відбору рейсів що проходять через станцію пересадки point
	lst = []*0
	counter = 0
	for l in fdispl:
		p = 0
		if l[2] == point:
			lst.append(l.copy())
			lst[counter].insert(1, 0)
			counter += 1
		else:
			for li in dstopsl:
				if li[0] == l[0]:
					p += 1
					if li[1] == point:
						lst.append(l.copy())
						lst[counter][2] = point
						lst[counter][4] = li[2]
						lst[counter][5] = int(li[3]*pricecoef)
						lst[counter].insert(1, p)
						counter += 1
	return lst

def arrFindbyTransPoint(point):
	lst = []*0
	counter = 0
	for l in tarrl:
		p = 0
		if l[1] == point:
			lst.append(l.copy())
			lst[counter].insert(1, 0)
			counter += 1
		else:
			for li in astopsl:
				if li[0] == l[0]:
					p += 1
					if li[1] == point:
						lst.append(l.copy())
						lst[counter][1] = point
						lst[counter][3] += li[2]
						lst[counter][4] -= li[2]
						lst[counter][5] = int((lst[counter][5] - li[3])*pricecoef)
						lst[counter].insert(1, p)
						counter += 1
	return lst

def createVariants(lst): #за списком пересадочних станцій сворює список доступних варіантів маршрутів
	variants = []*0
	for search in lst:
		first = dispFindbyTransPoint(search)
		last = arrFindbyTransPoint(search)
		print()
		printList(first)
		printList(last)
		for l in first:
			for li in last:
				waiting = li[4] - (l[4] + l[5])
				if waiting > waitingTime:
					variants.append([l[0], l[1], li[0], li[1], search, l[4], (l[4] + l[5]), li[4], (li[4] + li[5]), l[6], li[6], MtoH((li[4] + li[5]) - l[4])])
	return variants

def sortbyTime(l):
	return (l[8]-l[5])

def sortbyPrice(l):
	return (l[9]+l[10])

def result(by, ls): #функція для виведення результатів на екран та у файл
	print('\n' + "Results for " + disp + ' - ' + arr + ' by ' + by + ':')
	fileName = str(datetime.datetime.now()).split('.')[0] + ' ' + disp + ' - ' + arr + ' by ' + by + '.txt'
	ln = len(fileName)
	for c in range(ln):
		if fileName[c] == ':':
			fileName = fileName[:c] + '-' + fileName[c+1:]
	fres = open(fileName, 'w')
	for l in ls:
		print(disp, '-', l[4], 'Відправлення/Прибуття', l[5], '/', l[6], 'Час очікування', MtoH(HtoM(l[7]) - HtoM(l[6])), l[4], '-', arr, 'Відправлення/Прибуття', l[7], '/', l[8], 'Загальний час:', MtoH(HtoM(l[8]) - HtoM(l[5])), 'Ціна:', (l[9] + l[10]))
		fres.write(str(l[0:4])[1:-1] + '\n' + disp + ' - ' + l[4] + ' - ' + arr + '\n' + l[5] + '/' + l[6] + ' ' + MtoH(HtoM(l[7]) - HtoM(l[6])) + ' ' + l[7] + '/' + l[8] + ' All time: ' + MtoH(HtoM(l[8]) - HtoM(l[5])) + '\n' + str(l[9]) + ' UAH ' + str(l[10]) + ' UAH Full price: ' + str(l[9] + l[10]) + ' UAH' + '\n'*2)
	fres.close()
	print("Data loaded in file:", fileName)

def create_config(path): #створення конфіг-файлу
	config = configparser.ConfigParser()
	config.add_section("Input")
	config.add_section("Settings")
	config.set("Input", "dispatch", "")
	config.set("Input", "arrive", "")
	config.set("Settings", "time_search", "1")
	config.set("Settings", "price_search", "1")
	config.set("Settings", "optimality_search", "1")
	config.set("Settings", "price_increase", "1.2")
	config.set("Settings", "min_wait_time", "10")
	config.set("Settings", "coefficient_station_filtration_time", "2")
	config.set("Settings", "coefficient_station_filtration_price", "2")
	config.set("Settings", "coefficient_result_filtration_time", "1.4")
	config.set("Settings", "coefficient_result_filtration_price", "1.5")
	with open(path, "w") as config_file:
		config.write(config_file)
 
def get_setting(path, section, setting): #читання конфіг-файлу
	config = configparser.ConfigParser()
	config.read(path)
	value = config.get(section, setting)
	if not value:
		print("Помилка: Введіть вхідні дані у файл 'config.cfg'")
		input()
		exit()
	msg = "{section} {setting} is {value}".format(section=section, setting=setting, value=value)
	print(msg)
	return value
 
 
if __name__ == "__main__": #читання конфіг-файлу
	path = "config.cfg"
	if not os.path.exists(path):
		create_config(path)
		print("Помилка: Введіть вхідні дані у файл 'config.cfg'")
		input()
		exit()
	disp = get_setting(path, 'Input', 'dispatch')
	arr = get_setting(path, 'Input', 'arrive')
	timeFlag = float(get_setting(path, "Settings", "time_search")) #виконання пошуку за часом
	if (timeFlag == 1):
		timeFlag = True
	else:
		timeFlag = False
	priceFlag = int(get_setting(path, "Settings", "price_search")) #виконання пошуку за ціною
	if (priceFlag == 1):
		priceFlag = True
	else:
		priceFlag = False
	optimalityFlag = float(get_setting(path, "Settings", "optimality_search")) #виконання пошуку за обома параметрами
	if (optimalityFlag == 1):
		optimalityFlag = True
	else:
		optimalityFlag = False
	pricecoef = float(get_setting(path, "Settings", "price_increase")) #коефіцієнт збільшення ціни
	waitingTime = int(get_setting(path, "Settings", "min_wait_time")) #мінімальний час очікування на пересадочній станції
	coefFTM = float(get_setting(path, "Settings", "coefficient_station_filtration_time")) #коефіцієнт фільтрації тривалості маршруту від найшвидшого для відбору станцій пересадки
	coefFPM = float(get_setting(path, "Settings", "coefficient_station_filtration_price")) #коефіцієнт фільтрації ціни маршруту від найдешевшого для відбору станцій пересадки
	coefFTF = float(get_setting(path, "Settings", "coefficient_result_filtration_time")) #коефіцієнт фільтрації тривалості підібраних рейсів від найкоротшого для фінальних результатів
	coefFPF = float(get_setting(path, "Settings", "coefficient_result_filtration_price")) #коефіцієнт фільтрації ціни підібраних рейсів від найдешевшого для фінальних результатів

fdispf = open("fromdisp.txt", "r") #читання з файлів у стрічки
tarrf = open("toarr.txt", "r")
dstopsf = open("dstops.txt", "r")
astopsf = open("astops.txt", "r")
fdisps = fdispf.readlines()
tarrs = tarrf.readlines()
dstopss = dstopsf.readlines()
astopss = astopsf.readlines()
fdispf.close()
tarrf.close()
dstopsf.close()
astopsf.close()

fdispl = []*0 # створення списків та занесення у них даних з файлів
tarrl = []*0
dstopsl = []*0
astopsl = []*0
type1toList(fdisps, fdispl)
type1toList(tarrs, tarrl)
type2toList(dstopss, dstopsl)
type2toList(astopss, astopsl)

print()
printList(fdispl)
print()
printList(tarrl)
print()
printList(dstopsl)
print()
printList(astopsl)

dispMatrixList = [disp] #створення списків до матриць суміжності
arrMatrixList = [arr]
DN = 1
AN = 1
for l in fdispl:
	if l[2] not in dispMatrixList:
		dispMatrixList.append(l[2])
		DN += 1
for l in dstopsl:
	if l[1] not in dispMatrixList:
		dispMatrixList.append(l[1])
		DN += 1
for l in tarrl:
	if l[1] not in arrMatrixList:
		arrMatrixList.append(l[1])
		AN += 1
for l in astopsl:
	if l[1] not in arrMatrixList:
		arrMatrixList.append(l[1])
		AN += 1

print(dispMatrixList, DN)
print(arrMatrixList, AN)

if (timeFlag or optimalityFlag):
	dispMatrixTime = createMatrix(DN) #створення і заповнення матриць суміжностей
	arrMatrixTime = createMatrix(AN)
	fillMatrixTime(fdispl, dstopsl, dispMatrixList, dispMatrixTime)
	fillMatrixTime(tarrl, astopsl, arrMatrixList, arrMatrixTime)
if (priceFlag):
	dispMatrixPrice = createMatrix(DN)
	arrMatrixPrice = createMatrix(AN)
	fillMatrixPrice(fdispl, dstopsl, dispMatrixList, dispMatrixPrice)
	fillMatrixPrice(tarrl, astopsl, arrMatrixList, arrMatrixPrice)

print()
print(dispMatrixList, DN)
if (timeFlag or optimalityFlag):
	printList(dispMatrixTime, 'Time:')
if (priceFlag):
	printList(dispMatrixPrice, 'Price:')
print()
print(arrMatrixList, AN)
if (timeFlag or optimalityFlag):
	printList(arrMatrixTime, 'Time:')
if (priceFlag):
	printList(arrMatrixPrice, 'Price:')


if (timeFlag or optimalityFlag):
	weightDispTime = Dijkstra(DN, 0, dispMatrixTime) #виконання алгоритму Дейкстри
	weightArrTime = Dijkstra(AN, 0, arrMatrixTime)
	dispMatrixTime.clear()
	arrMatrixTime.clear()
	del(dispMatrixTime)
	del(arrMatrixTime)
	for i in range(DN):
		weightDispTime[i] = MtoH(weightDispTime[i])
	for i in range(AN):
		weightArrTime[i] = MtoH(weightArrTime[i])
if (priceFlag):
	weightDispPrice = Dijkstra(DN, 0, dispMatrixPrice)
	weightArrPrice = Dijkstra(AN, 0, arrMatrixPrice)
	dispMatrixPrice.clear()
	arrMatrixPrice.clear()
	del(dispMatrixPrice)
	del(arrMatrixPrice)

intersections = dispMatrixList.copy() #створення списку пунктів пересадки
Itrc = DN
for c in range(-DN, 0):
	if intersections[c] not in arrMatrixList:
		intersections.pop(c)
		Itrc -= 1

print()
print(dispMatrixList, DN)
if (timeFlag or optimalityFlag):
	print(weightDispTime, 'by time')
if (priceFlag):
	print(weightDispPrice, 'by price')
print()
print(arrMatrixList, AN)
if (timeFlag or optimalityFlag):
	print(weightArrTime, 'by time')
if (priceFlag):
	print(weightArrPrice, 'by price')
print()
print(intersections, 'intersections')

if (timeFlag or optimalityFlag):
	weighItrcTime = []*0
	for s in intersections:
		weighItrcTime.append( HtoM(weightDispTime[dispMatrixList.index(s)]) + HtoM(weightArrTime[arrMatrixList.index(s)]) )
	intersectionsT = intersections.copy() #фільтрація пунктів пересадки за коефіцієнтами для кожного з методів пошуку
	min = 1000000
	for i in weighItrcTime:
		if i < min:
			min = i
	for c in range(-Itrc, 0):
		if weighItrcTime[c] > min*coefFTM:
			weighItrcTime.pop(c)
			intersectionsT.pop(c)
			print()
	print(intersectionsT)
	print(weighItrcTime, 'time')
if (priceFlag):
	weighItrcPrice = []*0
	for s in intersections:
		weighItrcPrice.append(weightDispPrice[dispMatrixList.index(s)] + weightArrPrice[arrMatrixList.index(s)])
	intersectionsP = intersections.copy()
	min = 1000000
	for i in weighItrcPrice:
		if i < min:
			min = i
	for c in range(-Itrc, 0):
		if weighItrcPrice[c] > min*coefFPM:
			weighItrcPrice.pop(c)
			intersectionsP.pop(c)
	print()
	print(intersectionsP)
	print(weighItrcPrice, 'price')

if (timeFlag or optimalityFlag):
	variantsTime = createVariants(intersectionsT)
	print()
	printList(variantsTime)
if (priceFlag):
	variantsPrice = createVariants(intersectionsP)
	print()
	printList(variantsPrice)
if (optimalityFlag):
	variantsOptimality = []*0
	for l in variantsTime:
		variantsOptimality.append(l.copy())

if (timeFlag):
	variantsTime.sort(key=sortbyPrice)
	variantsTime.sort(key=sortbyTime)
	counter = 0 #видалення найменш вигідних варіантів
	minTime = variantsTime[0][8] - variantsTime[0][5]
	for l in variantsTime:
		if (l[8] - l[5]) > minTime*coefFTF:
			variantsTime = variantsTime[0:counter]
			break
		l[5] = MtoH(l[5])
		l[6] = MtoH(l[6])
		l[7] = MtoH(l[7])
		l[8] = MtoH(l[8])
		counter += 1
	print()
	printList(variantsTime)

if (priceFlag):
	variantsPrice.sort(key=sortbyTime)
	variantsPrice.sort(key=sortbyPrice)
	counter = 0
	minPrice = variantsPrice[0][9] + variantsPrice[0][10]
	for l in variantsPrice:
		if (l[9] + l[10]) > minPrice*coefFPF:
			variantsPrice = variantsPrice[0:counter]
			break
		l[5] = MtoH(l[5])
		l[6] = MtoH(l[6])
		l[7] = MtoH(l[7])
		l[8] = MtoH(l[8])
		counter += 1
	print()
	printList(variantsPrice)

if (optimalityFlag):
	variantsOptimality.sort(key=sortbyTime)
	counter = 0
	minTime = variantsOptimality[0][8] - variantsOptimality[0][5]
	for l in variantsOptimality:
		if (l[8] - l[5]) > minTime*coefFTF:
			variantsOptimality = variantsOptimality[0:counter]
			break
		counter += 1
	variantsOptimality.sort(key=sortbyPrice)
	counter = 0
	minPrice = variantsOptimality[0][9] + variantsOptimality[0][10]
	for l in variantsOptimality:
		if (l[9] + l[10]) > minPrice*coefFPF:
			variantsOptimality = variantsOptimality[0:counter]
			break
		l[5] = MtoH(l[5])
		l[6] = MtoH(l[6])
		l[7] = MtoH(l[7])
		l[8] = MtoH(l[8])
		counter += 1
	print()
	printList(variantsOptimality)

if (timeFlag):
	print()
	result('time', variantsTime)
if (priceFlag):
	print()
	result('price', variantsPrice)
if (optimalityFlag):
	print()
	result('optimality', variantsOptimality)

input()