# Module 1. 나의 첫 AWS Lambda  
  
이번 워크샵을 통해 처음 AWS Lambda 를 접하는 분들을 위해 간단한 실습을 준비했습니다. 이미 Lambda 가 익숙한 분들은 바로 [Modeul 2]() 를 진행하셔도 무방합니다.  
  
서버리스의 대표적인 서비스 답게 Lambda 는 서버를 프로비저닝하거나 관리하지 않고도 코드를 실행할 수 있게 해주는 컴퓨팅 서비스입니다. [Lambda 는 동기, 비동기 방식으로 호출](https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/lambda-invocation.html)이 가능하고 기본적으로 이벤트에 반응하여 동작합니다. 이러한 기능을 활용해 많은 분들이 파일이나 데이터 처리, 자동화 등에 적극적으로 Lambda 를 활용 중이고, 나아가서는 웹 애플리케이션이나 모바일 백엔드 구축에 사용되고 있습니다.  
  
Module 1 에서는 아래 아키텍처와 같이 Amazon S3 에 파일이 업로드 되는 ***이벤트***가 발생하면 Amazon SNS 를 통해 사용자에게 email 로 알람을 전송하는 간단한 자동화 프로세스를 AWS Lambda 를 통해 구축해보겠습니다.  
  
<div align="center">
    <img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/module1_architecture.jpg"></img> 
</div>  
  
### Step 1. Amazon SNS 구성
  
첫번째로 할 작업은 AWS Lambda 가 이벤트를 처리한 결과를 email 로 전송할 때 사용할 Amazon SNS 를 구성하는 것입니다.

1. [AWS Management Console](https://console.aws.amazon.com/) 에서 Amazon SNS 서비스로 이동합니다. 리전은 서울(ap-northeast-2)을 사용합니다.
2. 메인 화면의 [Create topic] 하단의 [Topic name] 에 **s3-event** 를 입력하고 [Next step] 을 클릭합니다.  <div align="center">
    <img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/1.png"></img> 
</div>  
3. 별도의 내용 변경 없이 [Create topic] 버튼을 클릭하여 SNS Topic 생성을 완료합니다.
4. 생성된 Topic 하단의 [Subcriptions] 탭에서 [Create subscription] 을 선택합니다.
5. [Protocol] 에는 **Email** 을 선택하면 Endpoint 메뉴가 나타납니다. [Endpoint] 에는 email 알람을 받을 **email 주소** 를 입력합니다. [Create subscription] 버튼을 클릭하여 구독을 완료합니다.
<div align="center">
    <img src="https://github.com/aws-samples/aws-games-sa-kr/blob/main/contributor/anhyobin/optimize-serverless-application-on-aws/module1/img/3.png"></img> 
</div>  
6.
