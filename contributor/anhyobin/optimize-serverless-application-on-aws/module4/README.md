# Module 4. 서버리스 애플리케이션 코드 최적화 및 부하 테스트
앞서 Module 2 와 Moduel 3 을 통해 REST API 기반 서버리스 애플리케이션을 개발하고 DB 사용 경험을 개선하는 내용을 살펴봤습니다. 이번 모듈부터는 개발과 운영 관점에서 AWS Lambda 최적화의 핵심인 동시성과 스케일링에 관한 실습을 진행하겠습니다.

함수가 호출되면 Lambda 는 함수의 인스턴스를 할당하여 이벤트를 처리하는데  [Lambda 함수의 동시성](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html)은 특정 시각에 요청을 처리하는 인스턴스의 수를 이야기 합니다. 흔히 초당 요청 수인 RPS (Requests per second) 와 혼동하는 경우가 많은데 Lambda 함수의 동시성은 RPS 와 Lambda 실행 시간의 곱으로 계산됩니다. 예를 들어 1초에 5번의 요청이 있고 Lambda 의 실행 시간이 200ms 이라면 5 RPS * 0.2 Sec = 1 동시성이 필요합니다. 이러한 동시성은 리전의 모든 함수가 공유하는 리전 [할당량](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) 이 적용되기 때문에 서버리스 애플리케이션을 운영함에 있어 주의 깊게 모니터링 해야합니다.

