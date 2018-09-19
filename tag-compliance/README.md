### EC2 Tag Compliance
Listens `RunInstances` CloudTrail Event and inspects tags. If the mandatory tags are not available, terminate instances immediately.

#### Cloud Watch Rule 
```yaml
    Type: "AWS::Events::Rule"
    Properties: 
      Description: Event Rule To Trigger Tag Compliance Lambda
      EventPattern:
        detail-type:
          - AWS API Call via CloudTrail
        source:
          - aws.ec2
        detail:
          eventSource:
            - ec2.amazonaws.com
          eventName:
            - RunInstances        
      Name: Tag-Compliance-EC2-Rule
      Targets:
        - 
          Arn: !Ref YOUR_LAMBDA_FUNCTION_ARN
          Id: SOME_ID
```