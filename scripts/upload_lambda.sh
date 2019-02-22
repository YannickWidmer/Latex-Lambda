cd latexlambda
pip install -r requirements.txt --target python_packages/

docker build --no-cache -t la0ruse/lambdalatex .

rm latexlambda.zip
docker run --rm -it -v $(pwd)/:/var/host la0ruse/lambdalatex zip --symlinks -r -9 /var/host/latexlambda.zip .
echo "Now uploading the function to AWS cloud"
aws lambda update-function-code --function-name latex_compiler --zip-file fileb://latexlambda.zip
