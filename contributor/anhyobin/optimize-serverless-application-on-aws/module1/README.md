# Module 1. 나의 첫 AWS Lambda  
  
이번 워크샵을 통해 처음 AWS Lambda 를 접하는 분들을 위해 간단한 실습을 준비했습니다. 이미 Lambda 가 익숙한 분들은 바로 [Modeul 2]() 를 진행하셔도 무방합니다.  
  
서버리스의 대표적인 서비스 답게 Lambda 는 서버를 프로비저닝하거나 관리하지 않고도 코드를 실행할 수 있게 해주는 컴퓨팅 서비스입니다. [Lambda 는 동기, 비동기 방식으로 호출](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/lambda-invocation.html)이 가능하고 기본적으로 이벤트에 반응하여 동작합니다. 이러한 기능을 활용해 많은 분들이 파일이나 데이터 처리, 자동화 등에 적극적으로 Lambda 를 활용 중이고, 나아가서는 웹 애플리케이션이나 모바일 백엔드 구축에 사용되고 있습니다.  
  
Module 1 에서는 아래 아키텍처와 같이 Amazon S3 에 파일이 업로드 되는 ***이벤트***가 발생하면 Amazon SNS 를 통해 사용자에게 email 로 알람을 전송하는 간단한 자동화 프로세스를 AWS Lambda 를 통해 구축해보겠습니다.  
  
<div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/module1_architecture.jpg"></img></div>  
  
### Step 1. Amazon SNS 구성
  
첫번째로 할 작업은 AWS Lambda 가 이벤트를 처리한 결과를 email 로 전송할 때 사용할 Amazon SNS 를 구성하는 것입니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon SNS 서비스로 이동합니다. 리전은 서울(ap-northeast-2)을 사용합니다.
2. 메인 화면의 [Create topic] 하단의 [Topic name] 에 **s3-event** 를 입력하고 [Next step] 을 클릭합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/1.png"></img></div>
3. 별도의 내용 변경 없이 [Create topic] 버튼을 클릭하여 SNS Topic 생성을 완료합니다.
4. 생성된 Topic 하단의 [Subcriptions] 탭에서 [Create subscription] 을 선택합니다.
5. [Protocol] 에 **Email** 을 선택하면 Endpoint 메뉴가 나타납니다. [Endpoint] 에는 email 알람을 받을 **email 주소** 를 입력합니다. [Create subscription] 버튼을 클릭하여 구독을 완료합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/3.png"></img></div>
6. 잠시 후 입력한 email 주소로 Subscription Confirmation 메일이 수신됩니다. 메일의 [Confirm subscription] 을 클릭하여 구독을 완료합니다.

### Step 2. Amazon S3 구성

이제 AWS Lambda 에 이벤트를 발생시킬 S3 Bucket 을 생성합니다. 

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon S3 서비스로 이동합니다.
2. 화면 상단의 [Create bucket] 을 선택하여 Bucket 생성을 시작합니다.
3. [Bucket name] 에 실습에 사용할 **사용자 고유의 이름** 을 입력한 뒤 별도의 옵션 변경 없이 하단의 [Create bucket] 버튼을 클릭하여 생성을 완료합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/5.png"></img></div>

### Step 3. AWS Lambda 를 구성하여 이벤트 처리

