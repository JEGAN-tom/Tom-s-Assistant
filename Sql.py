import sys
import platform
try:
    import MySQLdb
    from MySQLdb.cursors import DictCursor
except:
    import mysql.connector as MySQLdb
import traceback

# Database Configuration
Host = "localhost"
Username = "root"
Password = "root"
PersonalAssistantTom = "personalassistanttom"

# Task Table Definitions
Hw_Db_TableDetails = {
    "Windows": {
        "Tasks": {
            "TaskId": {
                "Field": "TaskId",
                "Type": "int",
                "Null": "NO",
                "Key": "PRI",
                "Default": "None",
                "Extra": "auto_increment"
            },
            "Name": {
                "Field": "Name",
                "Type": "varchar(255)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "TaskType": {
                "Field": "TaskType",
                "Type": "varchar(50)",
                "Null": "NO",
                "Key": "",
                "Default": "Daily",
                "Extra": ""
            },
            "TaskParams": {
                "Field": "TaskParams",
                "Type": "varchar(255)",
                "Null": "YES",
                "Key": "",
                "Default": "NULL",
                "Extra": ""
            }
        },
        "TaskSchedules": {
            "ScheduleId": {
                "Field": "ScheduleId",
                "Type": "int",
                "Null": "NO",
                "Key": "PRI",
                "Default": "None",
                "Extra": "auto_increment"
            },
            "TaskId": {
                "Field": "TaskId",
                "Type": "int",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            },
            "Name": {
                "Field": "Name",
                "Type": "varchar(255)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "Date": {
                "Field": "Date",
                "Type": "varchar(10)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "OrderIndex": {
                "Field": "OrderIndex",
                "Type": "int",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            },
            "Completed": {
                "Field": "Completed",
                "Type": "int",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            }
        }
    },
    "Linux": {
        "Tasks": {
            "TaskId": {
                "Field": "TaskId",
                "Type": "int(11)",
                "Null": "NO",
                "Key": "PRI",
                "Default": "None",
                "Extra": "auto_increment"
            },
            "Name": {
                "Field": "Name",
                "Type": "varchar(255)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "TaskType": {
                "Field": "TaskType",
                "Type": "varchar(50)",
                "Null": "NO",
                "Key": "",
                "Default": "Daily",
                "Extra": ""
            },
            "TaskParams": {
                "Field": "TaskParams",
                "Type": "varchar(255)",
                "Null": "YES",
                "Key": "",
                "Default": "NULL",
                "Extra": ""
            }
        },
        "TaskSchedules": {
            "ScheduleId": {
                "Field": "ScheduleId",
                "Type": "int(11)",
                "Null": "NO",
                "Key": "PRI",
                "Default": "None",
                "Extra": "auto_increment"
            },
            "TaskId": {
                "Field": "TaskId",
                "Type": "int(11)",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            },
            "Name": {
                "Field": "Name",
                "Type": "varchar(255)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "Date": {
                "Field": "Date",
                "Type": "varchar(10)",
                "Null": "NO",
                "Key": "",
                "Default": "None",
                "Extra": ""
            },
            "OrderIndex": {
                "Field": "OrderIndex",
                "Type": "int(11)",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            },
            "Completed": {
                "Field": "Completed",
                "Type": "int(11)",
                "Null": "NO",
                "Key": "",
                "Default": "0",
                "Extra": ""
            }
        }
    }
}

MyPlatform = platform.system()

# Database Functions
def CreateDatabase(DatabaseName):
    Db = MySQLdb.connect(host=Host, user=Username, password=Password)
    Cursor = Db.cursor()
    Cursor.execute("CREATE DATABASE IF NOT EXISTS " + str(DatabaseName))
    Cursor.close()
    Db.close()

