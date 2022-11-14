# ECE1779_Group22_a2

## Project description
This project is a simple application that allows users to upload and retrieve images with cache.
The user can upload a image to store into the cache with a unique key and the image will be stored into local file system (S3) as well as database (RDS).
The user can also retrieve images with a specific key, and the images will be retrieved from cache or local file system (S3) depending on whether they are in the cache or not.
Different cache configuration and mode can be changed to meet user's need and the statistics of the cache stored in the cloudwatch will be displayed upon request.


## General Architecture
![Screenshot](architecture.png)

The diagram above shows the general architecture of our application. 
The frontend, the memcache, the manager app, and the autoscaler highlighted in blue are the four Flask instances in our application. 
In this project, our memcache is a pool of nodes and each node is an EC2 instance that stands alone as a server and functions as a small memcache. 
The frontend, manager app and the autoscaler run on another EC2 instance. 
Generally, the web browser sends requests to the frontend. 
The frontend directly interacts with S3 and RDS for image retrieval and storage. 
Then, the frontend will send the requests to the manager app to interact with memcache. Manager app, as a middle man, directs the requests to the corresponding memcache instance through consistent hashing based on MD5 hashes, and helps send back the response to frontend. 
Finally, after all communications end, the frontend will render the information the client needs and display it on the browser. 

In addition, manager app has the right to set configuration and mode for memcache and stores the setting in RDS directly. 
It can also show the aggregated statistics of memcache retrieved from the cloud watch. 
When the mode is set to auto mode, the manager app triggers the autoscaler, which helps monitor the statistics in the cloudwatch put by each memcache node. 
Each minute when the autoscaler detects that a size change is needed, it will inform the manager app. 

## Run the application
```
./start.sh
```
