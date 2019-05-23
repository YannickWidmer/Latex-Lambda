cd latex_compiler_lambda
pip install -r requirements.txt --target python_packages/

docker build --no-cache -t la0ruse/latex_compile_lambda .

rm latex_compile_lambda.zip
docker run --rm -it -v $(pwd)/:/var/host la0ruse/latex_compile_lambda zip --symlinks -r -9 /var/host/latex_compile_lambda.zip .
echo "Now uploading the function to AWS cloud"
aws lambda update-function-code --function-name latex_compiler --zip-file fileb://latex_compile_lambda.zip