def CreateTable(TableName, TableDetails, Database):
    Query = "CREATE TABLE IF NOT EXISTS `" + TableName + "` ("
    primary_key_field = None
    
    for FieldDetails in TableDetails.values():
        if FieldDetails['Null'] == 'YES':
            DefaultString = "DEFAULT NULL"
        elif FieldDetails['Default'] != 'None':
            Default = FieldDetails['Default']
            if 'varchar' in FieldDetails['Type']:
                DefaultString = f"NOT NULL DEFAULT '{Default}'"
            else:
                DefaultString = f"NOT NULL DEFAULT {Default}"
        else:
            DefaultString = "NOT NULL"
        
        ExtraString = FieldDetails['Extra'] if FieldDetails['Extra'] else ''
        if FieldDetails['Key'] == 'PRI':
            primary_key_field = FieldDetails['Field']
        
        Query += f"{FieldDetails['Field']} {FieldDetails['Type']} {DefaultString} {ExtraString}, "
    
    if primary_key_field:
        Query += f"PRIMARY KEY ({primary_key_field})"
    Query = Query.rstrip(", ") + ")"
    
    Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=Database)
    Cursor = Db.cursor()
    Cursor.execute(Query)
    Cursor.close()
    Db.close()

def InsertRow(Table, RowDetails):
    ColumnList = list(RowDetails.keys())
    ColumnNameString = ','.join(ColumnList)
    ValuesString = ','.join(['%s'] * len(ColumnList))
    Values = [RowDetails[key] for key in ColumnList]
    Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
    Cursor = Db.cursor()
    Cursor.execute(f"INSERT INTO {Table.lower()} ({ColumnNameString}) VALUES ({ValuesString})", Values)
    Db.commit()
    Result = Cursor.lastrowid
    Cursor.close()
    Db.close()
    return Result

def GetAllRows(Table):
    Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
    try:
        Cursor = Db.cursor(cursorclass=DictCursor)
    except:
        Cursor = Db.cursor(dictionary=True)
    Cursor.execute(f"SELECT * FROM {Table.lower()}")
    Results = Cursor.fetchall()
    Cursor.close()
    Db.close()
    return list(Results) if isinstance(Results, tuple) else Results

def UpdateRow(Table, RowDetails, condition):
    SetClause = ','.join([f"{key}=%s" for key in RowDetails.keys() if key != condition])
    Values = [RowDetails[key] for key in RowDetails.keys() if key != condition] + [RowDetails[condition]]
    Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
    Cursor = Db.cursor()
    Cursor.execute(f"UPDATE {Table.lower()} SET {SetClause} WHERE {condition}=%s", Values)
    Db.commit()
    Cursor.close()
    Db.close()

def RemoveRow(Table, condition, value):
    Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
    Cursor = Db.cursor()
    Cursor.execute(f"DELETE FROM {Table.lower()} WHERE {condition}=%s", (value,))
    Db.commit()
    Cursor.close()
    Db.close()

def CheckTableStructure(TableName):
    try:
        Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
        Cursor = Db.cursor()
        Cursor.execute(f"DESCRIBE {TableName.lower()}")
        Results = Cursor.fetchall()
        ColumnList = [Column[0] for Column in Cursor.description]
        FinalResult = {TableColumn[0]: {ColumnList[Column]: str(TableColumn[Column]) for Column in range(len(ColumnList))} for TableColumn in Results}
        Cursor.close()
        Db.close()
        return FinalResult
    except:
        return None

def Hw_Db_TableInitialization():
    for Table, TableDetails in Hw_Db_TableDetails[MyPlatform].items():
        table_name = Table.lower()
        existing_structure = CheckTableStructure(table_name)
        
        if existing_structure is None:
            CreateTable(table_name, TableDetails, PersonalAssistantTom)
        else:
            expected_columns = set(TableDetails.keys())
            existing_columns = set(existing_structure.keys())
            
            if expected_columns != existing_columns:
                Db = MySQLdb.connect(host=Host, user=Username, password=Password, database=PersonalAssistantTom)
                Cursor = Db.cursor()
                Cursor.execute(f"DROP TABLE {table_name}")
                Cursor.close()
                Db.close()
                CreateTable(table_name, TableDetails, PersonalAssistantTom)

if __name__ == '__main__':
    CreateDatabase(PersonalAssistantTom)
    Hw_Db_TableInitialization()