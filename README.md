This project is to create a lambda function to create pdfs and html files from templates written in Latex.
The lambda expects a name and a data dict. Using the name it gatters the template placed in  s3 bucket where the lambda has access, together with a python class of the same name, used to preprocess the data. The template is written using Jinja to which the dict returned by the python class is passed.


# Usage

TODO

# Using the lambda function

The function expects a template name and data to render the template before compiling it with latex. For a template name an according template with `.tex` ending should be available in the corresponding s3 bucket aswell as a render module in render_modules of the same name with the function render expecting a dict and returning a dict which will then be passe to jinja to render the template.

# Trouble shooting LateX missing files

tlmgr search --global --file {missing file name}

will tell which packages contain this file. You can then add the package to the list in Dockerfile