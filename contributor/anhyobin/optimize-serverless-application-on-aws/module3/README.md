# Module 3. 서버리스 애플리케이션의 DB 사용 경험 개선

이 모듈에서는 Module 2.에서 생성한 API Gateway, Lambda, RDS를 기반으로 AWS Secrets Manager와 RDS Proxy 설정을 추가하는 과정입니다. 이 모듈을 추가함으로서 Lambda 기반 API application 서비스의 장점은 AWS Secrets Manager를 통하여 RDS의 보안 정보를 쉽게 관리할 수 있고, RDS Proxy를 설정함으로서 Connection pooling로 보다 효율적인 connection 관리로 API 의 성능을 향상 시킬 수 있습니다.

Step 1. AWS Secrets Manager 새 보안 암호 저장, VPC endpoint 생성

1. 콘솔의 서비스 검색창에서 **Secrets Manger** 를 검색하고, AWS Secrets Manager 콘솔 창에서 **새 보안 암호 저장** 버튼을 클릭합니다.

2. **RDS 데이터베이스에 대한 자격 증명** 을 선택합니다. 그리고 사용자 이름, 암호는 Module 2. 에서 RDS를 생성했을때 입력하였던 사용자와 암호를 적습니다. 그리고 **이 보안 암호로 액세스할 RDS 데이터베이스 선택** 에서 `serverless-workshop-rds` 를 찾아 선택하고 **다음**을 클릭합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_sm.png"></img></div>

3. 그리고 보안 암호 이름 및 설명의 **보안 암호 이름** 은 `serverless-workshop-rds-secret`를 입력하고 **다음** 을 클릭합니다. 그리고 **3단계 교체구성, 4단계 검토** 는 그대로 다음을 클릭하여 생성을 마칩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_sm_2.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_sm_3.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/created_sm.png"></img></div>

4. AWS Secrets Manager를 **VPC 내부로 연결된 Lambda** 에 사용하기 위해서는 Secrets Manager의 VPC endpoint를 생성해야 합니다. 그리고 VPC endpoint를 생성할 Subnet을 생성해야 합니다. 따라서 먼저 **VPC 콘솔 화면** 에서 왼쪽 패널의 서브넷을 클릭하고, 아래의 사진과 같이 Subnet을 생성합니다. 본 실습에서는 서울리전에서 진행되고, 서울리전의 4개의 AZ(Availiablity Zone)에 모두 생성하였습니다. Subnet을 생성할때는 VPC에 할당된 CIDR 블록을 토대로 IP주소 범위를 설정해줍니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_sm_subnet.png"></img></div>

Subnet 생성에 대하여 궁금하시다면 [VPC 및 서브넷 관련 작업](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/working-with-vpcs.html#AddaSubnet) 을 참고할 수 있습니다.
또한 VPC와 Subnet 설정에 관련하여 좀 더 자세히 알고싶으시다면 [VPC 및 콘솔](https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/VPC_Subnets.html) 을 참고할 수 있습니다.

5. 다음으로는 VPC Endpoint에 적용할 Security Group을 생성합니다. **VPC 콘솔 화면** 에서 왼쪽 패널의 **보안 그룹** 을 클릭하고, 오른쪽 상단의 **보안 그룹 생성** 버튼을 클릭하여 생성 화면으로 진입합니다. 그리고 아래의 사진과 같이 **Lambda의 보안 그룹에 대하여 HTTPS 통신을 허용** 하도록 인바운드 설정을 합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_sm_sg.png"></img></div>

6. 다음으로는 VPC Endpoint를 생성합니다. **VPC 콘솔 화면** 에서 왼쪽 패널의 **엔드포인트** 를 클릭하고, **엔드포인트 생성** 버튼을 클릭하여 생성 화면으로 진입합니다. 생성 화면에서 서비스 범주는 **AWS 서비스** 그리고 서비스 이름은 `com.amazonaws.##region##.secretsmanager` 입니다. 아래의 사진과 같이 secret manager를 검색하여 선택하실 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_endpoint.png"></img></div>

7. VPC는 Lambda와 RDS를 구성한 VPC를 선택하고, Subnet은 아래의 사진과 같이 3.에서 생성한 Subnet을 선택하시면 됩니다. 보안 그룹은 4. 에서 생성한 보안 그룹을 선택하고, 나머지 설정은 그대로 놔두고 가장 하단의 **엔드포인트 생성** 파란색 버튼을 클릭하여 생성을 마칩니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_endpoint_2.png"></img></div>

Step 2. RDS Proxy 설정

1. RDS Proxy를 생성하기 위해서 AWS 콘솔의 서비스 검색창에서 RDS를 검색하여 RDS 콘솔 화면으로 진입합니다. 그리고 Module 2. 에서 생성한 `serverless-workshop-rds` 식별자의 RDS 화면으로 진입합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy_2.png"></img></div>

2. RDS의 화면의 가장 하단에 프록시 항목이 있습니다. 여기서 **프록시 생성** 버튼을 클릭하여 생성 화면으로 진입합니다. 프록시 식별자는 `serverless-workshop-rds-proxy` 를 입력하고 엔진 호환성은 MySQL을 선택합니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy_3.png"></img></div>

3. 대상 그룹 구성에서는 Module 2. 에서 생성한 `serverless-workshop-rds`을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy_4.png"></img></div>

4. 연결에서는 이미 생성한 Secrets Manager 암호인 `serverless-workshop-rds-secret` 을 선택하고 IAM 역할에서 **IAM 역할 생성**, 그리고 Subnet은 아래의 사진과 같이 Module 2.에서 생성한 DB 전용 Subnet을 선택해줍니다. VPC도 마찬가지로 RDS, Lambda를 생성한 VPC를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy_5.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/create_proxy_6.png"></img></div>

5. 나머지 설정은 그대로 두고 **생성** 버튼을 클릭하여 생성을 마칩니다. 생성에는 몇 분의 시간이 걸릴 수 있습니다. 다음과 같이 프록시 화면이 보이면, **Proxy Endpoint** 를 확인하실 수 있습니다. 이 **Proxy Endpoint** 를 메모해 두도록합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/created_proxy.png"></img></div>

Step 3. Lambda 코드 변경

1. 람다 콘솔 들어감 람다 코드를 교체함
2. 람다코드에서 수정해야할 부분 수정, 업데이트
3. api gateway주소를 다시 호출해봄 제대로 동작하면 완료