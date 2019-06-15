from datetime import datetime
import pymssql
import mysql.connector
import calendar
teFrom = y[i]['fromDateTime']
# print(ActiveDateFrom)
#p = datetime.strptime(ActiveDateFrom,'%Y-%m-%d')
# print(p)
ActiveDateTo = y[i]['toDateTime']
'''
    print(ActiveDateTo)
    if ActiveDateTo == None:
        
        ActiveDateTo = ActiveDateFrom.replace(day = calendar.monthrange(date.year, date.month)[1])
        ActiveDateTo= new_date.date()
        print(ActiveDateTo)
    '''

TariffChargeType = tariffTypeDict.get(y[i]['rateGroupName'])  # CON
# print(TariffChargeType)
if TariffChargeType == None:
    continue
date = datetime.today()

db = pymssql.connect('aei-az-sqldev.nxe.nxegen.com',
                     'rtisdevel', 'nordic067', 'RTIS_Development')
# , database= 'RTIS_Development'
mydb = db.cursor()

query_tariffID = "SELECT * from NXLGenabilityRateID where G_MasterTariffID =" + \
    "'" + str(tariffid) + "'"
print(query_tariffID)
mydb.execute(query_tariffID)
data = mydb.fetchall()
RateID = data[0][1]
UtilityID = data[0][2]


print(data)

mydb.execute("SELECT * FROM [NXLTariffType]")
data = mydb.fetchall()
tariffTypeDict = {}
for i in data:
    tariffTypeDict[i[2]] = i[0]
print(tariffTypeDict)

mydb.execute("select * from NXLCalcType")
data = mydb.fetchall()
calcTypeDict = {}
for i in data:
    calcTypeDict[i[2]] = i[0]
# print(calcTypeDict)

mydb.execute("SELECT * FROM NXLTimeOfUseType")
data = mydb.fetchall()
touDict = {}
for i in data:
    touDict[i[2]] = i[0]

x = []
y = tariff['results'][0]['rates']
db_update_data = []
# print(y[0])
for i in range(len(y)):

    ActiveDa
    # print(TariffChargeType)

    CalcType = calcTypeDict.get(y[i]['chargeType'])  # CON # MATCH WITH VALUE

    # getting rate sequence and max rate amount
    rate_band = y[i]['rateBands']
    rateAmount = rate_band[0]['rateAmount']
    if len(rate_band) > 1:
        rateSequenceNumber = 1  # Unused

        for rs in rate_band:
            if rs['rateSequenceNumber'] > rateSequenceNumber:
                rateSequenceNumber = rs['rateSequenceNumber']
                rateAmount = rs['rateAmount']

    # print(CalcType)
    if CalcType == 3:
        Rate = 0
        TOU = 8  # 'NA'
        Charges = rateAmount  # y[i]['rateBands'][0]['rateAmount']
    else:
        Rate = rateAmount  # y[i]['rateBands'][0]['rateAmount']
        Charges = 0
        tou = y[i].get('timeOfUse')
        if not tou:
            TOU = 7  # 'All'
        else:
            # CON  # MATCH WITH VALUE
            TOU = touDict[y[i]['timeOfUse']['touType']]

    hasDemandLimit = y[i]['rateBands'][0]['hasDemandLimit']
    if not hasDemandLimit:
        LimitStart = 0
        LimitEnd = 0
    else:
        LimitStart = y[i]['rateBands'][0]['demandUpperLimit']
        LimitEnd = 0

    Notes = 'null'
    CreatedOn = date
    CreatedBy = 'system'
    Version = 1
    val = (RateID, UtilityID, ActiveDateFrom, ActiveDateTo, Rate, TariffChargeType,
           CalcType, TOU, LimitStart, LimitEnd, Charges, Notes, CreatedOn, CreatedBy, Version)
    db_update_data.append(val)


query = "INSERT INTO NXRATECHARGES VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

#val = (100,1,"2014-01-01","2014-06-30",0,6,3,8,0,0,400,'CustomerCharge',"2018-11-12 09:02:19.340","System",1)
# mydb.execute(query,val)
mydb.executemany(query, db_update_data)
db.commit()
print('DONE')
