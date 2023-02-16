# FastAPI SAAS Template
FastAPI is a web framework which can be applied to various problems. Building Subscription As a Service application is one use case.

As such I left the need to create a template that provides a lot of base/out of the box features such as 
Configs, Migrations, Authentication, Authorization and Permissions.

The core of the Application is a User Auth module and Organizations.

Organization is a team with team members. Invites can be sent via Links which can be revoked.

Permissions include freemium block checks as dependencies, an example is limiting the number of organizations a freemium user can have to 2.


Admin right actions: Only Admin can perform such actions.
Strict Member Actions.



# Installation
Click on use Template at the top righthand corner of the screen which would create a repository for you.

After Cloning the repo we are down to usage.

## Usage

first thing is to set up your virtual environment. 

By way of illustration I will provide snippets to help you setup.

Ps. All commands below are terminal commands.



creating a virtualenv via venv
```
python3 -m venv {name of your env}
```

To activate your venv

```
source {name of your venv}/bin/activate
```



Please create a dotenv file for your environment variables. An example environment variable is provided. This file is called ```.example.env```.

Installing Requirements can be done by using this command.


```
pip install -r requirements.txt

```

Migrating DB with Alembic

```
alembic upgrade heads
```

Starting your Server

```
uvicorn src.app.main:app --reload

```

## PostMan Collection.

I create a postman collection that can be forked for testing. here -> https://documenter.getpostman.com/view/17138168/2s93CGRbQg


## Contributing
There are few things that need to be worked on, they are 

1. Testing: I will be writting a comprehensive overwhelmingly encompassing test case which will cover every case especially edge cases. I would love to learn to write good test so I am willing to partner with engineers on this.

Intialy I was looking forward to writting test that handles edge cases oe exception block in place, however for now I am testing best case. 

What are the best cases? These are the apporiate response during the req-res cycle without any HTTPEception.


PR are welcome, For major changes, please open an issue first
to discuss what you would like to change.



## License


MIT License

Copyright (c) [2023] [FastAPI SAAS Template]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.