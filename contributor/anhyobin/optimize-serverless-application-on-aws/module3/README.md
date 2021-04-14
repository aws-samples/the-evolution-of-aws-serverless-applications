# Module 3. 서버리스 애플리케이션의 DB 사용 경험 개선

이 모듈에서는 Module 2.에서 생성한 API Gateway, Lambda, RDS를 기반으로 AWS Secrets Manager와 RDS Proxy 설정을 추가하는 과정입니다. 이 모듈을 추가함으로서 Lambda 기반 API application 서비스의 장점은 AWS Secrets Manager를 통하여 RDS의 보안 정보를 쉽게 관리할 수 있고, RDS Proxy를 설정함으로서 Connection pooling로 보다 효율적인 connection 관리로 API 의 성능을 향상 시킬 수 있습니다.

Step 1. AWS Secrets Manager 새 보안 암호 저장, VPC endpoint 생성

1. 콘솔 sm 들어감
2. 보안암호 저장
3. 서브넷 생성, sg 생성(꼭필요한지 확인)
4. vpc 엔드포인트 콘솔 들어감, 생성

Step 2. RDS Proxy 설정

1. RDS 콘손들어가서 serverless rds 들어감
2. 프록시 생성함, endpoint 확인 메모

Step 3. Lambda 코드 변경

1. 람다 콘솔 들어감 람다 코드를 교체함
2. 람다코드에서 수정해야할 부분 수정, 업데이트
3. api gateway주소를 다시 호출해봄 제대로 동작하면 완료