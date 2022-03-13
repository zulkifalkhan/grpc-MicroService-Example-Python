[This code's documentation lives on the grpc.io site.](https://grpc.io/docs/languages/python/quickstart)

#how We proceed
This microservice1 calls another microservice2
1.For that i first need .proto of that microservice,place it in folder where .proto file exist [Note:donot have repeated code inside it,means same code across multiple .proto files]

2.Compile both files to generate new files from it [first compile dependacy stubs]
3.Then in server (copy and paste code of client for that specific server to make communication between them.)
