package com.cloud;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.*;

import java.util.Collections;

public class SQSQueue {


    public boolean isQueueEmpty(AmazonSQS SQS,BasicAWSCredentials credentials, String queueURL) {
        try {

            Long size = 0L;
            GetQueueAttributesRequest getQueueAttributesRequest = new GetQueueAttributesRequest(queueURL,
                    Collections.singletonList(QueueAttributeName.ApproximateNumberOfMessages.name()));
            GetQueueAttributesResult queueAttributes = SQS.getQueueAttributes(getQueueAttributesRequest);
            if (queueAttributes.getAttributes() != null) {
                size = Long.valueOf(queueAttributes.getAttributes().getOrDefault(
                        QueueAttributeName.ApproximateNumberOfMessages.name(), "0"));
            }

            if (size > 0L) {
                System.out.println("Total Number of messages in SQS " + size);
                if(deleteMessage(SQS,queueURL))
                {
                   /* getQueueAttributesRequest = new GetQueueAttributesRequest(queueURL,
                            Collections.singletonList(QueueAttributeName.ApproximateNumberOfMessages.name()));
                    queueAttributes = SQS.getQueueAttributes(getQueueAttributesRequest);
                    System.out.println("Total number of messages in SQS after processing the request is "+Long.valueOf(queueAttributes.getAttributes().getOrDefault(
                            QueueAttributeName.ApproximateNumberOfMessages.name(), "0"))); */
                   System.out.println("Request will be processed");
                   return true;
                }
                else
                    { return false; }
            } else {
               // System.out.println("Queue is Empty");
                return false;
            }

        } catch (Exception e) {
            System.out.println("Issue with SQS and error is " + e.toString());
            return false;
        }
    }

    public boolean deleteMessage(AmazonSQS SQS,String queueUrl) {
        try {
            final String messageReceiptHandle = SQS.receiveMessage(queueUrl).getMessages().get(0).getReceiptHandle();
            System.out.println(messageReceiptHandle);
            SQS.deleteMessage(new DeleteMessageRequest(queueUrl, messageReceiptHandle));
            return true;
        }
        catch(Exception e)
        {
            System.out.println("Issue in deleting the message from SQS");
            return false;
        }
    }
}


