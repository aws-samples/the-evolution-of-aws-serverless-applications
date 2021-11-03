# Module 5. 서버리스 애플리케이션 추적 및 성능 모니터링
지금까지의 모듈들을 통해 서버리스 기반의 애플리케이션을 구축하였습니다. 만약 이런 분산 환경에서 성능에 문제가 발생한다면 어떻게 디버깅을 해야 할까요? 전통적인 디버깅 방식으로 Amazon API Gateway, AWS Lambda 함수 및 Amazon RDS로 구성된 분산 환경에을 분석하는 것은 쉽지 않습니다. [AWS X-Ray](https://aws.amazon.com//xray/)는 개발자가 분산 환경의 애플리케이션을 분석하고 디버깅하는데 필요한 정보를 수집하고 시각화하여 제공합니다. 이를 통해 개발자는 클라이언트의 요청이 Amazon API Gateway, AWS Lambda 를 거쳐 Amazon RDS 의 SQL 쿼리 수행까지의 단계별 추적 정보를 확인할 수 있고 맵 형태의 시각화 자료를 전체적인 성능 지표도 확인할 수 있습니다.

AWS X-Ray는 서비스 요청 혹은 수행중인 작업에 대한 데이터를 수집하여 세그먼트(segment)라는 논리적인 형태로 저장하며 호스트, 요청, 응답, 작업 시간 및 에러 등의 정보를 포합합니다. 단일 요청 혹은 작업이 내부적으로 AWS 서비스, 외부 API 혹은 데이터베이스를 경유하는 경우, 이러한 다운 스트림에 대한 하위 세그먼트(subsegment)를 통해 각 항목 별로 상세 정보를 확인할 수 있습니다. 그리고 이러한 하위 요청들은 추적(trace) 정보를 통해 보다 효과적으로 흐름을 도식화하고, 요청 상태 및 성능 정보를 확인할 수 있습니다. 

<div align="center"><img src="https://d1.awsstatic.com/Products/product-name/Images/product-page-diagram_AWS-X-Ray_how-it-works.2922edd4bfe011e997dbf32fdf8bd520bcbc85fb.png"></img></div> 

이번 모듈에서는 지금까지 구축된 Amazon API Gateway, AWS Lambda에 AWS X-Ray 활성화를 서버리스 애플리케이션 구성 요소들을 도식화하고, 세부 추적 정보를 확인해보도록 하겠습니다. 

### Step 1. Amazon API Gateway X-Ray 추적 활성화
Amazon API Gateway에 등록된 리소스에 대한 요청 경로는 추적 ID(trace ID)를 통해 이루어지며, HTTP GET 혹은 POST와 같은 단일 요청으로 파생된 모든 세그먼트들에 대한 정보를 수집합니다.
클라이언트에서 AWS X-Ray가 활성화된 요청에 대해서 자동 추적을 기능을 제공하지만, 현재 워크샵 환경과 같이 브라우저를 통해서 요청을 전송하는 시나리오에서는 API Gateway의 배포 스테이지 별로 AWS X-Ray 활성화가 필요합니다. 

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS API Gateway 서비스로 이동합니다.
2. 리스트에서 serverless-app-api를 선택하여 상세 페이지로 이동한 후, 좌측 패널의 [Stages]를 선택합니다.
3. [Stages] 리스트에서 dev 를 선택하고, 우측 [Stage Editor]에서 [Logs/Tracing] 탭을 선택합니다.
4. [X-Ray Tracing] 섹션 아래 [Enable X-Ray Tracing] 의 체크박스를 선택하고 [Save Changes]를 눌러 활성화 시킵니다.
5. 
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/0.png"></img></div>
6. AWS X-Ray의 추적을 확인하기 위해 상단 [Invoke URL]을 복사하여 브라우저에서 연결하거나 터미널에서 호출해봅니다. 

> AWS X-Ray는 모든 요청을 추적하는 것이 아니라 샘플링을 통해 요청에 대한 대표값을 제공하고 있습니다. 기본적으로 초당 1개 및 추가 샘플링 비율 (1%) 로 설정되어 있습니다. 이 기본 규칙은 커스텀하게도 변경할 수 있으며, 추가 정보는 [X-Ray 샘플링 규칙](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-console-sampling.html)을 참고하시기 바랍니다.
