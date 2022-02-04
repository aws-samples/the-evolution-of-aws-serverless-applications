import json
import pymysql

def lambda_handler(event, context):
    db = pymysql.connect(
        host='YOUR RDS ENDPOINT', 
        user='YOUR DATABASE MASTER USERNAME', 
        password='YOUR MASTER PASSWORD'
        )

    cursor = db.cursor()
    
    cursor.execute("select now()")
    result = cursor.fetchone()

    db.commit()
    db.close()
    
    return {
        'statusCode': 200,
        'body': json.dumps(result[0].isoformat())
    }