# Module 2. REST API 기반 서버리스 애플리케이션

이번 워크샵부터는 AWS Lambda 를 중심으로 Amazon API Gateway 를 연동해 간단한 REST API 기반 서버리스 애플리케이션을 개발해보겠습니다. [AWS 의 서버리스 서비스](https://aws.amazon.com/serverless/getting-started)들을 사용하면 내장된 애플리케이션 가용성과 유연한 확장 기능을 활용해 비용 효율적인 애플리케이션을 구축하고 배포하는 것이 가능해집니다.

Module 2 에서는 아래 아키텍처와 같이 Amazon API Gateway 와 AWS Lambda 뿐만 아니라 Amazon RDS 를 연결하는 작업까지 진행됩니다. 이미 AWS 에는 워크로드 별로 참고할 수  [다양한 서버리스 애플리케이션의 아키텍처](https://aws.amazon.com/blogs/architecture/ten-things-serverless-architects-should-know/)가 존재하지만 그 중에서도 가장 기본이 되는 구조로 이해하시고 실습을 진행하면 됩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/module2_architecture.jpg"></img></div>

### Step 1. 서버리스 애플리케이션에서 사용할 Amazon VPC 생성

이번 실습에서 구성하는 리소스들을 위한 네트워크 환경을 먼저 구성합니다. 데이터베이스를 Amazon DynamoDB 와 같은 리전 서비스를 활용한다면 필요없는 단계겠지만 오늘 실습에는 Amazon RDS 를 활용하기 때문에 이를 위한 VPC 구성이 우선 되어야 합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon VPC 서비스로 이동합니다. 리전은 서울(ap-northeast-2)을 사용합니다.
2. 화면 좌측의 [Your VPCs] 로 이동한 뒤 상단의 [Create VPC] 버튼을 클릭하여 VPC 생성을 시작합니다.
3. [Name tag - optional] 에는 **serverless-app** 을 입력하고 [IPv4 CIDR block] 에는 **10.0.0.0/16** 을 입력한 뒤 [Create VPC] 버튼을 클릭하여 생성을 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/1.png"></img></div>

4. VPC 에 서브넷을 가용 영역별로 2개씩 총 4개를 생성합니다. 좌측의 [Subnets] 메뉴로 이동한 뒤 [Create subnet] 버튼을 선택합니다.
5. VPC ID 에는 앞서 생성한 **serverless-app** VPC 를 선택한 뒤 아래와 같이 4개의 서브넷을 생성합니다. 하나씩 입력한 뒤 아래 [Add new subnet] 버튼을 클릭하여 한번에 추가할 수 있습니다.

| Subnet name | Availability Zone | IPv4 CIDR block |
| --- | --- | --- |
| lambda-subnet-a | ap-northeast-2a | 10.0.1.0/24 |
| lambda-subnet-c | ap-northeast-2c | 10.0.2.0/24 |
| rds-subnet-a | ap-northeast-2a | 10.0.10.0/24 |
| rds-subnet-c | ap-northeast-2c | 10.0.20.0/24 |

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/2.png"></img></div>

6. 다음과 같이 4개의 서브넷을 생성했다면 다음으로 진행합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/3.png"></img></div>

7. RDS 와 Lambda 에서 각각 사용할 보안 그룹을 생성합니다. RDS 의 경우 이 후 생성할 Lambda 와 RDS Proxy 에서 접근이 허용되도록 구성할 것입니다.
8. 좌측의 [Security Groups] 메뉴로 이동한 뒤 [Create security group] 버튼을 클릭합니다.
9. 우선 Lambda 에서 사용할 보안 그룹을 생성합니다. [Security group name] 에는 **lambda-sg** 를 입력하고 [Description] 을 적은 뒤 [VPC] 는 앞서 생성한 **serverless-app** 을 선택합니다. Lambda 의 경우 별도의 인바운드 규칙이 필요하지 않습니다. 하단의 [Create security group] 버튼을 클릭하여 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/4.png"></img></div>

10. 이어서 RDS 에서 사용할 보안 그룹을 생성합니다. 앞서와 동일하게 보안 그룹 생성 메뉴로 이동한 뒤 [Security group name] 에는 **rds-sg** 를 입력하고 [Description] 을 적은 뒤 [VPC] 는 동일하게 **serverless-app** 을 선택합니다.
11. 하단의 Inbound rules 에서 [Add rule] 버튼을 클릭하여 인바운드 규칙을 추가합니다. [Type] 은 **MYSQL/Aurora** 를 선택하고 [Source] 에는 앞서 생성한 **lambda-sg** 를 선택합니다. 아래 [Create security group] 을 선택하여 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/5.png"></img></div>

### Step 2. Amazon RDS 생성

이번 실습은 많은 분들이 사용 중이고 가장 익숙한 RDBMS 를 기준으로 이를 서버리스 애플리케이션에서 활용하는 방법을 살펴봅니다. AWS 에는 사용할 수 있는 다양한 [데이터베이스 옵션](https://aws.amazon.com/products/databases/) 이 제공되고 있고 서버리스 데이터 베이스인 Amazon DynamoDB 를 활용하는 사례가 많이 있습니다. 하지만 최근에는 [Amazon Aurora Serverless](https://aws.amazon.com/rds/aurora/serverless/) 나 [Amazon RDS Proxy](https://aws.amazon.com/rds/proxy/) 등의 새로운 기능이 추가되어 조금 더 익숙한 데이터베이스를 서버리스 애플리케이션에서도 활용할 수 있게 되었습니다.

이번 단계에서는 이 후 실습에서 사용할 Amazon RDS for MySQL 을 생성하겠습니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon RDS 서비스로 이동합니다.
2. 좌측의 [Subnet groups] 메뉴로 이동한 뒤 [Create DB Subnet Group] 을 선택합니다.
3. [Name] 에는 **rds-subnet-group** 을 입력하고 [Description] 을 입력한 뒤 [VPC] 는 **serverless-app** 을 선택합니다.
4. 하단의 Add subnets 의 [Availability Zones] 에는 **ap-northeast-2a** 와 **ap-northeast-2c** 두가지를 선택합니다.
5. [Subnets] 에는 앞서 데이터베이스용으로 만든 서브넷 두 가지 **10.0.10.0/24** 와 **10.0.20.0/24** 를 선택하고 [Create] 를 클릭하여 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/6.png"></img></div>

6. RDS 생성을 시작합니다. 좌측의 [Databases] 옵션으로 이동한 뒤 [Create database] 를 선택합니다.
7. [Engine options] 에는 [MySQL] 을 선택합니다. [Version] 은 **MySQL 5.7.33** 을 선택합니다. Module 3 에서 사용할 RDS Proxy 는 2021년 5월을 기준으로 MySQL 5.6, 5.7 을 지원하고 있으며 RDS Proxy 의 보다 자세한 제한 사항은 [여기](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html#rds-proxy.limits)에서 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/7.png"></img></div>

8. 하단 Settings 에서 [DB instance identifier] 에는 **serverless-app-rds** 를 입력합니다. Credentials Settings 에서 [Master username] 은 기본 값인 **admin** 으로 두고 [Master password] 와 [Confirm password] 에는 **Passw0rd** 를 입력합니다. 혹은 다른 기억할 수 있는 비밀번호를 입력합니다.
9. [DB instance class] 는 **db.m5.large** 로 변경하고 아래 Storage 옵션에서 [Storage type] 은 **General Purpose (SSD)** 로 변경합니다. [Allocated storage] 는 **20 GiB** 를 입력하고 아래 [Enable storage autoscaling] 옵션은 비활성화 해줍니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/8.png"></img></div>

10. 워크샵 환경에서는 Multi-AZ 배포를 할 필요는 없기 때문에 Availability & durability 의 [Multi-AZ deployment] 옵션은 **Do not create a standby instance** 를 체크합니다. 프로덕션 환경에서는 standby instance 옵션을 사용하는 것이 좋습니다.
10. 아래 Connectivity 옵션에서 [Virtual private cloud (VPC)] 는 **serverless-app** 을 선택하고 [Subnet group] 은 **rds-subnet-group** 을 선택합니다.
11. [VPC security group] 은 **Choose existing** 을 선택하고 [Existing VPC security groups] 에 앞서 생성한 **rds-sg** 를 추가로 선택해줍니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/9.png"></img></div>

12. 다른 옵션은 기본값을 유지한채 [Create database] 를 선택하여 RDS 생성을 완료합니다.

### Step 3-1. AWS Lambda 구성

이번 단계부터 본격적으로 서버리스 애플리케이션의 핵심이 되는 AWS Lambda 함수를 구성합니다. 이렇게 구성하는 Lambda 함수는 RESTful 한 방식으로 동작하며 앞서 생성한 데이터베이스에 쿼리를 하게 됩니다. 이를 위해 [VPC 의 리소스에 액세스 하는 Lambda 함수](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html) 를 구성하는 작업 등을 수행합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
2. [Create function] 버튼을 클릭하여 함수 생성을 시작합니다.
3. [Function name] 에는 **serverless-app-lambda** 를 입력하고 [Runtime] 은 **Python 3.8** 을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/10.png"></img></div>

4. 하단의 [Advanced settings] 의 드롭다운 버튼을 클릭합니다.
5. Network 에서 [VPC - optional] 에는 **serverless-app** 을 선택하고 [Subnets] 는 **lambda-subnet-a** 와 **lambda-subnet-c** 를 선택합니다. [Security groups] 는 **lambda-sg** 를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/11.png"></img></div>

6. 위와 같이 구성했다면 [Create function] 버튼을 클릭하여 Lambda 함수를 생성을 완료합니다.
7. 생성한 Lambda 함수 화면으로 자동으로 이동합니다. 화면 중간의 [Code source] 에 해당 Lambda 함수에 포함된 코드를 확인할 수 있습니다. 좌측의 **lambda_function.py** 를 더블 클릭하여 선택합니다.
8. 기본으로 제공되는 코드를 삭제한 뒤 다음의 Python 코드를 붙여 넣습니다.

```Python
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
```

9. 코드 상 5:9 라인의 pymysql.connect() 부분의 host, user, password 부분에 대한 업데이트가 필요합니다. 우선 host 에 대한 정보는 앞서 생성한 RDS 에서 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/12.png"></img></div>

10. RDS Endpoint 정보를 확인하여 아래의 내용을 Lambda 함수에 업데이트 합니다.

| host | user | password |
| --- | --- | --- |
| Your RDS Endpoint | admin | Passw0rd |

> Module 2 에서는 가장 간편한 방법으로 Lambda 에서 RDS 에 연결하기 위해 DB 의 크리덴셜을 직접 코드에 입력하여 접속합니다. 하지만 이는 보안상 안전한 방법은 아닙니다. 실제 프로덕션 환경에는 [AWS Secrets Manager 등을 활용](https://aws.amazon.com/blogs/security/how-to-securely-provide-database-credentials-to-lambda-functions-by-using-aws-secrets-manager/)해 DB 크리덴셜 정보를 직접 코드에 입력하는 것이 더 안전합니다.

### Step 3-2. Lambda Layer 구성

앞서 Step 3-1 에서 작성한 Lambda 함수에는 pymysql 이라는 라이브러리가 포함되어 있습니다. 기본적으로 Lambda 에는 AWS SDK for Python (Boto3) 와 각각의 런타임 별 기본 라이브러리는 포함되어 있습니다. 그 외에 다른 라이브러리의 사용을 위해서는 [Lambda 배포 패키지](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html) 를 사용하여 Lambda 함수 코드를 배포해야 합니다.

여기에서 한단계 더 나아가 [Lambda Layer](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html) 를 수 있습니다. 이 기능을 활용하여 여러 Lambda 함수 간에 코드를 공유할 수 있고, .zip 배포 패키지 크기를 줄일 수 있으므로 Lambda 를 통한 운영에도 도움이 됩니다. Lambda 함수별로 최대 5개의 Lambda Layer 를 포함할 수 있으며, 보다 자세한 내용은 [다음](https://aws.amazon.com/blogs/compute/using-lambda-layers-to-simplify-your-development-process/) 에서 확인할 수 있습니다.

이번 실습에서는 pymysql 라이브러리를 Lambda Layer 로 구성한 뒤 이를 함수가 참조하는 구성을 합니다.

1. 우선 다음 [pypi.org](https://pypi.org/project/PyMySQL/#files) 에서 Python 3 용 tar.gz 압축 파일을 다운 받아 zip 으로 새로 압축하거나, 다음 [링크](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/src/pymysql.zip) 를 통해 pymysql 을 다운받습니다.
2. 왼쪽 메뉴 탭의 Additional resources 의 [Layers] 메뉴로 이동한 뒤 [Create layer] 버튼을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/13.png"></img></div>

3. [Name] 에는 **pymysql** 을 입력하고 [Upload a .zip file] 을 선택한 뒤 [Upload] 버튼을 클릭해 앞서 다운 받은 pymysql.zip 파일을 업로드 합니다. [Compatible runtimes] 에는 **Python 3.8** 을 선택합니다. 아래 스크린샷과 같이 구성 후 [Create] 버튼을 클릭하여 Lambda Layer 생성을 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/14.png"></img></div>

4. 앞서 생성한 **serverless-app-lambda** 함수로 이동한 뒤 하단 Layers 메뉴의 [Add a layer] 버튼을 클릭합니다.
5. Layer source 는 [Custom layers] 를 선택하고 드롭 다운 메뉴에서 **pymysql** 을 선택한 뒤 [Version] 은 **1** 을 선택합니다. 배포를 여러번 했다면 버전은 다르게 보일 수 있습니다. [Add] 버튼을 선택하여 Lambda 에 추가하는 작업을 완료해줍니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/15.png"></img></div>

6. 아래와 같이 Layers 메뉴에 pymysql 이 추가된 것을 확인할 수 있습니다. Lambda 함수 구성이 끝났습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/16.png"></img></div>

### Step 3-3. Lambda 테스트

1. 구성한 Lambda 의 테스를 해봅니다. Lambda 콘솔 중앙의 [Test] 메뉴로 이동합니다.
2. [Template] 는 **hello-world** 기본값을 사용하고 [Name] 에는 **apptest** 를 입력하고 [Save changes] 를 클릭한 뒤 우측의 [Test] 버튼을 클릭해 테스트를 수행합니다. 다음과 같은 테스트 결과가 표시됩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/17.png"></img></div>

> 만약 테스트가 실패하면 pymysql.connect 부분에서 ,, '' 등 syntax 에러가 없는지 확인이 필요합니다. 모든 문자는 ''로 감싸져야합니다. 또한 host, user 라인의 끝에는 , 가 있어야 합니다.

3. 작성한 Lambda 함수는 단순히 cursor.execute("select now()") 를 통해 현재 시간을 반환하는 동작을 합니다. 때문에 아래와 같이 "statusCode": 200 와 "body" 부분에 RDS 시간이 표시되면 Lambda 와 RDS가 정상적으로 통신하는 것을 확인할 수 있습니다.
```JSON
{
  "statusCode": 200,
  "body": "\"2021-05-13T06:06:26\""
}
```

> 한 가지 재밌는 점은 최초 테스트 때의 Duration 을 확인한 뒤 이 후에 다시 테스트를 수행하면 실행 시간이 최초 실행에 비해 줄어드는 것을 확인할 수 있습니다. 이는 Lambda 의 콜드스타트 때문입니다. 이 후 [Module 4. XXXX]() 에서는 부하테스트와 더불어 콜드스타트 시간을 최적화 하는 방법에 대해 다루고 있습니다. 다음 [블로그](https://aws.amazon.com/blogs/compute/new-for-aws-lambda-predictable-start-up-times-with-provisioned-concurrency/) 에 이에 관련된 내용 설명이 있습니다.

### Step 4. Amazon API Gateway 구성

AWS Lambda 는 [Module 1. 나의 첫 AWS Lambda](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/README.md) 에서와 같이 이벤트에 의한 방식으로 호출할 수도 있지만 REST API 작업 등을 위해 Amazon API Gateway 에서 호출하는 방식도 많이 사용되고 있습니다. 그 외에도 [Lambda 함수를 호출하는 다양한 방법](https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html)이 존재합니다.

[Amazon API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) 는 REST 및 WebSocketAPI 등을 생성, 배포, 유지 관리 할 수 있는 AWS 서비스로 모든 규모의 API 를 개발자가 손쉽게 구성할 수 있도록 해줍니다.

이번 실습에서는 Lambda 를 API Gateway 와 함께 사용하여 REST API 호출하는 것을 구성합니다. 실습 외에도 이 두 서비스를 연동하는 다양한 자습서가 제공되고 있습니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon API Gateway 서비스로 이동합니다.
2. 우측 상단의 [Create API] 를 클릭하고 [REST API] 옵션의 [Build] 버튼을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/18.png"></img></div>

3. API 생성 화면에서 Create new API 에는 [New API] 를 선택하고 하단 Settings 의 [API name] 에는 **serverless-app-api** 를 입력합니다. [Endpoint Type] 은 **Regional** 을 선택합니다. [API 트래픽의 오리진에 따라 Edge, Regional, Private 등의 옵션](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-endpoint-types.html) 을 제공하고 있습니다. [Create API] 를 클릭하여 API 를 생성합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/19.png"></img></div>

4. API 생성이 완료되면 [Resources] 메뉴 상단의 [Actions] 버튼을 드롭 다운 한 뒤 [Create Method] 옵션을 선택합니다. 생성된 빈 드롭 다운 메뉴에서는 [GET] 을 선택한 뒤 체크 버튼을 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/20.png"></img></div>

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/21.png"></img></div>

5. / - GET - Setup 화면이 나타납니다. [Ingegration type] 은 **Lambda Function** 을 선택하고 [Lambda Region] 은 **ap-northeast-2** 를 선택합니다. [Lambda Function] 에는 **serverless-app-lambda** 를 선택합니다. [Save] 를 선택하여 API 메소드 생성을 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/22.png"></img></div>

6. Add Permission to Lambda Function 팝업이 나타나면 [OK] 를 선택합니다.
7. 생성한 API 를 배포해줘야 합니다. [Resources] 메뉴 상단의 [Actions] 버튼을 드롭다운 한 뒤 [Deploy API] 를 클릭합니다.
8. [Deploy stage] 는 **[New Stage]** 를 선택하고 [Stage name*] 에는 **dev** 를 입력한 뒤 [Deploy] 버튼을 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/23.png"></img></div>

9. 각각의 배포 스테이지 별 다양한 설정이 가능하지만 오늘 실습에서 이 부분은 다루지 않겠습니다. 생성한 **dev** 스테이지 상단에 [Invoke URL] 이 표시된 것을 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/24.png"></img></div>

11. 주소를 복사하여 브라우저에서 연결하거나 혹은 터미널에서 호출해봅니다. Lambda 를 테스트했을 때와 동일한 결과값이 나오는 것을 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/25.png"></img></div>

```
$ curl YOUR API Gateway Invoke URL
{"statusCode": 200, "body": "\"2021-05-13T07:16:42\""}
```

12. Lambda 서비스로 이동하여 **serverless-app-lambda** 함수를 선택하면 다음과 같이 트리거에 API Gateway 가 추가된 것을 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/26.png"></img></div>

고생 하셨습니다. [Module 3. 서버리스 애플리케이션의 DB 사용 경험 개선](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/README.md) 으로 이동합니다.
