# Module 3. 서버리스 애플리케이션의 DB 사용 경험 개선

앞서 [Module 2. REST API 기반 서버리스 애플리케이션](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/README.md) 에서 간단한 서버리스 애플리케이션을 개발해봤습니다. 이 때는 DB 인증 정보를 Lambda 함수의 코드 자체에 직접 포함해 접근했는데 이는 보안상 안전한 방법은 아닙니다. 이런 문제를 극복하기 위해서 권장되는 방법은 [AWS Secrets Manager 를 활용해 Lambda 함수에 DB 크리덴셜 정보를 전달](https://aws.amazon.com/blogs/security/rotate-amazon-rds-database-credentials-automatically-with-aws-secrets-manager/) 하는 것입니다.

또한 DB 의 커넥션을 모두 함수 내부의 Handler 에서 처리했습니다. 이렇게 개발할 경우 Lambda 함수가 호출될 때마다 DB 에 연결하고 종료하는 것이 반복되므로 실행 컨텍스트 재활용 측면에서 성능에 좋지 않은 영향이 생기게 됩니다. 하지만 DB 커넥션을 전역으로 선언할 경우 커넥션 종료에 대한 로직 처리가 어려워 각 DB 엔진이의 최대 연결 수를 초과하는 문제가 발생할 수 있습니다. 이 문제는 [Amazon RDS Proxy 를 통해 풀을 관리](https://docs.aws.amazon.com/lambda/latest/dg/configuration-database.html) 하고 Lambda 함수에서 쿼리를 릴레이하면 큰 변경 없이 해결이 가능합니다.

[서버리스 애플리케이션에는 사용할 수 있는 다양한 DB 옵션](https://aws.amazon.com/blogs/compute/understanding-database-options-for-your-serverless-web-applications/) 이 존재합니다. Module 3 에서는 이 중 가장 많이 활용되는 형태 중 하나인 관계형 데이터베이스를 기준으로 안전하게 DB 에 연결하고 커넥션 풀을 효과적으로 관리하기 위해 아래 아키텍처와 같이 AWS Secrets Manager 와 Amazon RDS Proxy 를 활용해보겠습니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/module3_architecture.jpg"></img></div>

이번 실습은 앞서 Module 2 에서 생성한 서버리스 애플리케이션을 그대로 활용합니다.

### Step 1. AWS Secrets Manager 구성

[AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 를 사용하면 애플리케이션, 서비스, IT 리소스에 액세스할 때 필요한 보안 정보를 보하할 수 있습니다. 특히 DB 크리덴셜 뿐 아니라 API 키와 같은 보안 정보를 손쉽게 교체, 관리 및 검색하는게 가능합니다. 이를 사용하면 애플리케이션은 Secrets Manager API 를 호출하여 크리덴셜 정보를 읽으므로, 민감한 정보를 평문으로 하드코딩할 필요가 없는 보안상의 이점이 있습니다.

이번 단계에서는 앞서 생성한 Lambda 함수에 직접 하드코딩 되어있는 DB 크리덴셜 정보를 Secrets Manager API 를 호출하여 불러오는 구성을 수행합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Secretes Manager 서비스로 이동합니다.
2. 화면의 [Store a new secret] 버튼을 클릭합니다.
3. Select secret type 은 [Credential for RDS database] 옵션을 선택하고 Module 2 에서 생성했던 DB 크리덴셜 정보를 입력합니다. [User name] 에는 `admin` [Password] 에는 `Passw0rd` 를 입력합니다. 아래 Select which RDS database this secret will access 옵션에서는 이전에 생성한 **serverless-app-rds** 를 선택한 뒤 [Next] 버튼을 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/1.png"></img></div>

4. [Secret name] 에는 `serverless-app-rds-secret` 을 입력하고 나머지는 기본 옵션을 유지한 채 [Next] 버튼을 클릭합니다.
5. [DB 크리덴셜을 자동으로 로테이션](https://aws.amazon.com/blogs/security/rotate-amazon-rds-database-credentials-automatically-with-aws-secrets-manager/) 할 수도 있습니다. 이번 실습에서는 이를 활용하지는 않습니다. [Next] 버튼을 클릭합니다.
6. 설정 값을 검토한 뒤 하단의 [Store] 를 선택하여 DB 인증 정보 저장을 완료합니다.
7. Secrets Manager 를 사용하면 기본적으로는 퍼블릭 통신을 통해 DB 크리덴셜을 가져오게 되지만 [VPC Endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html) 를 사용하면 프라이빗 엔드포인트를 통해 VPC 내의 리소스가 직접 액세스 할 수 있습니다. VPC Endpoints 설정을 위해 Amazon VPC 서비스로 이동합니다.
8. 좌측의 [Your VPCs] 로 이동한 뒤 실습에 사용 중인 **serverless-app** 을 선택하고 상단의 [Actions] 메뉴의 [Edit DNS hostnames] 를 선택합니다.
9. [DNS hostnames] 의 [Enable] 을 체크하여 활성화 합니다. [Save changes] 버튼을 클릭해 변경사항을 저장합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/0.png"></img></div>

10. VPC Endpoints 설정에는 보안 그룹이 필요합니다. 오늘 실습의 Secrets Manager 의 경우 Lambda 에서 접근할 수 있어야 합니다. 좌측의 [Security Group] 메뉴로 이동한 뒤 [Create security group] 버튼을 선택합니다.
11. [Security group name] 에는 `secret-sg` 를 입력하고 [Description] 을 적은 뒤 [VPC] 는 앞서 생성한 **serverless-app** 을 선택합니다.
12. 하단의 Inbound rules 에서 [Add rule] 버튼을 클릭하여 인바운드 규칙을 추가합니다. [Type] 은 **HTTPS** 를 선택하고 [Source] 에는 앞서 생성한 lambda-sg 를 선택합니다. 아래 [Create security group] 을 선택하여 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/2.png"></img></div>

13. VPC Endpoints 를 설정합니다. 좌측의 [Endpoints] 메뉴로 이동한 뒤 [Create Endpoint] 버튼을 선택합니다.
14. [Service category] 는 **AWS services** 를 선택하고 아래의 [Service Name] 에 `com.amazonaws.ap-northeast-2.secretsmanager` 를 검색하여 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/3.png"></img></div> 

15. 하단의 [VPC] 는 **serverless-app** 을 선택하고 아래 [Subnets] 에는 Secrets Manager 를 위해 생성한 **secret-subnet-a** 와 **secret-subnet-c** 를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/4.png"></img></div>

16. 아래 [Security group] 에는 **secret-sg** 를 선택해줍니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/5.png"></img></div>

17. 여기까지 잘 설정했다면 [Create endpoint] 버튼을 클릭하여 VPC Endpoints 생성을 완료합니다. 잠시후 다음과 같이 Status 가 available 이 되면 다음으로 진행합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/6.png"></img></div>

### Step 2. Amazon RDS Proxy 구성

서버리스 애플리케이션에서 효과적으로 RDS 를 사용하는 것은 쉽지 않습니다. 서버리스 아키텍처를 기반으로 구축된 애플리케이션은 DB 에 다수의 커넥션을 만들어 max_connections 옵션을 초과하는 에러가 발생하거나 빠른 속도로 DB 커넥션을 열고 닫음으로 과도하게 메모리와 컴퓨팅 리소스를 소진하는 경우가 발생합니다. Amazon RDS Proxy 를 사용하면 애플리케이션과 DB 사이의 연결을 풀링하고 공유할 수 있기 때문에 이런 어려움을 극복할 수 있습니다. 또한 DB 장애조치 시에 새로운 DB 로 연결을 복구하는 시간 역시 최대 66% 단축할 수 있도록 구현되어 있습니다. [RDS Proxy 를 활용한 애플리케이션 가용성 향상](https://aws.amazon.com/blogs/database/improving-application-availability-with-amazon-rds-proxy/) 을 보면 보다 자세한 내용을 살펴볼 수 있습니다.

이번 실습에는 개발 중인 서버리스 애플리케이션에서 관계형 데이터베이스 사용을 효율적으로 바꿀 고가용상 DB 프록시 서비스인 RDS Proxy 를 구성합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon RDS 서비스로 이동합니다.
2. 좌측의 [Proxies] 메뉴를 선택한 뒤 [Create proxy] 버튼을 클릭합니다.
3. [Proxy identifier] 에는 `serverless-app-rds-proxy` 를 입력하고 [Engine compatibility] 는 **MySQL** 을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/7.png"></img></div>

4. 하단의 Target group configuration 에서 [Database] 는 Module 2. 에서 생성한 **serverless-app-rds** 를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/8.png"></img></div>

5. Connectivity 설정에서 [Secrets Manager secret(s)] 에는 앞서 생성한 **serverless-app-rds-secret** 을 선택합니다.
6. [Subnets] 에는 VPC 의 모든 서브넷이 선택되어 있습니다. RDS 에서 사용하는 **rds-subnet-a, rds-subnet-c** 를 확인하여 나머지는 제거합니다.
7. [Additional connectivity configuration] 의 드롭다운 버튼을 클릭한 뒤 [Existing VPC security groups] 에는 **rds-sg** 를 추가합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/9.png"></img></div>

8. 설정을 잘 했다면 하단의 [Create proxy] 버튼을 클릭하여 생성을 시작합니다. RDS Proxy 를 사용할 수 있게 되는 데는 몇 분 정도 소요됩니다.
9. 생성이 완료된 후 해당 RDS Proxy 를 선택해보면 다음과 같이 [Proxy endpoints] 를 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/10.png"></img></div>

### Step 3. AWS Lambda 함수 변경

이번 단계에서는 앞서 생성한 Lambda 함수가 구성한 RDS Proxy 를 활용해 RDS 에 접근하도록 수정합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
2. 이전에 생성한 **serverless-app-lambda** 를 선택하고 [Configuration] 탭의 [Permissions] 메뉴로 이동합니다. Lambda 함수에 설정한 IAM Role 이 보입니다. 클릭하여 IAM 페이지로 이동합니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/11.png"></img></div>

3. RDS Proxy 에 연결하기 위해 Secrets Manager API 를 활용할 것입니다. [Attach policies] 메뉴를 선택하고 `SecretsManagerReadWrite` 권한을 찾아 선택한 뒤 [Attach policy] 버튼을 클릭하여 추가합니다. 다음과 같이 새로운 정책이 추가 됩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/12.png"></img></div>

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/13.png"></img></div>

4. 권한 설정은 완료했습니다. 다시 Lambda 서비스의 **serverless-app-lambda** 로 이동한 뒤 코드를 아래와 같이 변경합니다.

```Python
import json
import pymysql
import boto3
import base64
from botocore.exceptions import ClientError

secret_name = "serverless-app-rds-secret"
region_name = "ap-northeast-2"

def lambda_handler(event, context):
    secret = get_secret()
    json_secret = json.loads(secret)

    db = pymysql.connect(
        host = 'YOUR RDS PROXY ENDPOINT', 
        user = json_secret['username'], 
        password = json_secret['password']
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


def get_secret():    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
```

> Module 2 보다 코드가 길어졌지만 실제로 AWS Secrets Manager 를 활용하는 것을 제외한다면 pymysql.connect() 의 host 주소만 RDS Proxy 로 변경된 것을 알 수 있습니다. 이처럼 RDS Proxy 는 애플리케이션의 변경을 최소화하는 방식으로 충분히 활용이 가능합니다.

5. 코드 상 15 라인의 pymysql.connect() 부분의 host 부분에 대한 변경이 필요합니다. 앞서 생성한 RDS Proxy 의 Proxy endpoints 중 [Tartget role] 이 **Read/write** 로 되어 있는 엔드포인트를 복사하여 Lambda 함수에 업데이트 합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/14.png"></img></div>

> Module 2 에서 구성할 때는 user, password 와 같은 DB 크리덴셜을 하드코딩 했습니다. 앞서 설명했 듯 이는 안전한 방법이 아니며 이번 실습과 같이 AWS Secrets Manager 에 이를 저장하고 API 등을 통해 이러한 정보를 가져와서 DB 에 연결하는 것이 안전합니다.

6. 변경을 완료 했다면 [Deploy] 버튼을 클릭해 배포를 완료합니다.

### Step 3. 테스트

이번 모듈을 마치기에 앞서 구성한 AWS Secrets Manager 와 Amazon RDS Proxy 가 제대로 동작하는지 테스트를 해보겠습니다. Lambda 콘솔에서 바로 Test 를 수행할 수 있지만 Module 2 에서 생성한 Amazon API Gateway 의 Invoke URL 을 활용해 테스트 하겠습니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon API Gateway 서비스로 이동합니다.
2. 앞서 생성한 **serverless-app-api** 를 선택하고 좌측의 [Stages] 메뉴로 이동한 뒤 **dev** 스테이지를 선택합니다.
3. 화면에 표시된 [Invoke URL] 를 복사하여 브라우저에서 연결하거나 터미널에서 호출해봅니다. Module 2 에서 수행하던 것과 유사한 결과값이 나오는 것을 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/15.png"></img></div>

```
$ curl YOUR API Gateway Invoke URL
{"statusCode": 200, "body": "\"2021-06-21T12:02:55\""}
```

서버리스 애플리케이션에서 RDS 를 보다 안전하고 효율적으로 활용하는 방법을 알아봤습니다. [Module 4. AWS Lambda 부하테스트]() 로 이동합니다.