이제 AWS Lambda 를 구성하여 앞서 생성한 S3 Bucket 과 SNS Topic 을 통해 파일이 업로드 되면 email 로 알람을 받는 간단한 자동화 구성을 해보겠습니다. Lambda 함수는 AWS 콘솔, IDE Toolkit, AWS CLI 또는 AWS SDK 등 다양한 방법으로 작성할 수 있습니다. 오늘 실습에서는 AWS 콘솔을 활용하지만 [IDE Toolkit 이나 AWS Cloud9 을 통한 개발](https://aws.amazon.com/ko/blogs/korea/how-to-use-aws-services-from-you-desktop-easily/) 방법도 살펴보시기 바랍니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 AWS Lambda 서비스로 이동합니다.
2. 화면 상단의 [Create Function] 버튼을 클릭합니다.
3. Lambda 함수를 생성할 수 있는 다양한 옵션이 제공되는 것을 확인할 수 있습니다. 이번 실습은 [Author from scratch] 옵션을 통해 처음부터 함수를 생성합니다.
4. [Function name] 에는 **s3-email** 을 입력하고, [Runtime] 은 **Python 3.8** 을 선택합니다. 그 외에도 다양한 프로그래밍 언어를 지원하는 것을 확인할 수 있습니다.
5. [Change default execution role] 메뉴를 확장한 뒤 [Create a new role from AWS policy templates] 를 선택합니다.
6. [Role name] 에는 **lambda-sns-pub** 을 입력하고, 아래 [Policy templates - optional] 에는 **Amazon SNS publish policy** 를 선택합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/6.png"></img></div>
7. 하단의 [Create function] 버튼을 클릭하여 Lambda 함수 생성을 완료합니다.
8. 코드를 수정하기 전에 잠시 생성된 코드를 살펴보겠습니다. 아래 [Code] 탭의 **s3-email** 폴더 아래의 **lambda_function.py** 를 보면 아래와 같이 단순한 Python 코드가 생성된 것을 확인할 수 있습니다.
```Python
import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
```
보시는 것처럼 모든 Lambda 함수에는 [Handler](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/python-handler.html) 가 포함 되어 있습니다. Lambda 함수가 호출되면 실행되는 메소드가 바로 이 Handler 메소드입니다. 이러한 특징을 이용하여 Lambda 함수의 코드를 최적화 하는 실습은 [Module 2.X. AWS Lambda 코드 최적화]() 에서 조금 더 살펴보도록 하겠습니다.
  
이번 실습에 사용되는 함수는 Amazon S3 에 파일이 업로드 되는 이벤트가 발생하면 Amazon SNS 를 통해 사용자에게 이메일을 발송합니다. 이러한 로직은 lambda_handler() 메소드 내부에 구현해주면 됩니다. Lambda 함수의 가장 기본이 되는 구조입니다.
  
9. 해당 코드를 모두 삭제한 뒤 아래의 코드를 붙여 넣습니다. 코드의 TopicArn 은 Step 1. Amazon SNS 에서 구성한 Topic 을 참조합니다.
```Python
import json
import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    response = sns.publish(
        TopicArn = '생성한 SNS Topic 의 ARN',
        Message = event['Records'][0]['s3']['object']['key'] + ' has been ' + event['Records'][0]['eventName'],
        Subject = 'S3 Event',
        )
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
```

10. [Deploy] 버튼을 클릭하여 작성한 코드를 저장합니다. 가장 간단하게 AWS 콘솔에서 Lambda 함수를 작성하는 법을 살펴 봤습니다. 
11. 마지막으로 작성한 Lambda 함수를 호출 할 이벤트를 구성합니다. 상단의 [+ Add trigger] 버튼을 클릭합니다.
12. [Select a trigger] 메뉴에는 **S3** 를 선택합니다. [Bucket] 은 Step 2. Amazon S3 에서 구성한 S3 Bucket 을 선택합니다. 하단의 Recursive invocation 옵션을 체크한 뒤 [Add] 버튼을 클릭하여 트리거 설정을 완료합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/10.png"></img></div>

### Step 4. 테스트

모든 작업을 완료했습니다. 이제는 작성한 AWS Lambda 함수가 구성한 이벤트에 맞게 동작하는지 테스트를 해보겠습니다.

1. [AWS 콘솔](https://console.aws.amazon.com/) 에서 Amazon S3 서비스로 이동합니다.
2. 앞서 생성했던 Bucket 으로 이동합니다.
3. 아무 파일이나 드래그&드랍 하여 업로드 해줍니다.
4. 잠시 후 지정한 email 주소로 다음과 같은 이메일이 온 것을 확인합니다. <div align="center"><img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/9.png"></img></div>
