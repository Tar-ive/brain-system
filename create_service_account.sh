#!/bin/bash
PROJECT=${1:-brain-gmail}
gcloud iam service-accounts create gmail-brain \
    --display-name="Gmail Brain Integration" \
    --project="$PROJECT"

gcloud iam service-accounts keys create \
    /Users/tarive/brain-poc/mcp-gmail/service-account.json \
    --iam-account="gmail-brain@${PROJECT}.iam.gserviceaccount.com"

echo "Service account created. However, note that service accounts"
echo "have limited Gmail access and may not work for personal email."
