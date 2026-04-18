#!/bin/sh
set -eu

CONNECT_URL="http://kafka-connect:8083/connectors"

printf 'Waiting for Kafka Connect...\n'
until curl -fsS "$CONNECT_URL" >/dev/null; do
  sleep 3
done

printf 'Registering Debezium PostgreSQL connector...\n'
HTTP_CODE=$(curl -s -o /tmp/connector-response.txt -w "%{http_code}" \
  -X POST "$CONNECT_URL" \
  -H 'Content-Type: application/json' \
  --data @/postgres-connector.json)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "409" ]; then
  printf 'Connector registration finished with HTTP %s\n' "$HTTP_CODE"
  cat /tmp/connector-response.txt
  exit 0
fi

printf 'Connector registration failed with HTTP %s\n' "$HTTP_CODE"
cat /tmp/connector-response.txt
exit 1
