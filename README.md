# Latex Compiler Lambda

**Lambda function to create pdfs and html files from templates written in Latex.**
The lambda expects a `name` and a `data` dict and a boolean `to_pdf`. It then returns a pdf or an html file according to `to_pdf`, created by rendering the template `name` using the data ind `data`.

Example usage

``` python
import base64
import boto3
import ast

payload = json.dumps({
    "name": "nda",
    "data": {
            "ownerName": "Yannick:Owner",
            "recipientName": "tispr:Recipient",
            "contractDated": "1/1/2019",
            "contractEndWithinDays": 7,
            "isDisclosurePerpetual": False,
            "lawState": "California:lawState",
            "isOwnerCompany": False,
            "isRecipientCompany": True,
            "recipientRepresentantName": "Jonathan:Recipient",
            "recipientRepresentantTitle": "Boss:recipient",
            "ownerRole": "Client",
            "ownerAddress": "8123 McConnell:OwnerAddress",
            "ownerState": "California:OwnerState",
            "ownerZipCode": "90045:OwnerZip",
            "recipientAddress": "8123 McConnell:RecipientAddress",
            "recipientState": "California:Recipient",
            "recipientZipCode": "90045:recipient"
        },
    "to_pdf": True
    })


client = boto3.client('lambda')

response = client.invoke(
    FunctionName="latex_compiler",
    InvocationType='RequestResponse',
    Payload=payload,
)

res = ast.literal_eval(response['Payload'].read().decode())
return base64.b64decode(res['pdf'])
```
**Note that a configured Access Key Pair for AWS is assumed.**
In this example the `pdf` file is returned as a string. Replacing `"to_pdf": True` to `"to_pdf": False` and `return base64.b64decode(res['pdf'])` to `return base64.b64decode(res['html'])` returns html code.

Note that the dict `res` contains the keys `stdout`, `tex`, `path`, `pdf`, and  `log`. And in  the case when `"to_pdf": False` the keys `stdout`, `tex`, `path`, `html`, `css`, and  `log`.
The remaining content is sent for debugging purposes when developing new templates. The entries `tex`, `stdout`, `path` and `log` are sent as plain string all others are base64 encoded.

Finally in case an error occures res contains `errorMessage`, `errorType`,and `stackTrace`, all as plain text.

# Structure of this repository

Every thing to create the lambda function is in `latexlambda/`. The templates and their corresponding python classes are stored in s3, however we develop them `templates/` from where we upload them to s3. The file `templates/README.md` describes the expected fields for each template. Scripts helping development and testing are in `scripts/`,  when testing files are written into `test_output/`. To test from a browser a sample flask application is in `server/`.

# How the Lambda works

When the lambda function is called with
```
{
    "name": {name},
    "data": {data},
    "to_pdf": {to_pdf}
}
```
as argument, it first queries s3 for a template named `{name}.tex` and a python class `{name}.py`. In staging the folder it queries is `latex_template_test/` in the bucket `ds-temp-stg`.

It then passes `{data}` and `{to_pdf}` to the function `render` in `{name}.py` of the signature
``` python
def render(data, to_pdf):
```
which returns a dict.
**This function is also in charge of validating the data in `{data}` and returns an according error if not**
This new dict is then passed to Jinja to render the template `{name}.tex` with it. The result is a latex file with no Jinja commands anymore which is then compiled using `latexmk` in case `{to_pdf}` is true and `htlatex` if not. The remainder of the lambda function encodes the result before sending it back.

# Developing

## Code Structure

The LaTeX compilation consists of 2 lambdas and one s3 directory, these correspond to the directories `lambda_main_latex`, `latex_compiler_lambda` and `templates`. Additionally there is a `script` folder for build and test scripts aswell as a `server` for prototypes with frontend.

## Setup lambda in an AWS environment

To add the LaTeX compiler to an AWS environment, create two lambdas and put the templates in an s3 directory.
    - First decide in which bucket, or create a bucket, and a prefix inside that buchet to store the template
    - Then create the pure LaTeX comipler with runtime environment Python 3.6 and environment variables `bucket` and `key_prefix` pointing to the s3 bucket and directory where the templates are.
    - Then create the main lambda with runtime environment Python 3.6 and the same environment variables `bucket` and `key_prefix`. Additionally the environment variable `compiler_function_name` which should be set to the name of the first lambda function.
    - Both Lambdas need access to read from the s3 directories additionally the main lambda needs access to trigger the compiler lambda like in the folowing mock policy:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "SomeID name",
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": "arn:aws:lambda:us-west-2:{the rest of the arn}"
            }
        ]
    }

