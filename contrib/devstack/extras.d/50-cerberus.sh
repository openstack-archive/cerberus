# cerberus.sh - Devstack extras script to install Cerberus

if is_service_enabled cerberus-api cerberus-agent; then
    if [[ "$1" == "source" ]]; then
        # Initial source
        source $TOP_DIR/lib/cerberus
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Cerberus"
        install_cerberus
        install_cerberusclient

        if is_service_enabled cerberus-dashboard; then
            install_cerberusdashboard
        fi
        cleanup_cerberus
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Cerberus"
        configure_cerberus
        if is_service_enabled cerberus-dashboard; then
            configure_cerberusdashboard
        fi
        if is_service_enabled key; then
            create_cerberus_accounts
        fi

    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        # Initialize cerberus
        echo_summary "Initializing Cerberus"
        init_cerberus

        # Start the Cerberus API and Cerberus agent components
        echo_summary "Starting Cerberus"
        start_cerberus
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_cerberus
    fi
fi
