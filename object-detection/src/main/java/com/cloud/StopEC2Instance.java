package com.cloud;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.StopInstancesRequest;
import com.amazonaws.util.EC2MetadataUtils;

public class StopEC2Instance
{
    public static void stopEC2Instance(BasicAWSCredentials credentials)
    {
        AmazonEC2 ec2Client = AmazonEC2ClientBuilder.standard()
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .withRegion(Regions.US_WEST_1)
                .build();

        //Stop EC2 Instance
        String instanecID = EC2MetadataUtils.getInstanceId(); // Get the Instance ID of current EC2 instance
        StopInstancesRequest stopInstancesRequest = new StopInstancesRequest()
                .withInstanceIds(instanecID);
        ec2Client.stopInstances(stopInstancesRequest).getStoppingInstances().get(0).getPreviousState().getName();
        System.out.println("ID of the Stopped instance "+instanecID);

    }
}