All needed files to work on the Lambda function are contained in the folder `latexlambda/` the templates and their corresponding python classes are in `templates/`.

Note that for vs code users the `taks.json` file contains build tasks to upload the lambda function aswell as to upload the templates and test tasks to test the lambda or start a flask server to test it in a browser. **Make sure to configure your aws cli with an access key pair for the staging environment before using those scripts.** The scripts used by these tasks are in `scripts/`.

TODO: create process to upload lambda and templates to production.


## Developing/uploading the Lambda function

The executed code in the cloud is contained in `lambda_function.py`. The libraries available to the lambda function and hence to the template classes are in `requirements.txt`, the LaTex libraries are specified in the Dockerfile and the LaTex settings are specified in `texlive.profile`. `setup.cfg` is needed to avoid a problem Docker has when installing LaTex. To upload a new version of the lambda function

- delete `latexlambda/latexlambda.zip`
- install the requirements

inside `latexlambda/` run `pip install -r requirements.txt --target python_packages/`
- build the docker image

inside `latexlambda/` run `docker build --no-cache -t la0ruse/lambdalatex .` (where la0ruse is simply my dockerhub username and can be replaced with anything, the same name needs to be used in the next command though)
- create the zip file

For this use the docker image by runing `docker run --rm -it -v $(pwd)/:/var/host la0ruse/lambdalatex zip --symlinks -r -9 /var/host/latexlambda.zip .`

This will take `install-tl-unx.tar.gz` to install LaTex, install extra packages according to what is specified in the Dockerfile, delete unneeded files to make sure the zip file is small enough to be uploaded as a lambda function. Then it copies the installed python packages to the correct location. Then it copies `lambda_function.py` into the zip file.

- upload the zip file

Using the AWS CLI to upload the lambda function, first make sure that your credentials are configure for the right account (staging/production) and then run `aws lambda update-function-code --function-name latex_compiler --zip-file fileb://latexlambda.zip`

### Uploading the lambda using the script

To simplify the process of uploading the lambda function run the script `scripts/upload_lambda.sh` from the root folder. To make it easier for vs code users an according building task called `upload lambda` is in `tasks.json`.

### Adding libraries

To add a library simply add it in `latexlambda/requirements.txt`. The next build of the lambda function will contain the library.


### Trouble shooting LateX missing files

tlmgr search --global --file {missing file name}

will tell which packages contain this file. You can then add the package to the list in Dockerfile

## Developing Templates

To add a new template simply add a file ending with `.tex` and another with the same name ending in `.py`. The tex file needs to be written in LaTex and can use `\VAR` to include variables that are passed to Jinja and `\BLOCK` to create logic using the same variables. The python file needs a function with following signature
```python
def render(data, to_pdf):
```
which returns a dict. This dict is what will be passed to jinja when rendering the template, meaning that if it returns `{"name":"John Doe"}` and the tex file contains `\VAR{ name }` this will be replaced with `John Doe`. **Python libraries used in this class need to be in `latexlambda/requirements.txt`**.

Note that when reading Jinja resources, the Jinja Environment used in the lambda is

```python
jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=False,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.join('/tmp', 'templates')
```

To start a new template, a good start is to copy `template.py` and `template.tex` and replace the names with the new template name. Write the python file expecting whatever will be send to the lambda function and returning the dict for Jinja. Also make sure to do data validation inside this function.

## Upload templates

The templates can be uploaded using the vs code task `build` -> `upload templates` or by running
```sh
aws s3 cp templates/ s3://ds-temp-stg/latex_template_test --recursive --exclude \"*\" --include \"*.tex\" --include \"*.py\"
```
**Make sure to have configured the aws cli with an Access Key Pair for staging AWS.**

# Testing

To test the lambda function simply run `scripts/test_lambda.py`. To test new templates simply add an entry at the end like the following

```python
test_template({template_name},{the_data_to_be_send},{true_or_false})
```

To test how it will render in the browser run the test server after changing the template name and data sent. Thissimulates how a browser display the generated html using the static css file `server/static/style.css`.

If something is not displayed as whished change the css file until this is reached. We then need to implement the css change in the actual app.