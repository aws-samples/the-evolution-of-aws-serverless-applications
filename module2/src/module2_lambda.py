import json
import pymysql

def lambda_handler(event, context):
    db = pymysql.connect(
        host=#'your rds endpoint', 
        user=#'your user', 
        password=#'your password'
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