Lambda 는 동시 실행 한도보다 먼저 초기 트래픽 버스트의 경우 500 ~ 3000의 리전 별로 다른 버스트 동시성 할당량의 영향을 받으며, [Lambda 스케일링](https://docs.aws.amazon.com/lambda/latest/dg/invocation-scaling.html) 은 버스트 이후 매분 500개의 추가 인스턴스가 동시성 한도에 이를 때까지 확장하는 방식으로 이루어 집니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/features-scaling.png"></img></div>

Module 4 에서는 [AWS Lambda 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html) 중 일부를 적용하여 성능을 향상 시키는 방법을 알아보고 오픈 소스 부하 테스트 도구인 [Locust](https://locust.io/) 를 활용해 Lambda 스케일링에 관해 알아보겠습니다.

### Step 1. AWS Cloud9 에 부하 테스트 도구인 Locust 구성
서비스 런칭 전에 사용할 수 있는 부하 테스트 도구는 [JMeter](http://jmeter.apache.org/), [ApacheBench](https://httpd.apache.org/docs/2.4/programs/ab.html), [Vegeta](https://github.com/tsenart/vegeta) 등으로 굉장히 다양합니다. 또한 AWS 에서는 [Distributed Load Testing on AWS](https://aws.amazon.com/solutions/implementations/distributed-load-testing-on-aws/) 라는 솔루션을 제공하고 있으며 이를 통해 애플리케이션의 스케일과 안정성 등에 대해 테스트를 수행할 수 있습니다.

이번 단계에서는 오픈 소스 부하 테스트 도구인 [Locust](https://locust.io/) 를 AWS Cloud9 에 설치해 간단한 Python 코드로 손쉽게 부하 테스트를 수행해보겠습니다. 이를 통해 지금까지 구성한 서버리스 애플리케이션을 테스트하고 스케일링에 관해 알아봅니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Cloud9 서비스로 이동합니다.
2. 화면의 [Create environment] 버튼을 클릭합니다.
3. Name 은 `Locust` 를 입력하고 [Next step] 버튼을 클릭합니다.
4. Instance type 은 [Other instance type] 을 선택하고 아래에서 [c5.24xlarge] 를 선택합니다. 

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/1.png"></img></div>

> Event Engine 을 활용하는 AWS Event 가 아니라면 더 작은 인스턴스 타입을 선택해도 괜찮습니다. Locust 의 부하 발생 TPS 의 차이가 발생합니다.

5. 하단 [Network settings (advanced)] 메뉴를 확장한 뒤 Network (VPC) 는 [serverless-app-vpc] 를 선택하고 Subnet 은 [cloud9-subnet-a] 를 선택합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/2.png"></img></div>

6. 하단의 [Next step] 을 선택하고 [Create environment] 를 선택하여 Cloud9 생성을 완료합니다. 생성에는 시간이 소요되며 생성이 완료되면 바로 IDE 환경에 접속하게 됩니다.
7. 초기 화면의 Welcome 페이지를 닫고 + 버튼을 클릭한 뒤 [New Terminal] 옵션을 선택합니다. 혹은 하단의 터미널 창에서 수행해도 무방합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/3.png"></img></div>

8. 다음의 명령어를 통해 Locust 를 Cloud9 환경에 설치합니다.

```
$ pip3 install locust
```

9. 아래 명령어를 통해 설치를 확인합니다.

```
$ locust -V
```

10. 설치를 확인했다면 테스트를 수행합니다. 이를 위해 테스트를 위한 locustfile 을 작성합니다. 좌측 파일 탐색기의 Locust 폴더에서 우 클릭 후 [New File] 옵션을 선택하고 파일명은 ```locustfile.py``` 를 입력합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/4.png"></img></div>

11. 생성한 locustfile.py 를 열고 아래의 테스트 스크립트를 붙여넣은 뒤 상단 메뉴 [File] 의 [Save] 옵션을 선택하여 저장합니다.

```Python
import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):

    @task
    def hello_world(self):
        self.client.get("/")
```

> 오늘 구성한 환경에는 단순히 GET 을 통한 테스트만을 진행합니다. 실제 운영 환경에서는 [Writing a locustfile](https://docs.locust.io/en/stable/writing-a-locustfile.html) 을 참고하여 필요한 테스트 시나리오를 작성할 수 있습니다.

12. 터미널로 돌아와서 다음 명령어를 입력하여 실행합니다.

```
$ locust
```

13. 부하는 Locust 의 web interface 를 통해 손쉽게 할 수 있습니다. 브라우저의 새 탭을 열고 [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon EC2 서비스로 이동합니다.
14. aws-cloud9-Locust 라는 이름으로 실행 중인 인스턴스를 선택하고 하단 메뉴의 [Security] 탭을 선택합니다. 아래 Security groups 을 보면 22번 포트에 대해서만 Inbound 가 허용된 것을 확인할 수 있습니다. 보안 그룹을 선택하여 수정 페이지로 이동합니다.
15. Inbound rules 메뉴 하단에서 [Edit inbound rules] 메뉴를 선택하고 [Add rule] 버튼을 클릭합니다.
16. Type 은 [Custom TCP] 를 선택하고 Port range 에는 ```8089``` 를 입력합니다. Source 는 [Anywhere-IPv4] 를 선택한 뒤 [Save rules] 버튼을 클릭하여 완료합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/5.png"></img></div>

17. 좌측의 [Instaces] 메뉴로 다시 이동한 뒤 aws-cloud9-Locust 인스턴스의 Public IP 를 복사합니다.
18. 브라우저의 새 탭을 연 뒤 ```http://Cloud9 Instance Public IP:8089``` 를 입력하여 Locust web interface 에 접속합니다. 부하 테스트를 위한 Locust 구성을 완료했습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/6.png"></img></div>

### Step 2. 1차 부하 테스트

Lambda 함수를 최적화 하기 전 현재 구성한 환경에서 어떻게 스케일링이 이루어지고 요청의 스로틀이 발생하는지 살펴보겠습니다.

1. Locust web interface 화면의 3가지 옵션을 통해 부하를 발생시키게 됩니다.

- Number of users 는 동시에 실행하는 최대의 Locust user 입니다.
- Spawn rate 는 초당 생성하는 Locust user 입니다. 최대 Number of users 까지 스케일링이 이루어집니다.
- Host 는 부하를 발생할 호스트입니다. 오늘 실습에서는 API Gateway 의 Endpoint 가 해당됩니다.

2. [Number of users] 는 ```10000```, [Spawn rate] 에는 ```500```, [Host] 는 ```API Gateway Invoke URL``` 을 입력합니다.

> API Gateway Invoke URL 은 API Gateway 에서 생성한 API 의 Stages 메뉴에서 확인할 수 있습니다.
> Number of users 나 Spawn rate 값은 임의로 변경하여 테스트해도 괜찮습니다. 부하 발생 중 값 변경도 가능합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/7.png"></img></div>

3. 아래와 같이 입력했다면 [Start swarming] 버튼을 클릭하여 부하를 줍니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/8.png"></img></div>

4. 상단의 [Charts] 메뉴로 이동하면 RPS 등 부하 상황을 그래프로 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/9.png"></img></div>

5. 실제 Lambda 의 호출과 스케일링을 확인해보겠습니다. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
6. 앞서 구성한 serverless-app-lambda 를 선택한 뒤 [Monitor] 탭으로 이동하면 Lambda 에서 제공하는 메트릭을 확인할 수 있습니다. 그래프를 살펴보면 최초 Burst Limit 에 도달한 뒤 1분당 500 씩 Concurrent executions 이 증가하는 것을 확인할 수 있습니다. 그에 따라 최초 스케일링 전 스로틀이 발생했다가 Lambda 가 스케일링 되면서 해소되는 것을 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/10.png"></img></div>

> AWS 에서 제공하는 기본 Concurrent executions 제한이 1000이기 때문에 스케일링에 대한 부분 확인이 어려울 수 있습니다. 

7. 이 후 테스트를 위해 Locust web interface 로 이동한 뒤 상단의 STOP 버튼을 클릭하여 부하 테스트를 중지합니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/11.png"></img></div>

### Step 3. Lambda 코드 최적화

앞 서 Step 2 에서 경험한 것과 같이 발생하는 Lambda 의 스로틀링을 회피하는 방법은 크게 두 가지가 있습니다. 첫 번째는 [Lambda provisioned concurrency](https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html) 를 통해 지정한 갯수 만큼의 실행 환경을 구성해두는 것입니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4/img/features-scaling-provisioned.png"></img></div>

두 번째는 Module 4 가장 앞에서 설명한 것과 같이 동시성의 최소화를 위해 Lambda 함수의 실행 시간을 최적화 하는 것입니다. 이것은 [Lambda 의 모범 사례](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html) 중 하나로 실행 시간은 비용과도 밀접한 연관이 있기 때문에 Lambda 를 활용하신다면 필수로 적용해야 합니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
2. serverless-app-lambda 함수를 선택하여 코드를 살펴보겠습니다. 앞서 Module 1 에서 모든 Lambda 함수에는 언어와 관계 없이 [Handler](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html) 가 포함 되어 있고 이는 함수의 호출 마다 실행된다고 설명드렸습니다.
3. 저희가 사용 중인 Lambda 함수는 29라인의 ```Python def lambda_handler(event, context)``` 내에서 get_secret() 을 통해 DB 크리덴셜 정보를 읽고 DB 와 연결을 맺는 구조로 되어 있습니다. 이럴 경우

```Python
def lambda_handler(event, context):
    get_secret()
    pymysql.connect()
    
    execute("select now()")
```


15. 1차 부하 테스트
16. AWS Lambda 코드 최적화
17. 2차 부하 테스트 및 결과 
