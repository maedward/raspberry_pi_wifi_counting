output=$(python check_connection.py 2>&1)
if [[ $output = "True" ]]; then
    echo "success"
else
    echo "failure: $output"
    curl -X POST --header "Content-Type:application/json" "$RESIN_SUPERVISOR_ADDRESS/v1/reboot?apikey=$RESIN_SUPERVISOR_API_KEY"
fi
