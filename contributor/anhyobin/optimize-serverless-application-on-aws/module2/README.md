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

|Subnet name|Availability Zone|IPv4 CIDR block|
|------|---|---|
|lambda-subnet-a|ap-northeast-2a|10.0.1.0/24|
|lambda-subnet-c|ap-northeast-2c|10.0.2.0/24|
|rds-subnet-a|ap-northeast-2a|10.0.10.0/24|
|rds-subnet-c|ap-northeast-2c|10.0.20.0/24|

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

### Step 3. AWS Lambda 구성

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



///

1. 먼저 Lambda, RDS를 위한 Subnet을 생성해야 합니다. Lambda는 기본적으로 Subnet을 요구하지 않습니다. 하지만 일반적으로 RDS는 private Subnet으로 구성하여 외부와 통신이 되지 않도록 구성합니다. 따라서 Lambda와 RDS간의 통신이 되기 위해서는 추가적인 설정이 필요합니다. 본 실습에서는 Lambda에 VPC 네트워크 액세스를 설정하여 진행합니다.

RDS를 위한 Subnet, Lambda를 위한 Subnet 각각 2세트를 생성합니다.
**Subnet은 하나의 VPC에서 설정이 되어야합니다.**
**Multi-AZs 설정이 용이하도록 최소 2개이상의 AZ에 해당하는 Subnet을 생성해줍니다.**
본 실습에서는 Seoul Region의 4개의 AZ에 각각 생성을 해서 진행합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_subnet.png"></img></div>

