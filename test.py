import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import json

fileName = os.path.join(os.getcwd(), "files", "abhi12.txt")
deadlineDate = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0)
data = {}
dataAddIn = {}
with open(fileName, 'r') as f:
    for line in reversed(list(f)):
        jsonLine = json.loads(line)
        startDateTimeStr = jsonLine['startTime']
        endDateTimeStr = jsonLine['endTime']
        startDateOfEntry = datetime.strptime(startDateTimeStr, "%a, %d %b %Y %H:%M:%S %Z")
        endDateOfEntry = datetime.strptime(endDateTimeStr, "%a, %d %b %Y %H:%M:%S %Z")
        addInUsed = True
        addInList = jsonLine['addInList']
        if addInList == "[]":
            addInUsed = False
        if endDateOfEntry > deadlineDate:
            if addInUsed:
                if str(endDateOfEntry.date()) in dataAddIn.keys():
                    dataAddIn[str(endDateOfEntry.date())].append((endDateOfEntry - startDateOfEntry).total_seconds())
                else:
                    dataAddIn[str(endDateOfEntry.date())] = [(endDateOfEntry - startDateOfEntry).total_seconds()]
            else:
                if str(endDateOfEntry.date()) in data.keys():
                    data[str(endDateOfEntry.date())].append((endDateOfEntry - startDateOfEntry).total_seconds())
                else:
                    data[str(endDateOfEntry.date())] = [(endDateOfEntry - startDateOfEntry).total_seconds()]
        else:
            break
print(data)
print(dataAddIn)
for key in data.keys():
    timeList = np.array(data[key])
    data[key] = np.mean(timeList)
for key in dataAddIn.keys():
    timeList = np.array(dataAddIn[key])
    dataAddIn[key] = np.mean(timeList)
print(data)
print(dataAddIn)
dataList = np.array(list(data.values()))
dataAddInList = np.array(list(dataAddIn.values()))
combinedData = np.column_stack((dataList, dataAddInList))
print(combinedData)
plotData = pd.DataFrame(combinedData, index=[data.keys()], columns=['Compose Time without addin', 'Compose Time with addins'])
print(plotData)
plotDataFig = plotData.plot().get_figure()