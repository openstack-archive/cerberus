#!/usr/bin/env/bash
# Plugin file for Cerberus security component
#--------------------------------------------
# Install and start **Cerberus** service


# Dependencies:
# - functions
# - OS_AUTH_URL for auth in api
# - DEST, HORIZON_DIR, DATA_DIR set to the destination directory
# - SERVICE_PASSWORD, SERVICE_TENANT_NAME for auth in api
# - IDENTITY_API_VERSION for the version of Keystone
# - STACK_USER service user


# Save trace setting
XTRACE=$(set +o | grep xtrace)
set +o xtrace


# Defaults
# --------

# Support potential entry-points console scripts
if [[ -d $CERBERUS_DIR/bin ]]; then
    CERBERUS_BIN_DIR=$CERBERUS_DIR/bin
else
    CERBERUS_BIN_DIR=$(get_python_exec_prefix)
fi


# Functions
# ---------

# create_cerberus_accounts() - Set up common required cerberus accounts

# Tenant               User       Roles
# ------------------------------------------------------------------
# service              cerberus   admin        # if enabled
function create_cerberus_accounts {

    SERVICE_TENANT=$(openstack project list | awk "/ $SERVICE_TENANT_NAME / { print \$2 }")
    ADMIN_ROLE=$(openstack role list | awk "/ admin / { print \$2 }")

    # Cerberus
    if [[ "$ENABLED_SERVICES" =~ "cerberus-api" ]]; then
        CERBERUS_USER=$(openstack user create \
            cerberus \
            --password "$SERVICE_PASSWORD" \
            --project $SERVICE_TENANT \
            --email cerberus@example.com \
            | grep " id " | get_field 2)
        openstack role add \
            $ADMIN_ROLE \
            --project $SERVICE_TENANT \
            --user $CERBERUS_USER
        if [[ "$KEYSTONE_CATALOG_BACKEND" = 'sql' ]]; then
            CERBERUS_SERVICE=$(openstack service create \
                cerberus \
                --type=security \
                --description="Security service" \
                | grep " id " | get_field 2)
            openstack endpoint create \
                $CERBERUS_SERVICE \
                --region RegionOne \
                --publicurl "$CERBERUS_SERVICE_PROTOCOL://$CERBERUS_SERVICE_HOSTPORT" \
                --adminurl "$CERBERUS_SERVICE_PROTOCOL://$CERBERUS_SERVICE_HOSTPORT" \
                --internalurl "$CERBERUS_SERVICE_PROTOCOL://$CERBERUS_SERVICE_HOSTPORT"
        fi
    fi
}


# Test if any Cerberus services are enabled
# is_cerberus_enabled
function is_cerberus_enabled {
    [[ ,${ENABLED_SERVICES} =~ ,"cerberus-" ]] && return 0
    return 1
}

