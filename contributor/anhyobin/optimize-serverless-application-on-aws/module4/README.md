# Module 4. 서버리스 애플리케이션 코드 최적화 및 부하 테스트
앞서 Module 2 와 Moduel 3 을 통해 REST API 기반 서버리스 애플리케이션을 개발하고 DB 사용 경험을 개선하는 내용을 살펴봤습니다. 이번 모듈부터는 개발과 운영 관점에서 AWS Lambda 최적화의 핵심인 동시성과 스케일링에 관한 실습을 진행하겠습니다.

함수가 호출되면 Lambda 는 함수의 인스턴스를 할당하여 이벤트를 처리하는데  [Lambda 함수의 동시성](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)은 특정 시각에 요청을 처리하는 인스턴스의 수를 이야기 합니다. 흔히 초당 요청 수인 RPS (Requests per second) 와 혼동하는 경우가 많은데 Lambda 함수의 동시성은 RPS 와 Lambda 실행 시간의 곱으로 계산됩니다. 예를 들어 1초에 5번의 요청이 있고 Lambda 의 실행 시간이 200ms 이라면 5 RPS * 0.2 Sec = 1 동시성이 필요합니다. 이러한 동시성은 리전의 모든 함수가 공유하는 리전 [할당량](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) 이 적용되기 때문에 서버리스 애플리케이션을 운영함에 있어 주의 깊게 모니터링 해야합니다.

Lambda 는 동시 실행 한도보다 먼저 초기 트래픽 버스트의 경우 500 ~ 3000의 리전 별로 다른 버스트 동시성 할당량의 영향을 받으며, [Lambda 스케일링](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html) 은 버스트 이후 매분 500개의 추가 인스턴스가 동시성 한도에 이를 때까지 확장하는 방식으로 이루어 집니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/features-scaling.png"></img></div>

Module 4 에서는 [AWS Lambda 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html) 중 일부를 적용하여 성능을 향상 시키는 방법을 알아보고 오픈 소스 부하테스트 도구인 [Locust](https://locust.io/) 를 활용해 Lambda 스케일링에 관해 알아보겠습니다.

1. AWS Cloud9 에 Locust 구성
2. 1차 부하 테스트
3. AWS Lambda 코드 최적화
4. 2차 부하 테스트 및 결과 