Subnet을 생성할때는 VPC에 할당된 CIDR 블록을 토대로 IP주소 범위를 설정해줍니다.
Subnet 생성에 대하여 궁금하시다면 [VPC 및 서브넷 관련 작업](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/working-with-vpcs.html#AddaSubnet) 을 참고할 수 있습니다.
또한 VPC와 Subnet 설정에 관련하여 좀 더 자세히 알고싶으시다면 [VPC 및 콘솔](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/VPC_Subnets.html) 을 참고할 수 있습니다.

2. Security Group도 마찬가지로 Lambda, RDS용도로 각각 2개를 생성해 줍니다.
RDS는 Lambda의 Subnet에서만 통신이 될 수 있도록 설정해줍니다. 인바운드 규칙은 DB전용 Security Group은 Lambda Security Group와 Database Security Group의 3306 포트를 허용하고, Lambda 전용 Security Group은 인바운드 규칙에 아무것도 추가하실 필요가 없습니다. DB, Lambda Security Group 모두 아웃바운드 규칙은 Default 상태로 놔둡니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_sg.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/db_sg.png"></img></div>

보안 그룹에 대하여 더 자세히 알고시면 [VPC의 보안그룹](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/VPC_SecurityGroups.html) 을 참고하실 수 있습니다.

### Step 2. Amazon RDS 생성

1. 먼저 콘솔에서 RDS 항목을 검색하여 RDS 화면으로 진입하고, 왼쪽 탭의 **서브넷 그룹**을 클릭하여 아래 사진과 같이 RDS에 적용할 전용 Subnet group을 구성해줍니다. RDS를 생성할 Subnet을 선택하여 그룹을 생성하는 작업입니다. 본 실습에서는 서울리전에서 사용할 수 있는 총 4개의 가용영역 ap-northeast-2a, ap-northeast-2b, ap-northeast-2c, ap-northeast-2d 에 모두 서브넷을 생성하였고 그룹으로 설정하였습니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_subnet_group.png"></img></div>

2. 그리고 **데이터베이스 생성** 버튼을 클릭하여 생성 화면으로 넘어갑니다. 본 실습에서는 MySQL을 생성합니다. 하지만 이는 필수는 아닙니다. 익숙한 DB를 선택하여 구성하실 수 있습니다.

3. 엔진 옵션에서 MySQL을 선택하고 버전은 **5.6, 5.7** 버전을 선택하도록 합니다. **현재기준(2021.5) RDS Proxy는 **MySQL 5.6, 5.7 버전**을 지원하고 있습니다. [여기](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/rds-proxy.html)에서 **RDS Proxy 제한사항** 항목에서 자세한 내용을 확인하실 수 있습니다. 

4. 템플릿 부분는 **개발/테스트**를 선택합니다. 하지만 필요에 따라 프로덕션, 혹은 프리 티어를 선택하셔도 됩니다. **개발/테스트**를 선택하시면 **다중 AZ 배포** 기능이 비활성화 됩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_rds.png"></img></div>

5. 다음으로 설정에서는 DB 인스턴스 식별자에서는 `serverless-workshop-rds`를 적습니다. 자격 증명 설정에서는 마스터 사용자 이름은 **admin** , 마스터 암호는 **your password** 를 적습니다.

6. DB 인스턴스 크기는 적당한 타입을 선택하도록 합니다. 여기서는 m5.large를 선택합니다. (프리티어나 T클래스 인스턴스를 선택하셔도 실습을 진행하실 수 있습니다)

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_rds_2.png"></img></div>

7. 스토리지는 여기서는 최소 값인 20 GIB, 그리고 범용(SSD)를 선택합니다. 또한 자동조정 활성화는 끄도록 하겠습니다.

8. 가용성 및 내구성에서는 **대기 인스턴스를 생성하지 마십시오.**를 선택합니다. **개발/테스트** 템플릿을 선택하셨다면 Default로 생성하지 않습니다. 만약 production 환경을 목적으로 생성하신다면 꼭 Multi-AZs 배포를 선택하여 가용성을 확보하도록 합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_rds_3.png"></img></div>

9.  연결 부분에서는 Step 1.에서 Subnet을 생성한 VPC를 선택하고, 1.에서 생성한 서브넷 그룹을 추가해줍니다. 나머지 부분은 그대로 두고 다음을 진행합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_rds_4.png"></img></div>

10. 아래의 나머지 부분은 본 실습에서는 그대로 두고 진행을 합니다. 추가적인 설정 정보는 [DB 인스턴스 생성](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/USER_CreateDBInstance.html) 에서 확인 하실 수 있습니다.

11. 생성이 완료되면 다음과 같이 생성된 인스턴스를 확인하실 수 있고, RDS의 endpoint를 보실 수 있습니다. 이 endpoint는 Lambda 설정에 필요한 정보이니 메모를 해둡니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/rds_endpoint.png"></img></div>

### Step 3. AWS Lambda 생성

1. 먼저 콘솔 상단의 서비스 검색창에서 Lambda를 검색하여 Lambda 서비스 화면으로 진입합니다. 그리고 왼쪽 탭의 **함수**를 클릭하고, **함수 생성** 버튼을 클릭합니다.

2. 함수 생성 화면에서 함수 이름에 `serverless-workshop-lambda`, 런타임은 Python 3.8을 선택합니다. 나머지 기본 정보 설정은 그대로 둡니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_lambda.png"></img></div>

3. 고급 설정탭을 클릭하고, VPC를 선택합니다. VPC는 Step 1.에서 Subnet을 생성한 VPC를 선택하고, 서브넷, 보안 그룹도 마찬가지로 Step 1.에서 생성한 Lambda를 위한 서브넷, 보안 그룹을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_lambda_2.png"></img></div>

4. Lambda 생성이 완료되면, 함수 탭의 함수 리스트에서 생성한 Lambda를 확인하실 수 있습니다. 생성한 Lambda를 클릭하여 세부 설정으로 진입합니다.

5. 코드 탭에서 Default로 코드가 작성되어있는 것을 확인하실 수 있습니다. 이 것을 [Lambda Module 2 샘플코드](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/src/module2_lambda.py)의 코드를 복사하여 대체하도록 합니다.

6. 코드의 5:9줄에서 pymysql.connect() 코드를 확인하실 수 있고 host, user, password를 입력해야 합니다. host는 생성하신 RDS의 endpoint, user와 password는 Step 2.에서 설정한 마스터 유저와 암호 값을 입력합니다. 입력이 완료되면 **Deploy** 버튼을 클릭하여 배포를 마칩니다. 여기에서는 비밀번호를 입력하는 방법으로 실습이 진행됩니다. 비밀번호를 노출하지 않고 IAM 인증으로 비밀번호 대신 토큰으로 접근하는 방법도 있습니다. 보다 자세한 내용은 [Lambda configuration-database](https://docs.aws.amazon.com/lambda/latest/dg/configuration-database.html)에서 확인하실 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_code.png"></img></div>

7. 이 상태만으로는 Lambda를 실행할 수 없습니다. RDS를 접근하기 위해서 pymysql 모듈이 설치가 되어야 합니다. pymysql 모듈을 사용할 수 있도록 본 실습에서는 **Lambda 계층**을 사용하여 설정합니다. **Lambda 계층**에 대하여 자세히 알기 위해서는 [Lambda 계층](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/configuration-layers.html)에서 확인하실 수 있습니다. 

8. 왼쪽의 탭에서 **추가 리소스의 계층** 항목을 클릭합니다. 그리고 오른쪽 상단의 **계층 생성**을 클릭합니다. 이름에는 **pymysql**을 입력하고 pymysql을 업로드 해야합니다. [pymysql](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/src/pymysql.zip)를 다운 받거나, [pypi.org](https://pypi.org/project/PyMySQL/#files)에서 tar.gz으로 압축된 파일을 zip으로 새로 압축하여 업로드 하셔도 됩니다. 그리고 생성 버튼을 클릭하여 마칩니다. **이 실습은 python 3.8로 작성된 Lambda 함수의 코드로 진행됩니다. pymysql을 pypi에서 다운로드 받을때 꼭 함수에서 사용되고 있는 python버전과 호환이 가능한지 확인이 필요합니다**

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_layer.png"></img></div>

9.  다시 함수 세부 설정 화면으로 들어가서 **함수 개요의 Layers**를 클릭합니다. 그리고 **[Add a Layer]** 를 클릭한 후 사용자 지정 계층을 클릭하고 8. 에서 생성한 pymysql을 선택하고 추가를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/add_lambda_layer.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/add_lambda_layer_2.png"></img></div>

10. 이로서 Lambda 생성을 마치고 테스트를 해봅니다. Lambda의 코드 탭에서 **Test** 버튼을 클릭합니다. 테스트를 클릭하면 다음과 같이 테스트 이벤트 구성화면이 보입니다. 여기서 이벤트 이름에 `workshoptest`를 입력하고 생성을 마칩니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_test_event.png"></img></div>

11. 화면 아래와 같이 테스트 버튼을 클릭하고, 테스트 결과에 아래와 같이 statusCode : 200, 그리고 body에 RDS의 시간이 나오면 정상적으로 RDS와 Lambda가 통신이 가능한 것을 확인하실 수 있습니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_code_test.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_code_test_result.png"></img></div>

**만약 테스트가 실패하면, 혹시 pymysql.connect 부분에서 `,`, `''` 등 syntax 에러가 없는지 확인이 필요합니다. 모든 문자는 `''`로 감싸져야합니다. 또한 host, user 라인의 끝에는 `,`가 있어야 합니다.**

### Step 4. Amazon API Gateway 생성

Lambda를 REST API로 호출하기 위해 [Amazon API Gateway](https://aws.amazon.com/ko/api-gateway/)를 연결하는 방법은 매우 쉽고 간단하며 관리하기가 쉽습니다. 본 Step에서는 Amazon API Gateway를 생성하여 Lambda와 연동하여 REST API를 호출해봅니다.

1. 먼저 콘솔 상단의 서비스 검색창에서 **API gateway**를 검색하여 서비스 화면으로 진입합니다. 그리고 오른쪽 상단의 **API 생성**을 클릭하여 생성 화면으로 진입합니다. 

2. API 유형 선택에서 **REST API의 구축** 버튼을 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway.png"></img></div>

3. 새 API 생성화면에서 API 이름에 `serverless-workshop-api`을 입력하고 **API 생성**버튼을 클릭하여 생성을 마칩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_2.png"></img></div>

4. 생성이 완료된 API의 리소스항목에서 왼쪽 두번째 탭의 **작업** 드롭다운 버튼을 클릭하여 **메서드 생성** 버튼을 클릭합니다. 클릭한 후 리소스탭에서 생성된 빈 드롭다운 버튼을 클릭하여 **GET**을 선택하고 오른쪽의 체크버튼을 클릭합니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_3.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_4.png"></img></div>

5. 4.의 과정을 거치면 -GET- 설정 화면이 보입니다. 여기서 통합 유형에 Lambda 함수를 클릭하고, lambda의 리전, 그리고 Lambda 함수를 설정해야 합니다. Lambda 함수의 text 창을 클릭하면 선택가능한 Lambda가 보입니다. **serverless-workshop-lambda**를 선택하고 생성을 마칩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_5.png"></img></div>

6. 그리고 다시 **리소스탭에서 작업** 드롭다운 버튼을 클릭하여 **API 배포**를 클릭합니다. API 배포 창에서 배포 스테이지는 ** [새 스테이지] **를 선택하고 스테이지 이름은 `test-api`를 입력하고 **배포**를 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_6.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_7.png"></img></div>

7. Amazon API Gateway 설정이 끝났습니다. **test-api 스테이지 편집기** 화면의 상단에 **URL 호출**에서 호출가능한 URL이 생성된 것을 확인하실 수 있습니다. 이 URL을 브라우저 혹은 터미널에서 호출하여 {"statusCode": 200, "body": "your RDS time"}이 제대로 나오는 것을 확인합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/create_api_gateway_8.png"></img></div>

8. 또한 Lambda 화면에서도 다음과 같이 API Gateway가 트리거에 추가된 것을 확인하실 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/lambda_trigger.png"></img></div>



실습에서 Mysql 5.7 인스턴스로 변경하고 Proxy 생성부터 다시 진행
Module 2도 제대로 되었는지 확인
