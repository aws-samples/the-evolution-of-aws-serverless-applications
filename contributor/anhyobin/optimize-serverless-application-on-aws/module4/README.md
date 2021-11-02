# Module 4. 서버리스 애플리케이션 코드 최적화 및 부하 테스트
앞서 Module 2 와 Moduel 3 을 통해 REST API 기반 서버리스 애플리케이션을 개발하고 DB 사용 경험을 개선하는 내용을 살펴봤습니다. 이번 모듈부터는 개발과 운영 관점에서 AWS Lambda 최적화의 핵심인 동시성과 스케일링에 관한 실습을 진행하겠습니다.

함수가 호출되면 Lambda 는 함수의 인스턴스를 할당하여 이벤트를 처리하는데  [Lambda 함수의 동시성](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)은 특정 시각에 요청을 처리하는 인스턴스의 수를 이야기 합니다. 흔히 초당 요청 수인 RPS (Requests per second) 와 혼동하는 경우가 많은데 Lambda 함수의 동시성은 RPS 와 Lambda 실행 시간의 곱으로 계산됩니다. 예를 들어 1초에 5번의 요청이 있고 Lambda 의 실행 시간이 200ms 이라면 5 RPS * 0.2 Sec = 1 동시성이 필요합니다. 이러한 동시성은 리전의 모든 함수가 공유하는 리전 [할당량](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) 이 적용되기 때문에 서버리스 애플리케이션을 운영함에 있어 주의 깊게 모니터링 해야합니다.

Lambda 는 동시 실행 한도보다 먼저 초기 트래픽 버스트의 경우 500 ~ 3000의 리전 별로 다른 버스트 동시성 할당량의 영향을 받으며, [Lambda 스케일링](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html) 은 버스트 이후 매분 500개의 추가 인스턴스가 동시성 한도에 이를 때까지 확장하는 방식으로 이루어 집니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/features-scaling.png"></img></div>

Module 4 에서는 [AWS Lambda 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html) 중 일부를 적용하여 성능을 향상 시키는 방법을 알아보고 오픈 소스 부하테스트 도구인 [Locust](https://locust.io/) 를 활용해 Lambda 스케일링에 관해 알아보겠습니다.

### Step 1. AWS Cloud9 에 부하테스트 도구인 Locust 구성
서비스 런칭 전에 사용할 수 있는 부하테스트 도구는 [JMeter](http://jmeter.apache.org/), [ApacheBench](https://httpd.apache.org/docs/2.4/programs/ab.html), [Vegeta](https://github.com/tsenart/vegeta) 등으로 굉장히 다양합니다. 또한 AWS 에서는 [Distributed Load Testing on AWS](https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/) 라는 솔루션을 제공하고 있으며 이를 통해 애플리케이션의 스케일과 안정성 등에 대해 테스트를 수행할 수 있습니다.

이번 단계에서는 오픈 소스 부하테스트 도구인 [Locust](https://locust.io/) 를 AWS Cloud9 에 설치해 간단한 Python 코드로 손쉽게 부하테스트를 수행해보겠습니다. 이를 통해 지금까지 구성한 서버리스 애플리케이션을 테스트하고 스케일링에 관해 알아봅니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Cloud9 서비스로 이동합니다.
2. 화면의 [Create environment] 버튼을 클릭합니다.
3. Name 은 `Locust` 를 입력하고 [Next step] 버튼을 클릭합니다.
4. Instance type 은 [Other instance type] 을 선택하고 아래에서 [c5.24xlarge] 를 선택합니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/1.png"></img></div>

> Event Engine 을 활용하는 AWS Event 가 아니라면 더 작은 인스턴스 타입을 선택해도 괜찮습니다. Locust 의 부하 발생 TPS 의 차이가 발생합니다.

5. 하단 [Network settings (advanced)] 메뉴를 확장한 뒤 Network (VPC) 는 [serverless-app-vpc] 를 선택하고 Subnet 은 [cloud9-subnet-a] 를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/2.png"></img></div>

6. 하단의 [Next step] 을 선택하고 [Create environment] 를 선택하여 Cloud9 생성을 완료합니다. 생성에는 시간이 소요되며 생성이 완료되면 바로 IDE 환경에 접속하게 됩니다.
7. 초기 화면의 Welcome 페이지를 닫고 + 버튼을 클릭한 뒤 [New Terminal] 옵션을 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/3.png"></img></div>

8. 다음의 명령어를 통해 Locust 를 Cloud9 환경에 설치합니다.

```
$ pip3 install locust
```

9. 아래 명령어를 통해 버전을 확인합니다.

```
$ locust -V
```

10. 설치를 확인했다면 테스트를 수행합니다. 이를 위해 테스트를 위한 locustfile 을 작성합니다. 좌측 파일 탐색기의 Locust 폴더에서 우 클릭 후 [New File] 옵션을 선택하고 파일명은 ```locustfile.py``` 를 입력합니다.
11. 생성한 locustfile.py 를 열고 아래의 테스트 스크립트를 붙여넣습니다.

```Python
import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):

    @task
    def hello_world(self):
        self.client.get("/")
```

> 오늘 구성한 환경에는 단순히 GET 을 통한 테스트만을 진행합니다. 실제 운영 환경에서는 [Writing a locustfile](https://docs.locust.io/en/stable/writing-a-locustfile.html) 을 참고하여 필요한 테스트 시나리오를 작성할 수 있습니다.

2. 1차 부하 테스트
3. AWS Lambda 코드 최적화
4. 2차 부하 테스트 및 결과 
