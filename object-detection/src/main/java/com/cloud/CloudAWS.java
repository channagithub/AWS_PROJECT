package com.cloud;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.util.IOUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.TimeUnit;

public class CloudAWS {

    public static void main (String[] args) {

        try {


            // Creates s3client to access s3 bucket
            int count=0;
            String bucketName = "clouddeeplearning";
	    AccessKeyID = "xxxxx";
	    SecretAccessKey = "yyyyyy";
            BasicAWSCredentials credentials = new BasicAWSCredentials(AccessKeyID, SecretAccessKey);
            AmazonS3 s3Client = AmazonS3ClientBuilder.standard().withRegion("us-west-1")
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .build();

            // Variables
            String fileName = "video.h264";
            String videoName = "video_name.txt";
            String unixPath = "/home/ubuntu/darknet/";
            // String windows_path = "C:\\Users\\abhin\\Desktop\\dump\\"; // To test on Windows machine during development
            // change to linux
            // 1. Replace windows_path with unix_path
            // 2. Replace result_label.txt with result_label
            // 3. Uncomment code for "Run the script to perform deep learning" ( 2 lines )

            // Check whether Queue is empty, if not then delete one message
            SQSQueue sqsQueue=new SQSQueue();
            String queueURL="https://sqs.us-west-1.amazonaws.com/138838165366/aws-project-queue";
            AmazonSQS SQS = AmazonSQSClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .withRegion(Regions.US_WEST_1)
                    .build();


            while(true) {
                if (sqsQueue.isQueueEmpty(SQS, credentials, queueURL)) // If queue is not empty then it will delete one message then return true
                {
                    count=0; // Re-initialize the Timer
                    // Create folder based on the timestamp in bucket
                    DateTime now = DateTime.now(DateTimeZone.UTC);
                    String folderName = "Request-" + now.toString().replace(":", "-");
                    String folderPath = folderName + "/";
                    CreateFolder.createFolder(bucketName, folderPath, s3Client);
                    System.out.println("Folder has been created, name of the folder is " + folderName);

                    // Create a connection to URL and fetch the video name ( from Header )
                    String[] tokens = {};
                    String url = "http://206.207.50.7//getvideo";
                    URL obj = new URL(url);
                    URLConnection conn = obj.openConnection();
                    String contentName = conn.getHeaderField("Content-Disposition");
                    if (contentName == null) {
                        System.out.println("Video name is empty");
                    } else {
                        tokens = contentName.split("=");
                    } // contentName structure -> attachment; filename="video-pie1-081409.h264"

                    // Get the video and store it on  an EC2 instance
                    Path path;
                    path = FileSystems.getDefault().getPath(unixPath + fileName);
                    InputStream is = obj.openStream();
                    Files.copy(is, path, StandardCopyOption.REPLACE_EXISTING);
                    is.close();
                    System.out.println("Video has been downloaded ");

                    // Write the video name into a file and put in s3 bucket
                    InputStream in = org.apache.commons.io.IOUtils.toInputStream(tokens[1], "UTF-8");
                    byte[] bytes = IOUtils.toByteArray(in);
                    ObjectMetadata metadata = new ObjectMetadata();
                    metadata.setContentLength(bytes.length);
                    ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);
                    PutObjectRequest putObjectRequest = new PutObjectRequest(bucketName, folderPath + videoName, byteArrayInputStream, metadata);
                    s3Client.putObject(putObjectRequest);
                    System.out.println("Video name: " + tokens[1]);

                    // Run the script to perform deep learning
                    String myShellScript = unixPath + "deep_learning.sh";
                    Process p = Runtime.getRuntime().exec(myShellScript);
                    p.waitFor();  // Wait for the subprocess to finish
                    System.out.println("Deep learning detection has been done ...!");

                    // Upload the result to S3
                    String result = "result_label.txt";
                    s3Client.putObject(new PutObjectRequest(bucketName, folderPath + result, new File(unixPath + "result_label"))); // Upload result_label
                    System.out.println("Done with uploading and status is success ...! " + "\n \n ");


                }
                else {
                    count++;
                    TimeUnit.SECONDS.sleep(5);
                    // System.out.println(count*5 + "seconds");
                    if(count==60)  // 60*5 = 300s , wait for 5 mins before terminating
                    {
                        break;
                    }
                }
            }
                    System.out.println("Terminate EC2 instance");
                    StopEC2Instance.stopEC2Instance(credentials);
        }
        catch (Exception e) {
            System.out.println(e.toString());
        }
    }
}
