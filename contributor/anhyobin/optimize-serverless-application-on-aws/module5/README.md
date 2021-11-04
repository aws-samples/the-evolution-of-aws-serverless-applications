# Module 5. 서버리스 애플리케이션 추적 및 성능 모니터링
지금까지의 모듈들을 통해 서버리스 기반의 애플리케이션을 구축하였습니다. 만약 이런 분산 환경에서 성능에 문제가 발생한다면 어떻게 디버깅을 해야 할까요?
전통적인 디버깅 방식으로 Amazon API Gateway, AWS Lambda 함수 및 Amazon RDS로 구성된 분산 환경에을 분석하는 것은 쉽지 않습니다. [AWS X-Ray](https://aws.amazon.com//xray/)는 개발자가 분산 환경의 애플리케이션을 분석하고 디버깅하는데 필요한 정보를 수집하고 시각화하여 제공합니다. 이를 통해 개발자는 클라이언트의 요청이 API Gateway, Lambda 를 거쳐 RDS 의 SQL 쿼리 수행까지의 단계별 추적 정보를 확인할 수 있고 맵 형태의 시각화 자료를 전체적인 성능 지표도 확인할 수 있습니다.

<div align="center"><img src="https://d1.awsstatic.com/Products/product-name/Images/product-page-diagram_AWS-X-Ray_how-it-works.2922edd4bfe011e997dbf32fdf8bd520bcbc85fb.png"></img></div> 

AWS X-Ray는 서비스 요청 혹은 수행중인 작업에 대한 데이터를 수집하여 세그먼트(segment)라는 논리적인 형태로 저장하며 호스트, 요청, 응답, 작업 시간 및 에러 등의 정보를 포합합니다. 단일 요청 혹은 작업이 내부적으로 AWS 서비스, 외부 API 혹은 데이터베이스를 경유하는 경우, 이러한 다운 스트림에 대한 하위 세그먼트(subsegment)를 통해 각 항목 별로 상세 정보를 확인할 수 있습니다. 그리고 이러한 하위 요청들은 추적(trace) 정보를 통해 보다 효과적으로 흐름을 도식화하고, 요청 상태 및 성능 정보를 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/module5_architecture.png"></img></div> 

이번 모듈에서는 지금까지 구축된 API Gateway, Lambda 를 활용한 서버리스 애플리케이션에 AWS X-Ray 활성화를 서버리스 애플리케이션 구성 요소들을 도식화하고, 세부 추적 정보를 확인해보도록 하겠습니다. 

### Step 1. Amazon API Gateway X-Ray 추적 활성화
Amazon API Gateway에 등록된 리소스에 대한 요청 경로는 추적 ID(trace ID)를 통해 이루어지며, HTTP GET 혹은 POST와 같은 단일 요청으로 파생된 모든 세그먼트들에 대한 정보를 수집합니다.
클라이언트에서 AWS X-Ray가 활성화된 요청에 대해서 자동 추적을 기능을 제공하지만, 현재 워크샵 환경과 같이 브라우저를 통해서 요청을 전송하는 시나리오에서는 API Gateway 의 배포 스테이지 별로 X-Ray 활성화가 필요합니다. 

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS API Gateway 서비스로 이동합니다.
2. 리스트에서 serverless-app-api를 선택하여 상세 페이지로 이동한 후, 좌측 패널의 [Stages]를 선택합니다.
3. [Stages] 리스트에서 `dev` 를 선택하고, 우측 [Stage Editor]에서 [Logs/Tracing] 탭을 선택합니다.
4. [X-Ray Tracing] 섹션 아래 [Enable X-Ray Tracing] 의 체크박스를 선택하고 [Save Changes]를 눌러 활성화 시킵니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/0.png"></img></div>

5. AWS X-Ray의 추적을 확인하기 위해 상단 [Invoke URL]을 복사하여 브라우저에서 연결하거나 터미널에서 호출해봅니다. 

> AWS X-Ray는 모든 요청을 추적하는 것이 아니라 샘플링을 통해 요청에 대한 대표값을 제공하고 있습니다. 기본적으로 AWS X-Ray SDK는 매초 최초 요청과 추가 요청의 5% 를 기록합니다. 
이 기본 규칙은 커스텀하게도 변경할 수 있으며, 추가 정보는 [X-Ray 샘플링 규칙](https://docs.aws.amazon.com/ko_kr/xray/latest/devguide/xray-console-sampling.html)을 참고하시기 바랍니다.


### Step 2. Amazon API Gateway의 AWS X-Ray 추적 활성화
Step 1. 에서 활성화 하였던 AWS X-Ray 에 수집된 추적 정보 및 시각화된 서비스 맵(service map)을 확인해보겠습니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS X-Ray 서비스로 이동합니다.
2. 기본적으로 클라이언트에서 `dev` 스테이지를 호출하였을 때의 때서비스 맵이 로딩되는 것을 확인할 수 있습니다. 각 노드는 각각 Amazon API Gateway, AWS Lambda 서비스를 나타내며 레이턴시 정보를 확인할 수 있습니다.

<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/1.png"></img></div>

> 만약 정보가 로딩되지 않는다면 상단의 새로고침 아이콘을 선택합니다. 기본적으로 최근 5분까지의 데이터만 검색해서 보여주기 때문에 만약 Step 1. 에서 REST API 를 호출한지 5분이 지났다면, 새로 호출하거나 시간 범위를 넓게 설정합니다.

3. 각 노드 및 노드를 연결하는 엣지를 클릭하면 레이턴시에 대한 히스토그램 정보도 확인할 수 있습니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/2.png"></img></div><br/>
위 화면은 API Gateway 에서 모든 요청 (100%)이 약 783ms 의 레이턴시가 소요되었다는 것을 의미합니다.  

> 히스토그램 해석에 대한 추가 정보는 [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-histograms.html#xray-console-historgram-details)를 확인하시기 바랍니다.

4. 좌측 패널의 [Traces]를 클릭하여, 추적 리스트로 이동합니다. 만약 5분이 경과하여 추적 리스트에 데이터가 확인되지 않는다면, 우측 상단의 [Last 5 minutes] 버튼을 클릭하여 시간을 조정합니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/3.png"></img></div><br/>

5. 추적들이 기본적으로 URL 기준으로 그룹화 되어 있는 것을 확인할 수 있으며, 평균 응답 시간, 응답 정보에 대한 통계를 확인할 수 있습니다. [Trace list] 리스트 상단에 있는 링크를 클릭하여, 추적 상세 페이지로 이동합니다. 
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/4.png"></img></div><br/>

6. 상세 페이지에서는 메소드, 응답 코드, 총 레이턴시, 추적ID의 전반적인 정보 및 서비스맵과 유사한 추적 맵 정보를 확인 할 수 있습니다.
또한 각 노드 별 상세 레이턴시 및 응답 코드 정보 또한 확인할 수 있습니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/5.png"></img></div>

### Step 3-1. AWS Lambda의 AWS X-Ray 추적 활성화
Step 2. 를 통해 Amazon API Gateway 에 AWS X-Ray를 활성화하여 **클라이언트 - Amazon API Gateway - AWS Lambda** 서비스 구간의 정보를 확인할 수 있었습니다. 하지만, AWS Lambda 함수에서 RDS SQL 쿼리 소요 시간등과 같은 세부적인 정보는 확인할 수 없었습니다. 이를 위해 AWS Lambda 에서도 AWS X-Ray 추적을 활성화 해야합니다. 

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
2. 이전에 생성한 **serverless-app-lambda** 를 선택하고, [Configuration] 탭의 [Monitoring and operations tools] 메뉴로 이동하여 좌측 상단의 [Edit] 버튼을 클릭합니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/6.png"></img></div><br/>
3. [Edit monitoring tools] 화면에서 [AWS X-Ray] 섹션의 [Active tracing] 토글을 클릭합니다. 이때 현재 AWS Lambda 함수에 AWS X-Ray 에 세그먼트 정보를 전달하기 위한 권한이 없기 때문에 자동으로 추가할 것이라는 안내 메시지가 나옵니다. [Save] 버튼을 눌러 활성화 시킵니다.<br/>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/7.png"></img></div><br/>
4. 정상적으로 활성화가 되면 [Monitoring and operations tools] 메뉴에서 [Active tracing] 상태가 `Enabled` 된것을 확인할 수 있습니다.

### Step 3-2. AWS X-Ray SDK 레이어 추가 및 패치 하기
AWS X-Ray SDK를 활용하여 Lambda 핸들러 내부에서 `pymysql` 와 같은 라이브러리를 사용한 다운스트림 호출을 기록할 수 있습니다. 이를 위해서는 AWS X-Ray Python SDK를 사용하여 함수에서 사용하는 라이브러리를 패치해야합니다. 라이브러리들을 패치하게 되면, AWS X-Ray 에서 알아서 해당 라이브러리를 사용한 호출을 추적의 서브세그먼트(Subsegment)로 인식하여 정보를 전달하게 됩니다. 

1. 로컬 환경에서 [AWS X-Ray SDK for Python를 다운로드](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python.html)하여 ZIP으로 압축시키거나, 다음 [링크](https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/src/xray.zip)를 통해 AWS X-Ray SDK ZIP 파일을 다운로드 받습니다.
2. [Module 2.Step 3-2](https://github.com/aws-samples/aws-games-sa-kr/tree/main/contributor/anhyobin/optimize-serverless-application-on-aws/module2#step-3-2-lambda-layer-%EA%B5%AC%EC%84%B1) 를 참고하여 **aws-xray-sdk** 라는 Lambda Layer를 등록하고, `serverless-app-lambda` 함수의 레이어로 추가합니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/8.png"></img></div>
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/9.png"></img></div><br/>
3. 이제 AWS X-Ray SDK를 함수에 Import하고, 다운스트림 호출을 기록하기 위해 라이브러리를 패치합니다. 이는 Lambda 함수가 초기화 시에만 필요하기 때문에 Handler 함수 외부에 아래와 같이 정의합니다.

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()
```

> AWS X-Ray for Python 는 특정 라이브러리들에 대해서만 패치를 지원하고 있습니다. 지원하는 리스트는 [AWS X-Ray 개발자 가이드](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-patching.html) 를 참고 하시기 바랍니다. 

전체 Lambda 함수 코드는 아래와 같습니다.
```python
import json
import pymysql
import boto3
import base64

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

secret_name = "serverless-app-rds-secret"
region_name = "ap-northeast-2"

def get_secret():    
    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return secret
    else:
        decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return decoded_binary_secret

secret = get_secret()
json_secret = json.loads(secret)

db = pymysql.connect(
    host = 'serverless-app-rds-proxy.proxy-c6hoagfyd6lw.ap-northeast-2.rds.amazonaws.com', 
    user = json_secret['username'], 
    password = json_secret['password']
    )

cursor = db.cursor()

def lambda_handler(event, context):
    cursor.execute("select now()")
    result = cursor.fetchone()

    db.commit()
    
    return {
        'statusCode': 200,
        'body': json.dumps(result[0].isoformat())
    }
 ```
 4. 변경된 코드를 Deploy 하고, AWS X-Ray 에서 AWS Lambda 함수의 정보도 기록되는지 확인을 하기 위해서 API Gateway의 엔드포인트로 다시 한번 브라우저 혹은 터미널에서 호출합니다.
 5. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS X-Ray 서비스로 이동합니다.
 6. AWS X-Ray 서비스 맵에서 AWS Lambda Function 노드 및 SQL 쿼리 실행 노드가 추가된것을 확인할 수 있습니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/10.png"></img></div><br/>
 7. [Trace list] 에서 상단의 추적을 선택하여 상세 페이지로 이동하면, Lambda 함수 초기화 및 SQL 쿼리 실행 레이턴시 정보를 담은 상세 정보를 확인할 수 있습니다.
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module5/img/11.png"></img></div><br/>

## [선택 사항 | 챌린지]
[Module 4.](https://github.com/aws-samples/aws-games-sa-kr/tree/main/contributor/anhyobin/optimize-serverless-application-on-aws/module4) 의 부하테스트를 수행 한 후에, X-Ray에 수집되는 정보들을 한번 확인해봅니다. 
