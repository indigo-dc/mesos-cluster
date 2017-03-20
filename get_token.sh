#!/bin/bash

IAM_CLIENT_ID=cms-demo
IAM_CLIENT_SECRET=cms-demo
IAM_USER=

IAM_CLIENT_ID=${IAM_CLIENT_ID:-iam-client}
IAM_CLIENT_SECRET=${IAM_CLIENT_SECRET}

if [[ -z "${IAM_CLIENT_SECRET}" ]]; then
  echo "Please provide a client secret setting the IAM_CLIENT_SECRET env variable."
  exit 1;
fi

if [[ -z ${IAM_USER} ]]; then
  read -p "Username: " IAM_USER
fi

echo -ne "Password:"
read -s IAM_PASSWORD
echo

result=$(curl -s -L \
  -d client_id=${IAM_CLIENT_ID} \
  -d client_secret=${IAM_CLIENT_SECRET} \
  -d grant_type=password \
  -d username=${IAM_USER} \
  -d password=${IAM_PASSWORD} \
  -d scope="openid profile email offline_access" \
  ${IAM_ENDPOINT:-https://iam-test.indigo-datacloud.eu/token})

if [[ $? != 0 ]]; then
  echo "Error!"
  echo $result
  exit 1
fi

echo $result

access_token=$(echo $result | jq -r .access_token)

echo "export ORCHENT_TOKEN=\"${access_token}\""
