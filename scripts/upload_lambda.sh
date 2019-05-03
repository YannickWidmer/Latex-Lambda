cd lambda_main_latex
pip install -r requirements.txt --target python_packages/

docker build --no-cache -t la0ruse/lambda_main_latex .

rm lambda_main_latex.zip
docker run --rm -it -v $(pwd)/:/var/host la0ruse/lambda_main_latex zip --symlinks -r -9 /var/host/lambda_main_latex.zip .
echo "Now uploading the function to AWS cloud"
aws lambda update-function-code --function-name lambda_main_latex --zip-file fileb://lambda_main_latex.zip
