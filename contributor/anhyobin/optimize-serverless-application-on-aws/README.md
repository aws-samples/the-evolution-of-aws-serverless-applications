# AWS 서버리스 애플리케이션의 진화 : 대용량 트래픽도 서버리스로 처리할 수 있습니다!

서버리스는 오늘날 클라우드에서 가장 인기있는 디자인 패턴 중 하나입니다. 서버 및 운영 체제 운영의 부담은 덜고 서비스의 개발 및 구축을 통해 빠르게 혁신에 집중할 수 있기 때문입니다. 이러한 이유로 이미 많은 개발자들이 서버리스를 적극적으로 활용하고 있습니다. AWS 에서 운영 중인 서비스를 자동화 하는데 항상 빠지지 않고 등장하는 것이 바로 AWS Lambda 입니다. 이번 워크샵에서는 서비스 자동화나 단순한 이벤트 처리에 활용하던 AWS Lambda 를 중심으로 대용량 트래픽을 처리하는 서버리스 애플리케이션을 개발하고 운영하는 방법에 관해 배워보겠습니다.

워크샵은 총 5 개의 모듈로 구성되어 있으며, 각각의 모듈은 모두 독립적으로 수행할 수 있습니다. 서버리스가 생소한 분도 이번 워크샵의 모듈을 모두 수행해보면 아무리 많은 CCU(Concurrent User, 동시접속자), DAU(Daily Active User, 일간 순수 이용자) 가 기대되는 서비스도 서버리스로 처리할 수 있다는 자신감을 얻으실 수 있을 것입니다.

## 준비물

* 실습에 사용할 랩탑 혹은 데스크톱
* AWS 계정 혹은 AWS 행사에 참여 중이라면 EventEngine 계정

## 모듈

1. [나의 첫 AWS Lambda](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/README.md) : AWS Lambda 를 사용해본 적 없는 분들을 위한 기초 과정입니다. 이미 Lambda 에 익숙하다면 진행하지 않아도 괜찮습니다. 다음 아키텍처와 같이 Lambda 를 활용해 단순한 자동화 프로세스를 구축해봅니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/module1_architecture.jpg"></img></div> 

2. [본격 REST API 기반 서버리스 애플리케이션 개발](https://github.com/aws-samples/aws-games-sa-kr/tree/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/README.md) : 본격적으로 AWS Lambda 를 활용해 서버리스 애플리케이션을 만들어 봅니다. 가장 많이 활용되는 형태인 Amazon API Gateway 의 REST API 구축에 AWS Lambda 를 활용하는 방법을 알아봅니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2/img/module2_architecture.jpg"></img></div> 

3. [서버리스 애플리케이션의 DB 사용 경험 개선](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/README.md) : 앞서 Module 2 에서 개발한 REST API 기반 서버리스 애플리케이션의 DB 사용 경험을 개선합니다. Amazon RDS Proxy 를 통해 DB 커넥션을 효과적으로 관리하고 AWS Secrets Manager 를 통해 보안을 강화해봅니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module3/img/module3_architecture.jpg"></img></div> 

4. [서버리스 애플리케이션 코드 최적화 및 부하 테스트](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/README.md) : Moduel 2, 3 에서 개발한 서버리스 애플리케이션을 최적화하고 테스트합니다. 우선 AWS Lambda 의 코드 최적화를 통해 실행 시간을 단축하여 성능을 개선합니다. 또한 Locust 오픈 소스  부하 테스트 도구를 통해 부하를 줌으로써 Lambda 의 Scaling 동작을 확인하고, Provisioned Concurrency 설정으로 Cold Start 를 줄여 실행 시간을 최적화 해봅니다.
5. [서버리스 애플리케이션 추적 및 성능 모니터링](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/README.md) : 서버리스 애플리케이션에 AWS X-Ray를 연동하여 애플리케이션의 구성 요소를 시각화 하고 성능 및 오류 디버깅에 필요한 정보를 확인해봅니다. 클라이언트에서 보낸 요청이 Amazon API Gateway, AWS Lambda 그리고 SQL 쿼리문에서 소요된 레이턴시 정보 및 각 구간별 요청에 대한 상태 정보를 확인 해봅니다.
 
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/module5_architecture.png"></img></div> 


## 참고 자료

* [서버리스 웹 애플리케이션 워크샵](https://github.com/aws-samples/aws-serverless-workshops-kr/tree/master/WebApplication)
* [Best practices for working with AWS Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
