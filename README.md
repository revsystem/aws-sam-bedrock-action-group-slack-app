# aws-sam-bedrock-slack-backlog-rag-app

This is a chatbot application with the  AWS bedrock. AI can answer questions using external API.

## Setup

### Python

```console
python3 -m venv .venv
source .venv/bin/activate
```

```console
pip3 install --upgrade pip
pip3 --version
```

```console
pip 23.3.2 from /home/xxxxx/aws-sam-bedrock-action-group-slack-rag-app/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

### AWS SAM

```console
curl -OL  https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation
```

Install the AWS SAM CLI.

```console
sudo ./sam-installation/install
sam --version
```

## Deploy

```console
sam build
sam deploy
```

You must set up the AWS Secrets Manager, Agents for AWS bedrock, and Slack App. Please follow the document on Qiita.com below.

https://qiita.com/revsystem/private/93e9c744c63c5667a810

```console

## Delete

```console
sam delete
```
