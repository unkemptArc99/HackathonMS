from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import zipfile
import json
# from OpenSSL import SSL


# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_flie('server.crt')

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello():
    return "Hello World!"

@app.route("/publish", methods=['POST'])
@cross_origin()
def publish():
    try:
        if request.method == 'POST':
            # return str(os.getcwd()) + " " + str(os.listdir(os.getcwd())), 200
            password = request.form['password']
            if password == "iamhacking":
                fileNum = request.form['id']
                data = request.form['file']
                if not os.path.exists(os.path.join(os.getcwd(), "files")):
                    os.mkdir("files")
                fileName = os.path.join(os.getcwd(), "files", fileNum + '.txt')
                writeFlag = 'w'
                if os.path.exists(fileName):
                    writeFlag = 'a'
                with open(fileName, writeFlag) as f:
                    f.write(data)
                    f.write("\n")
                return '', 200
            else:
                return '',400
    except Exception as e:
        return e, 400

@app.route("/download", methods=['POST'])
@cross_origin()
def download():
    if request.method == 'POST':
        password = request.form['password']
        if password == "iamhacking":
            dirName = os.path.join(os.getcwd(), "files")
            if 'id' in request.form.keys():
                fileName = request.form['id'] + ".txt"
                return send_from_directory(directory=dirName, filename=fileName)
            else:
                files = os.listdir(dirName)
                downloadableFiles = list(filter(lambda x : x.endswith(".txt"), files))
                if os.path.exists(os.path.join(os.getcwd(), "Files.zip")):
                    os.remove(os.path.join(os.getcwd(), "Files.zip"))
                zipf = zipfile.ZipFile('Files.zip','w', zipfile.ZIP_DEFLATED)
                for file in downloadableFiles:
                    zipf.write(os.path.join('files', file))
                zipf.close()
                return send_file('Files.zip',
                        mimetype = 'zip',
                        attachment_filename= 'Files.zip',
                        as_attachment = True)
            # mimeFields = {}
            # for files in downloadableFiles:
            #     mimeFields[files] = (files, open(".\\files\\" + files, 'r'), 'text/plain')
            # m = MultipartEncoder(mimeFields)
            # return Response(m.to_string(), mimetype=m.content_type)

@app.route("/delete", methods=['POST'])
@cross_origin()
def delete():
    if request.method == 'POST':
        password = request.form['password']
        if password == "iamhacking":
            if 'id' in request.form.keys():
                fileName = os.path.join(os.getcwd(), "files", request.form['id'] + ".txt")
                if(os.path.exists(fileName)):
                    os.remove(fileName)
                    return 'File Deleted!', 200
                else:
                    return 'Wrong ID', 400
            else:
                return 'Nothing deleted!', 200

@app.route("/figures/<path:path>", methods=['GET'])
@cross_origin()
def figure(path):
    return send_from_directory(os.path.join(os.getcwd(), "figures"), path)

def timeCalculator(fileName, deadlineDate):
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
    dataPoints = {}
    dataAddInPoints = {}
    for key in data.keys():
        timeList = np.array(data[key])
        dataPoints[key] = timeList.size
        data[key] = np.mean(timeList)
    for key in dataAddIn.keys():
        timeList = np.array(dataAddIn[key])
        dataAddInPoints[key] = timeList.size
        dataAddIn[key] = np.mean(timeList)
    dataList = np.array(list(data.values()))
    dataAddInList = np.array(list(dataAddIn.values()))
    combinedData = np.column_stack((dataList, dataAddInList))
    return combinedData, list(data.keys()), dataPoints, dataAddInPoints

@app.route("/getTime", methods=['GET'])
@cross_origin()
def getTime():
    if request.method == 'GET':
        username = request.args.get("user")
        if username is None:
            return '10'
        else:
            fileName = os.path.join(os.getcwd(), "files", username + ".txt")
            deadlineDate = datetime.now().replace(hour=0, minute=0, second=0)
            combinedData, dates, dataPoints, dataAddInPoints = timeCalculator(fileName, deadlineDate)
            print(combinedData, dates, dataPoints, dataAddInPoints)
            netAvg = (combinedData[0][0]*dataPoints[dates[0]] + combinedData[0][1]*dataAddInPoints[dates[0]])/(dataPoints[dates[0]] + dataAddInPoints[dates[0]])
            return str(((combinedData[0][0] - netAvg)*100.00)/combinedData[0][0])

@app.route("/graph", methods=['GET'])
@cross_origin()
def graph():
    if request.method == 'GET':
        username = request.args.get("user")
        fileName = os.path.join(os.getcwd(), "files", username + ".txt")
        deadlineDate = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0)

        combinedData, dates, dataPoints, dataAddInPoints = timeCalculator(fileName, deadlineDate)

        plotData = pd.DataFrame(combinedData, index=[dates], columns=['Compose Time without addin', 'Compose Time with addins'])
        plotDataFig = plotData.plot.bar(rot=0).get_figure()

        if not os.path.exists(os.path.join(os.getcwd(), "figures")):
            os.mkdir(os.path.join(os.getcwd(), "figures"))
        picName = username + ".png"
        plotDataFig.savefig(os.path.join(os.getcwd(), "figures", picName))
        return "https://hackabhiapp.azurewebsites.net/figures/" + picName, 200

if __name__ == '__main__':
    app.run(debug=True)