# cleanup_cerberus() - Remove residual data files, anything left over from previous
# runs that a clean run would need to clean up
function cleanup_cerberus {
    # Clean up dirs
    rm -rf $CERBERUS_AUTH_CACHE_DIR/*
    rm -rf $CERBERUS_CONF_DIR/*
    if [[ "$ENABLED_SERVICES" =~ "cerberus-dashboard" ]]; then
        rm -f $HORIZON_DIR/openstack_dashboard/local/enabled/_50_cerberus.py
    fi
}

# configure_cerberus() - Set config files, create data dirs, etc
function configure_cerberus {
    setup_develop $CERBERUS_DIR

    sudo mkdir -m 755 -p $CERBERUS_CONF_DIR
    sudo chown $STACK_USER $CERBERUS_CONF_DIR

    sudo mkdir -m 755 -p $CERBERUS_API_LOG_DIR
    sudo chown $STACK_USER $CERBERUS_API_LOG_DIR

    cp $CERBERUS_DIR$CERBERUS_CONF.sample $CERBERUS_CONF
    cp $CERBERUS_DIR$CERBERUS_POLICY $CERBERUS_POLICY

    # Default
    iniset $CERBERUS_CONF DEFAULT verbose True
    iniset $CERBERUS_CONF DEFAULT debug "$ENABLE_DEBUG_LOG_LEVEL"
    iniset $CERBERUS_CONF DEFAULT sql_connection `database_connection_url cerberus`

    # auth
    iniset $CERBERUS_CONF keystone_authtoken auth_uri "$KEYSTONE_SERVICE_PROTOCOL://$KEYSTONE_SERVICE_HOST:5000/v2.0/"
    iniset $CERBERUS_CONF keystone_authtoken admin_user cerberus
    iniset $CERBERUS_CONF keystone_authtoken admin_password $SERVICE_PASSWORD
    iniset $CERBERUS_CONF keystone_authtoken admin_tenant_name $SERVICE_TENANT_NAME
    iniset $CERBERUS_CONF keystone_authtoken region $REGION_NAME
    iniset $CERBERUS_CONF keystone_authtoken auth_host $KEYSTONE_AUTH_HOST
    iniset $CERBERUS_CONF keystone_authtoken auth_protocol $KEYSTONE_AUTH_PROTOCOL
    iniset $CERBERUS_CONF keystone_authtoken auth_port $KEYSTONE_AUTH_PORT
    iniset $CERBERUS_CONF keystone_authtoken signing_dir $CERBERUS_AUTH_CACHE_DIR
}

# configure_cerberusdashboard()
function configure_cerberusdashboard {
    ln -s $CERBERUS_DASHBOARD_DIR/_cerberus.py.example $HORIZON_DIR/openstack_dashboard/local/enabled/_50_cerberus.py
}

# init_cerberus() - Initialize Cerberus database
function init_cerberus {
     # Delete existing cache
    sudo rm -rf $CERBERUS_AUTH_CACHE_DIR
    sudo mkdir -p $CERBERUS_AUTH_CACHE_DIR
    sudo chown $STACK_USER $CERBERUS_AUTH_CACHE_DIR

    # (Re)create cerberus database
    if is_service_enabled mysql postgresql; then
        recreate_database cerberus utf8
        $CERBERUS_BIN_DIR/cerberus-dbsync upgrade
    fi # Migrate cerberus database
}

# install_cerberus() - Collect source and prepare
function install_cerberus {
    git_clone $CERBERUS_REPO $CERBERUS_DIR $CERBERUS_BRANCH
    setup_develop $CERBERUS_DIR
}

# install_cerberusclient() - Collect source and prepare
function install_cerberusclient {
    git_clone $CERBERUS_CLIENT_REPO $CERBERUS_CLIENT_DIR $CERBERUS_CLIENT_BRANCH
    setup_develop $CERBERUS_CLIENT_DIR
}

# install_cerberusdashboard() - Collect source and prepare
function install_cerberusdashboard {
    git_clone $CERBERUS_DASHBOARD_REPO $CERBERUS_DASHBOARD_DIR $CERBERUS_DASHBOARD_BRANCH
    setup_develop $CERBERUS_DASHBOARD_DIR
}


# start_cerberus() - Start running processes, including screen
function start_cerberus {
    screen_it cerberus-agent "cd $CERBERUS_DIR; $CERBERUS_BIN_DIR/cerberus-agent --config-file=$CERBERUS_CONF"
    screen_it cerberus-api "cd $CERBERUS_DIR; $CERBERUS_BIN_DIR/cerberus-api --config-file=$CERBERUS_CONF"
    echo "Waiting for cerberus-api ($CERBERUS_SERVICE_HOST:$CERBERUS_SERVICE_PORT) to start..."
    if ! timeout $SERVICE_TIMEOUT sh -c "while ! curl --noproxy '*' -s http://$CERBERUS_SERVICE_HOST:$CERBERUS_SERVICE_PORT/v1/ >/dev/null; do sleep 1; done"; then
        die $LINENO "cerberus-api did not start"
    fi
}

# stop_cerberus() - Stop running processes
function stop_cerberus {
    # Kill the cerberus screen windows
    for serv in cerberus-api cerberus-agent; do
        screen_stop $serv
    done
}


# Main dispatcher
# ----------------

if is_service_enabled cerberus-api cerberus-agent; then
    if [[ "$1" == "stack" && "$2" == "install" ]]; then
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
        if is_service_enabled keystone; then
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


# Restore xtrace
$XTRACE

# Local variables:
# mode: shell-script
# End:
