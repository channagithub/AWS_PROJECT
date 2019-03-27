package com.cloud;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.TerminateInstancesRequest;
import com.amazonaws.util.EC2MetadataUtils;

public class TerminateEC2Instance
{
    public static void terminateEC2Instance(BasicAWSCredentials credentials)
    {
        // Set up the amazon ec2 client
        AmazonEC2 ec2Client = AmazonEC2ClientBuilder.standard()
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .withRegion(Regions.US_WEST_1)
                .build();

        //Stop EC2 Instance
        String instanecID = EC2MetadataUtils.getInstanceId(); // Get the Instance ID of current EC2 instance
        TerminateInstancesRequest terminateInstancesRequest = new TerminateInstancesRequest()
                .withInstanceIds(instanecID);
        ec2Client.terminateInstances(terminateInstancesRequest).getTerminatingInstances().get(0).getPreviousState().getName();
        System.out.println("ID of the terminated instance "+instanecID);

    }
}

