#!/bin/sh
set -eu

CONNECT_URL="http://kafka-connect:8083"
CONNECTOR_NAME="postgres-orders-source"
CONFIG_FILE="/connectors/postgres-orders-source.json"

printf 'Waiting for Kafka Connect at %s\n' "$CONNECT_URL"
until curl -fsS "$CONNECT_URL/connectors" >/dev/null; do
  sleep 3
done

if curl -fsS "$CONNECT_URL/connectors/$CONNECTOR_NAME" >/dev/null 2>&1; then
  echo "Connector already exists"
  exit 0
fi

printf 'Creating connector %s\n' "$CONNECTOR_NAME"
HTTP_CODE=$(curl -s -o /tmp/connector-response.json -w "%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  --data @"$CONFIG_FILE" \
  "$CONNECT_URL/connectors")

cat /tmp/connector-response.json
printf '\nHTTP %s\n' "$HTTP_CODE"

case "$HTTP_CODE" in
  200|201|409)
    echo "Connector is ready"
    ;;
  *)
    echo "Connector registration failed"
    exit 1
    ;;
esac
