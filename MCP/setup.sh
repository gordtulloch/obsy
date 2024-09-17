#!/bin/bash

#set -x  # command tracing
#set -o errexit  # replace by trapping ERR
#set -o nounset  # problems with python virtualenvs
shopt -s nullglob

PATH=/usr/bin:/bin
export PATH

#### config ####
INDI_DRIVER_PATH="/usr/bin"

INDISERVER_SERVICE_NAME="indiserver"
ALLSKY_SERVICE_NAME="obsy"
GUNICORN_SERVICE_NAME="gunicorn-obsy"

ALLSKY_ETC="/etc/obsy"

DB_FOLDER="/var/lib/obsy"
DB_FILE="${DB_FOLDER}/obsy.sqlite"
SQLALCHEMY_DATABASE_URI="sqlite:///${DB_FILE}"
MIGRATION_FOLDER="$DB_FOLDER/migrations"

# mysql support is not ready
USE_MYSQL_DATABASE="${OBSY_USE_MYSQL_DATABASE:-false}"

INSTALL_INDI="${OBSY_INSTALL_INDI:-true}"
INSTALL_INDISERVER="${OBSY_INSTALL_INDISERVER:-}"
INDI_VERSION="${OBSY_INDI_VERSION:-}"

HTTP_PORT="${OBSY_HTTP_PORT:-80}"
HTTPS_PORT="${OBSY_HTTPS_PORT:-443}"

OPTIONAL_PYTHON_MODULES="${OBSY_OPTIONAL_PYTHON_MODULES:-false}"
GPIO_PYTHON_MODULES="${OBSY_GPIO_PYTHON_MODULES:-false}"

PYINDI_2_0_4="git+https://github.com/indilib/pyindi-client.git@6f8fa80#egg=pyindi-client"
PYINDI_2_0_0="git+https://github.com/indilib/pyindi-client.git@674706f#egg=pyindi-client"
PYINDI_1_9_9="git+https://github.com/indilib/pyindi-client.git@ce808b7#egg=pyindi-client"
PYINDI_1_9_8="git+https://github.com/indilib/pyindi-client.git@ffd939b#egg=pyindi-client"

ASTROBERRY="false"
#### end config ####


function catch_error() {
    echo
    echo
    echo "###############"
    echo "###  ERROR  ###"
    echo "###############"
    echo
    echo "The setup script exited abnormally, please try to run again..."
    echo
    echo
    exit 1
}
trap catch_error ERR

function catch_sigint() {
    echo
    echo
    echo "###############"
    echo "###  ERROR  ###"
    echo "###############"
    echo
    echo "The setup script was interrupted, please run the script again to finish..."
    echo
    exit 1
}
trap catch_sigint SIGINT


if [ ! -f "/etc/os-release" ]; then
    echo
    echo "Unable to determine OS from /etc/os-release"
    echo
    exit 1
fi

source /etc/os-release


DISTRO_ID="${ID:-unknown}"
DISTRO_VERSION_ID="${VERSION_ID:-unknown}"
CPU_ARCH=$(uname -m)
CPU_BITS=$(getconf LONG_BIT)
CPU_TOTAL=$(grep -c "^proc" /proc/cpuinfo)
MEM_TOTAL=$(grep MemTotal /proc/meminfo | awk "{print \$2}")

# get primary group
PGRP=$(id -ng)


echo "###############################################"
echo "### Welcome to the obsy setup script        ###"
echo "###############################################"


if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo
    echo "Please do not run $(basename "$0") with a virtualenv active"
    echo "Run \"deactivate\" to exit your current virtualenv"
    echo
    echo
    exit 1
fi


if [ -f "/usr/local/bin/indiserver" ]; then
    # Do not install INDI
    INSTALL_INDI="false"
    INDI_DRIVER_PATH="/usr/local/bin"

    echo
    echo
    echo "Detected a custom installation of INDI in /usr/local/bin"
    echo
    echo
    sleep 3
fi


if [[ -f "/etc/astroberry.version" ]]; then
    echo
    echo
    echo "Detected Astroberry server"
    echo

    if which whiptail >/dev/null 2>&1; then
        if ! whiptail --title "WARNING" --msgbox "Astroberry is not supported.  Please use Raspbian or Ubuntu.\n\n" 0 0; then
            exit 1
        fi
    else
        echo
        echo "!!! WARNING !!!  Astroberry is not supported.  Please use Raspbian or Ubuntu."
        echo
        exit 1
    fi

if systemctl --user -q is-active "${ALLSKY_SERVICE_NAME}" >/dev/null 2>&1; then
    echo
    echo
    echo "ERROR: obsy is running.  Please stop the service before running this script."
    echo
    echo "    systemctl --user stop ${ALLSKY_SERVICE_NAME}"
    echo
    exit 1
fi


echo
echo
echo "Distribution: $DISTRO_ID"
echo "Release: $DISTRO_VERSION_ID"
echo "Arch: $CPU_ARCH"
echo "Bits: $CPU_BITS"
echo
echo "CPUs: $CPU_TOTAL"
echo "Memory: $MEM_TOTAL kB"
echo
echo "INDI_DRIVER_PATH: $INDI_DRIVER_PATH"
echo "INDISERVER_SERVICE_NAME: $INDISERVER_SERVICE_NAME"
echo "ALLSKY_SERVICE_NAME: $ALLSKY_SERVICE_NAME"
echo "GUNICORN_SERVICE_NAME: $GUNICORN_SERVICE_NAME"
echo "ALLSKY_ETC: $ALLSKY_ETC"
echo "HTDOCS_FOLDER: $HTDOCS_FOLDER"
echo "DB_FOLDER: $DB_FOLDER"
echo "DB_FILE: $DB_FILE"
echo "INSTALL_INDI: $INSTALL_INDI"
echo "HTTP_PORT: $HTTP_PORT"
echo "HTTPS_PORT: $HTTPS_PORT"
echo
echo

if [[ "$(id -u)" == "0" ]]; then
    echo "Please do not run $(basename "$0") as root"
    echo "Re-run this script as the user which will execute the obsy software"
    echo
    echo
    exit 1
fi

if ! ping -c 1 "$(hostname -s)" >/dev/null 2>&1; then
    echo "To avoid the benign warnings 'Name or service not known sudo: unable to resolve host'"
    echo "Add the following line to your /etc/hosts file:"
    echo "127.0.0.1       localhost $(hostname -s)"
    echo
    echo
fi

echo "Setup proceeding in 10 seconds... (control-c to cancel)"
echo
sleep 10


# Run sudo to ask for initial password
sudo true


START_TIME=$(date +%s)


echo
echo
echo "obsy supports the following camera interfaces."
echo
echo "Wiki:  https://github.com/aaronwmorris/obsy/wiki/Camera-Interfaces"
echo
echo "             indi: For astro/planetary cameras normally connected via USB (ZWO, QHY, PlayerOne, SVBony, Altair, Touptek, etc)"
echo "        libcamera: Supports cameras connected via CSI interface on Raspberry Pi SBCs (Raspi HQ Camera, Camera Module 3, etc)"
echo "    pycurl_camera: Download images from a remote web camera"
echo " indi_accumulator: Create synthetic exposures using multiple sub-exposures"
echo "     indi_passive: Connect a second instance of obsy to an existing obsy indiserver"
echo

# whiptail might not be installed yet
while [ -z "${CAMERA_INTERFACE:-}" ]; do
    PS3="Select a camera interface: "
    select camera_interface in indi libcamera pycurl_camera indi_accumulator indi_passive ; do
        if [ -n "$camera_interface" ]; then
            CAMERA_INTERFACE="$camera_interface"
            break
        fi
    done


    # more specific libcamera selection
    if [ "$CAMERA_INTERFACE" == "libcamera" ]; then
        INSTALL_LIBCAMERA="true"

        echo
        PS3="Select a libcamera interface: "
        select libcamera_interface in libcamera_imx477 libcamera_imx378 libcamera_ov5647 libcamera_imx219 libcamera_imx519 libcamera_imx708 libcamera_imx296_gs libcamera_imx290 libcamera_imx462 libcamera_imx327 libcamera_imx298 libcamera_64mp_hawkeye libcamera_64mp_owlsight; do
            if [ -n "$libcamera_interface" ]; then
                # overwrite variable
                CAMERA_INTERFACE="$libcamera_interface"
                break
            fi
        done
    fi
done


if [[ -f "/usr/local/bin/libcamera-still" || -f "/usr/local/bin/rpicam-still" ]]; then
    INSTALL_LIBCAMERA="false"

    echo
    echo
    echo "Detected a custom installation of libcamera in /usr/local"
    echo
    echo
    sleep 3
fi


echo
echo
echo "Fixing git checkout permissions"
sudo find "$(dirname "$0")" ! -user "$USER" -exec chown "$USER" {} \;
sudo find "$(dirname "$0")" -type d ! -perm -555 -exec chmod ugo+rx {} \;
sudo find "$(dirname "$0")" -type f ! -perm -444 -exec chmod ugo+r {} \;



echo "**** Installing packages... ****"
if [[ "$DISTRO_ID" == "raspbian" && "$DISTRO_VERSION_ID" == "12" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

    if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
        sudo apt-get -y install \
            rpicam-apps
    fi

elif [[ "$DISTRO_ID" == "debian" && "$DISTRO_VERSION_ID" == "12" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

    if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
        sudo apt-get -y install \
            rpicam-apps
    fi

elif [[ "$DISTRO_ID" == "raspbian" && "$DISTRO_VERSION_ID" == "11" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

    if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
        sudo apt-get -y install \
            libcamera-apps
    fi

elif [[ "$DISTRO_ID" == "debian" && "$DISTRO_VERSION_ID" == "11" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi


    if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
        # this can fail on armbian debian based repos
        sudo apt-get -y install \
            libcamera-apps || true
    fi

elif [[ "$DISTRO_ID" == "raspbian" && "$DISTRO_VERSION_ID" == "10" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    VIRTUALENV_REQ=requirements/requirements_debian10.txt
    VIRTUALENV_REQ_POST=requirements/requirements_empty.txt


    if [[ "$CAMERA_INTERFACE" =~ ^libcamera ]]; then
        echo
        echo
        echo "libcamera is not supported in this distribution"
        exit 1
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg62-turbo-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            indi-rpicam \
            libindi-dev \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

    if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
        sudo apt-get -y install \
            libcamera-apps
    fi

elif [[ "$DISTRO_ID" == "debian" && "$DISTRO_VERSION_ID" == "10" ]]; then
    RSYSLOG_USER=root
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3

    VIRTUALENV_REQ=requirements/requirements_debian10.txt
    VIRTUALENV_REQ_POST=requirements/requirements_empty.txt


    if [[ "$CAMERA_INTERFACE" =~ ^libcamera ]]; then
        echo
        echo
        echo "libcamera is not supported in this distribution"
        exit 1
    fi


    INSTALL_INDI="false"

    if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
        echo
        echo
        echo "There are not prebuilt indi packages for this distribution"
        echo "Please run ./misc/build_indi.sh before running setup.sh"
        echo
        echo
        exit 1
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-rpicam \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-sv305 \
            libsv305 \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

elif [[ "$DISTRO_ID" == "ubuntu" && "$DISTRO_VERSION_ID" == "24.04" ]]; then
    RSYSLOG_USER=syslog
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"


    # Use Python 3.11 due to problems with Python 3.12 and pyindi-client
    # https://github.com/indilib/pyindi-client/issues/46
    sudo add-apt-repository -y ppa:deadsnakes/ppa

    PYTHON_BIN=python3.11


    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    if [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "armv7l" || "$CPU_ARCH" == "armv6l" ]]; then
        INSTALL_INDI="false"

        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            echo
            echo
            echo "There are not prebuilt indi packages for this distribution"
            echo "Please run ./misc/build_indi.sh before running setup.sh"
            echo
            echo
            exit 1
        fi
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg8-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-svbony \
            libsvbony \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi


    #if [[ "$INSTALL_LIBCAMERA" == "true" ]]; then
    #    sudo apt-get -y install \
    #        rpicam-apps
    #fi


elif [[ "$DISTRO_ID" == "ubuntu" && "$DISTRO_VERSION_ID" == "22.04" ]]; then
    RSYSLOG_USER=syslog
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3.11

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "armv6l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_armv6l.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    if [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "armv7l" || "$CPU_ARCH" == "armv6l" ]]; then
        INSTALL_INDI="false"

        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            echo
            echo
            echo "There are not prebuilt indi packages for this distribution"
            echo "Please run ./misc/build_indi.sh before running setup.sh"
            echo
            echo
            exit 1
        fi
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg8-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-svbony \
            libsvbony \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi


elif [[ "$DISTRO_ID" == "ubuntu" && "$DISTRO_VERSION_ID" == "20.04" ]]; then
    RSYSLOG_USER=syslog
    RSYSLOG_GROUP=adm

    MYSQL_ETC="/etc/mysql"

    PYTHON_BIN=python3.9

    if [ "$CPU_ARCH" == "armv7l" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [ "$CPU_ARCH" == "i686" ]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    elif [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "32" ]]; then
        VIRTUALENV_REQ=requirements/requirements_latest_32.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_latest_32_post.txt
    else
        VIRTUALENV_REQ=requirements/requirements_latest.txt
        VIRTUALENV_REQ_OPT=requirements/requirements_optional.txt
        VIRTUALENV_REQ_POST=requirements/requirements_empty.txt
    fi


    if [[ "$CPU_ARCH" == "x86_64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "aarch64" && "$CPU_BITS" == "64" ]]; then
        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            sudo add-apt-repository -y ppa:mutlaqja/ppa
        fi
    elif [[ "$CPU_ARCH" == "armv7l" || "$CPU_ARCH" == "armv6l" ]]; then
        INSTALL_INDI="false"

        if [[ ! -f "${INDI_DRIVER_PATH}/indiserver" && ! -f "/usr/local/bin/indiserver" ]]; then
            echo
            echo
            echo "There are not prebuilt indi packages for this distribution"
            echo "Please run ./misc/build_indi.sh before running setup.sh"
            echo
            echo
            exit 1
        fi
    fi


    sudo apt-get update
    sudo apt-get -y install \
        build-essential \
        python3.9 \
        python3.9-dev \
        python3.9-venv \
        python3 \
        python3-dev \
        python3-venv \
        python3-pip \
        virtualenv \
        cmake \
        gfortran \
        whiptail \
        bc \
        procps \
        rsyslog \
        cron \
        git \
        cpio \
        tzdata \
        ca-certificates \
        avahi-daemon \
        apache2 \
        swig \
        libatlas-base-dev \
        libilmbase-dev \
        libopenexr-dev \
        libgtk-3-0 \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        libgnutls28-dev \
        libcurl4-gnutls-dev \
        libcfitsio-dev \
        libnova-dev \
        libdbus-1-dev \
        libglib2.0-dev \
        libffi-dev \
        libopencv-dev \
        libopenblas-dev \
        libraw-dev \
        libgeos-dev \
        libtiff5-dev \
        libjpeg8-dev \
        libopenjp2-7-dev \
        libpng-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        libcap-dev \
        tcl8.6-dev \
        tk8.6-dev \
        python3-tk \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        default-libmysqlclient-dev \
        pkg-config \
        rustc \
        cargo \
        ffmpeg \
        gifsicle \
        jq \
        sqlite3 \
        libgpiod2 \
        i2c-tools \
        policykit-1 \
        dbus-user-session


    if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
        sudo apt-get -y install \
            mariadb-server
    fi


    if [[ "$INSTALL_INDI" == "true" && -f "/usr/bin/indiserver" ]]; then
        if ! whiptail --title "indi software update" --yesno "INDI is already installed, would you like to upgrade the software?" 0 0 --defaultno; then
            INSTALL_INDI="false"
        fi
    fi

    if [[ "$INSTALL_INDI" == "true" ]]; then
        sudo apt-get -y install \
            indi-full \
            libindi-dev \
            indi-webcam \
            indi-asi \
            libasi \
            indi-qhy \
            libqhy \
            indi-playerone \
            libplayerone \
            indi-svbony \
            libsvbony \
            libaltaircam \
            libmallincam \
            libmicam \
            libnncam \
            indi-toupbase \
            libtoupcam \
            indi-gphoto \
            indi-sx \
            indi-gpsd \
            indi-gpsnmea
    fi

else
    echo "Unknown distribution $DISTRO_ID $DISTRO_VERSION_ID ($CPU_ARCH)"
    exit 1
fi

VIRTUALENV_REQ_GPIO=requirements/requirements_gpio.txt


if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    echo
    echo
    echo "The DBUS user session is not defined"
    echo
    echo "Now that the dbus package has been installed..."
    echo "Please reboot your system and re-run this script to continue"
    echo
    echo "WARNING: If you use screen, tmux, or byobu for virtual sessions, this check may always fail"
    echo
    exit 1
fi


if systemctl -q is-enabled "${INDISERVER_SERVICE_NAME}" 2>/dev/null; then
    # system
    INSTALL_INDISERVER="false"
elif systemctl --user -q is-enabled "${INDISERVER_SERVICE_NAME}" 2>/dev/null; then
    while [ -z "${INSTALL_INDISERVER:-}" ]; do
        # user
        if whiptail --title "indiserver update" --yesno "An indiserver service is already defined, would you like to replace it?" 0 0 --defaultno; then
            INSTALL_INDISERVER="true"
        else
            INSTALL_INDISERVER="false"
        fi
    done
else
    INSTALL_INDISERVER="true"
fi


# find script directory for service setup
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || catch_error
ALLSKY_DIRECTORY=$PWD
cd "$OLDPWD" || catch_error


echo "**** Ensure path to git folder is traversable ****"
# Web servers running as www-data or nobody need to be able to read files in the git checkout
PARENT_DIR="$ALLSKY_DIRECTORY"
while true; do
    if [ "$PARENT_DIR" == "/" ]; then
        break
    elif [ "$PARENT_DIR" == "." ]; then
        break
    fi

    echo "Setting other execute bit on $PARENT_DIR"
    sudo chmod ugo+x "$PARENT_DIR"

    PARENT_DIR=$(dirname "$PARENT_DIR")
done


echo "**** Python virtualenv setup ****"
[[ ! -d "${ALLSKY_DIRECTORY}/virtualenv" ]] && mkdir "${ALLSKY_DIRECTORY}/virtualenv"
chmod 775 "${ALLSKY_DIRECTORY}/virtualenv"
if [ ! -d "${ALLSKY_DIRECTORY}/virtualenv/obsy" ]; then
    "${PYTHON_BIN}" -m venv "${ALLSKY_DIRECTORY}/virtualenv/obsy"
fi


if whiptail --title "Optional Python Modules" --yesno "Would you like to install optional python modules? (Additional database, object storage support)" 0 0 --defaultno; then
    OPTIONAL_PYTHON_MODULES=true
fi

if whiptail --title "GPIO Python Modules" --yesno "Would you like to install GPIO python modules? (Hardware device support)" 0 0 --defaultno; then
    GPIO_PYTHON_MODULES=true
fi

# shellcheck source=/dev/null
source "${ALLSKY_DIRECTORY}/virtualenv/obsy/bin/activate"

pip3 install --upgrade pip setuptools wheel


PIP_REQ_ARGS=("-r" "${ALLSKY_DIRECTORY}/${VIRTUALENV_REQ}")

if [ "${OPTIONAL_PYTHON_MODULES}" == "true" ]; then
    PIP_REQ_ARGS+=("-r" "${ALLSKY_DIRECTORY}/${VIRTUALENV_REQ_OPT}")
fi

if [ "${GPIO_PYTHON_MODULES}" == "true" ]; then
    PIP_REQ_ARGS+=("-r" "${ALLSKY_DIRECTORY}/${VIRTUALENV_REQ_GPIO}")
fi

pip3 install "${PIP_REQ_ARGS[@]}"


# some modules do not have their prerequisites set
pip3 install -r "${ALLSKY_DIRECTORY}/${VIRTUALENV_REQ_POST}"



# pyindi-client setup
SUPPORTED_INDI_VERSIONS=(
    "2.0.9"
    "2.0.8"
    "2.0.7"
    "2.0.6"
    "2.0.5"
    "2.0.4"
    "2.0.3"
    "2.0.2"
    "2.0.1"
    "2.0.0"
    "1.9.9"
    "1.9.8"
    "1.9.7"
    "skip"
)


# try to detect installed indiversion
#DETECTED_INDIVERSION=$(${INDI_DRIVER_PATH}/indiserver --help 2>&1 | grep -i "INDI Library" | awk "{print \$3}")
DETECTED_INDIVERSION=$(pkg-config --modversion libindi)
echo
echo
echo "Detected INDI version: $DETECTED_INDIVERSION"
sleep 3


if [ "$DETECTED_INDIVERSION" == "2.0.4" ]; then
    whiptail --msgbox "There is a bug in INDI 2.0.4 that will cause the build for pyindi-client to fail.\nThe following URL documents the needed fix.\n\nhttps://github.com/aaronwmorris/obsy/wiki/INDI-2.0.4-bug" 0 0 --title "WARNING"
fi


INDI_VERSIONS=()
for v in "${SUPPORTED_INDI_VERSIONS[@]}"; do
    if [ "$v" == "$DETECTED_INDIVERSION" ]; then
        #INDI_VERSIONS[${#INDI_VERSIONS[@]}]="$v $v ON"

        INDI_VERSION=$v
        break
    else
        INDI_VERSIONS[${#INDI_VERSIONS[@]}]="$v $v OFF"
    fi
done



while [ -z "${INDI_VERSION:-}" ]; do
    # shellcheck disable=SC2068
    INDI_VERSION=$(whiptail --title "Installed INDI Version for pyindi-client" --nocancel --notags --radiolist "Press space to select" 0 0 0 ${INDI_VERSIONS[@]} 3>&1 1>&2 2>&3)
done

#echo "Selected: $INDI_VERSION"



if [ "$INDI_VERSION" == "2.0.9" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.8" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.7" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.6" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.5" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.4" ]; then
    pip3 install "$PYINDI_2_0_4"
elif [ "$INDI_VERSION" == "2.0.3" ]; then
    pip3 install "$PYINDI_2_0_0"
elif [ "$INDI_VERSION" == "2.0.2" ]; then
    pip3 install "$PYINDI_2_0_0"
elif [ "$INDI_VERSION" == "2.0.1" ]; then
    pip3 install "$PYINDI_2_0_0"
elif [ "$INDI_VERSION" == "2.0.0" ]; then
    pip3 install "$PYINDI_2_0_0"
elif [ "$INDI_VERSION" == "1.9.9" ]; then
    pip3 install "$PYINDI_1_9_9"
elif [ "$INDI_VERSION" == "1.9.8" ]; then
    pip3 install "$PYINDI_1_9_8"
elif [ "$INDI_VERSION" == "1.9.7" ]; then
    pip3 install "$PYINDI_1_9_8"
else
    # assuming skip
    echo "Skipping pyindi-client install"
fi



# get list of ccd drivers
INDI_CCD_DRIVERS=()
cd "$INDI_DRIVER_PATH" || catch_error
for I in indi_*_ccd indi_rpicam* indi_pylibcamera*; do
    INDI_CCD_DRIVERS[${#INDI_CCD_DRIVERS[@]}]="$I $I OFF"
done
cd "$OLDPWD" || catch_error

#echo ${INDI_CCD_DRIVERS[@]}


if [[ "$CAMERA_INTERFACE" == "indi" && "$INSTALL_INDISERVER" == "true" ]]; then
    while [ -z "${CCD_DRIVER:-}" ]; do
        # shellcheck disable=SC2068
        CCD_DRIVER=$(whiptail --title "Camera Driver" --nocancel --notags --radiolist "Press space to select" 0 0 0 ${INDI_CCD_DRIVERS[@]} 3>&1 1>&2 2>&3)
    done
else
    # simulator will not affect anything
    CCD_DRIVER=indi_simulator_ccd
fi

#echo $CCD_DRIVER



# get list of gps drivers
INDI_GPS_DRIVERS=("None None ON")
cd "$INDI_DRIVER_PATH" || catch_error
for I in indi_gps* indi_simulator_gps; do
    INDI_GPS_DRIVERS[${#INDI_GPS_DRIVERS[@]}]="$I $I OFF"
done
cd "$OLDPWD" || catch_error

#echo ${INDI_GPS_DRIVERS[@]}


if [[ "$INSTALL_INDISERVER" == "true" ]]; then
    while [ -z "${GPS_DRIVER:-}" ]; do
        # shellcheck disable=SC2068
        GPS_DRIVER=$(whiptail --title "GPS Driver" --nocancel --notags --radiolist "Press space to select" 0 0 0 ${INDI_GPS_DRIVERS[@]} 3>&1 1>&2 2>&3)
    done
fi

#echo $GPS_DRIVER

if [ "$GPS_DRIVER" == "None" ]; then
    # Value needs to be empty for None
    GPS_DRIVER=""
fi



# create users systemd folder
[[ ! -d "${HOME}/.config/systemd/user" ]] && mkdir -p "${HOME}/.config/systemd/user"


if [ "$INSTALL_INDISERVER" == "true" ]; then
    echo
    echo
    echo "**** Setting up indiserver service ****"
    TMP1=$(mktemp)
    sed \
     -e "s|%INDI_DRIVER_PATH%|$INDI_DRIVER_PATH|g" \
     -e "s|%ALLSKY_DIRECTORY%|$ALLSKY_DIRECTORY|g" \
     -e "s|%INDISERVER_USER%|$USER|g" \
     -e "s|%INDI_CCD_DRIVER%|$CCD_DRIVER|g" \
     -e "s|%INDI_GPS_DRIVER%|$GPS_DRIVER|g" \
     "${ALLSKY_DIRECTORY}/service/indiserver.service" > "$TMP1"


    cp -f "$TMP1" "${HOME}/.config/systemd/user/${INDISERVER_SERVICE_NAME}.service"
    chmod 644 "${HOME}/.config/systemd/user/${INDISERVER_SERVICE_NAME}.service"
    [[ -f "$TMP1" ]] && rm -f "$TMP1"
else
    echo
    echo
    echo
    echo "! Bypassing indiserver setup"
fi


echo "**** Setting up obsy service ****"
# timer
cp -f "${ALLSKY_DIRECTORY}/service/${ALLSKY_SERVICE_NAME}.timer" "${HOME}/.config/systemd/user/${ALLSKY_SERVICE_NAME}.timer"
chmod 644 "${HOME}/.config/systemd/user/${ALLSKY_SERVICE_NAME}.timer"


TMP2=$(mktemp)
sed \
 -e "s|%ALLSKY_USER%|$USER|g" \
 -e "s|%ALLSKY_DIRECTORY%|$ALLSKY_DIRECTORY|g" \
 -e "s|%ALLSKY_ETC%|$ALLSKY_ETC|g" \
 "${ALLSKY_DIRECTORY}/service/obsy.service" > "$TMP2"

cp -f "$TMP2" "${HOME}/.config/systemd/user/${ALLSKY_SERVICE_NAME}.service"
chmod 644 "${HOME}/.config/systemd/user/${ALLSKY_SERVICE_NAME}.service"
[[ -f "$TMP2" ]] && rm -f "$TMP2"


echo "**** Setting up gunicorn service ****"
TMP5=$(mktemp)
sed \
 -e "s|%DB_FOLDER%|$DB_FOLDER|g" \
 -e "s|%ALLSKY_ETC%|$ALLSKY_ETC|g" \
 -e "s|%GUNICORN_SERVICE_NAME%|$GUNICORN_SERVICE_NAME|g" \
 "${ALLSKY_DIRECTORY}/service/gunicorn-obsy.socket" > "$TMP5"

cp -f "$TMP5" "${HOME}/.config/systemd/user/${GUNICORN_SERVICE_NAME}.socket"
chmod 644 "${HOME}/.config/systemd/user/${GUNICORN_SERVICE_NAME}.socket"
[[ -f "$TMP5" ]] && rm -f "$TMP5"

TMP6=$(mktemp)
sed \
 -e "s|%ALLSKY_USER%|$USER|g" \
 -e "s|%ALLSKY_DIRECTORY%|$ALLSKY_DIRECTORY|g" \
 -e "s|%GUNICORN_SERVICE_NAME%|$GUNICORN_SERVICE_NAME|g" \
 -e "s|%ALLSKY_ETC%|$ALLSKY_ETC|g" \
 "${ALLSKY_DIRECTORY}/service/gunicorn-obsy.service" > "$TMP6"

cp -f "$TMP6" "${HOME}/.config/systemd/user/${GUNICORN_SERVICE_NAME}.service"
chmod 644 "${HOME}/.config/systemd/user/${GUNICORN_SERVICE_NAME}.service"
[[ -f "$TMP6" ]] && rm -f "$TMP6"


echo "**** Enabling services ****"
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload

# obsy service is started by the timer (2 minutes after boot)
systemctl --user disable ${ALLSKY_SERVICE_NAME}.service
systemctl --user enable ${ALLSKY_SERVICE_NAME}.timer

# gunicorn service is started by the socket
systemctl --user disable ${GUNICORN_SERVICE_NAME}.service
systemctl --user enable ${GUNICORN_SERVICE_NAME}.socket

if [ "$INSTALL_INDISERVER" == "true" ]; then
    systemctl --user enable ${INDISERVER_SERVICE_NAME}.service
fi


echo "**** Setup policy kit permissions ****"
TMP_POLKIT=$(mktemp)

if [ -d "/etc/polkit-1/rules.d" ]; then
    sed \
     -e "s|%ALLSKY_USER%|$USER|g" \
     "${ALLSKY_DIRECTORY}/service/90-obsy.rules" > "$TMP_POLKIT"

    sudo cp -f "$TMP_POLKIT" "/etc/polkit-1/rules.d/90-obsy.rules"
    sudo chown root:root "/etc/polkit-1/rules.d/90-obsy.rules"
    sudo chmod 644 "/etc/polkit-1/rules.d/90-obsy.rules"

    # remove legacy config
    if sudo test -f "/etc/polkit-1/localauthority/50-local.d/90-org.aaronwmorris.obsy.pkla"; then
        sudo rm -f "/etc/polkit-1/localauthority/50-local.d/90-org.aaronwmorris.obsy.pkla"
    fi
else
    # legacy pkla
    sed \
     -e "s|%ALLSKY_USER%|$USER|g" \
     "${ALLSKY_DIRECTORY}/service/90-org.aaronwmorris.obsy.pkla" > "$TMP_POLKIT"

    sudo cp -f "$TMP_POLKIT" "/etc/polkit-1/localauthority/50-local.d/90-org.aaronwmorris.obsy.pkla"
    sudo chown root:root "/etc/polkit-1/localauthority/50-local.d/90-org.aaronwmorris.obsy.pkla"
    sudo chmod 644 "/etc/polkit-1/localauthority/50-local.d/90-org.aaronwmorris.obsy.pkla"
fi

[[ -f "$TMP_POLKIT" ]] && rm -f "$TMP_POLKIT"


echo "**** Ensure user is a member of the systemd-journal group ****"
sudo usermod -a -G systemd-journal "$USER"


echo "**** Setup rsyslog logging ****"
[[ ! -d "/var/log/obsy" ]] && sudo mkdir /var/log/obsy
sudo chmod 755 /var/log/obsy
sudo touch /var/log/obsy/obsy.log
sudo chmod 644 /var/log/obsy/obsy.log
sudo touch /var/log/obsy/webapp-obsy.log
sudo chmod 644 /var/log/obsy/webapp-obsy.log
sudo chown -R $RSYSLOG_USER:$RSYSLOG_GROUP /var/log/obsy


# 10 prefix so they are process before the defaults in 50
sudo cp -f "${ALLSKY_DIRECTORY}/log/rsyslog_obsy.conf" /etc/rsyslog.d/10-obsy.conf
sudo chown root:root /etc/rsyslog.d/10-obsy.conf
sudo chmod 644 /etc/rsyslog.d/10-obsy.conf

# remove old version
[[ -f "/etc/rsyslog.d/obsy.conf" ]] && sudo rm -f /etc/rsyslog.d/obsy.conf

sudo systemctl restart rsyslog


sudo cp -f "${ALLSKY_DIRECTORY}/log/logrotate_obsy" /etc/logrotate.d/obsy
sudo chown root:root /etc/logrotate.d/obsy
sudo chmod 644 /etc/logrotate.d/obsy


echo "**** obsy config ****"
[[ ! -d "$ALLSKY_ETC" ]] && sudo mkdir "$ALLSKY_ETC"
sudo chown -R "$USER":"$PGRP" "$ALLSKY_ETC"
sudo chmod 775 "${ALLSKY_ETC}"

touch "${ALLSKY_ETC}/obsy.env"
chmod 600 "${ALLSKY_ETC}/obsy.env"


echo "**** Flask config ****"

while [ -z "${FLASK_AUTH_ALL_VIEWS:-}" ]; do
    if whiptail --title "Web Authentication" --yesno "Do you want to require authentication for all web site views?\n\nIf \"no\", privileged actions are still protected by authentication." 0 0 --defaultno; then
        FLASK_AUTH_ALL_VIEWS="true"
    else
        FLASK_AUTH_ALL_VIEWS="false"
    fi
done


TMP_FLASK=$(mktemp --suffix=.json)
TMP_FLASK_MERGE=$(mktemp --suffix=.json)


jq \
 --arg sqlalchemy_database_uri "$SQLALCHEMY_DATABASE_URI" \
 --arg indi_allsky_docroot "$HTDOCS_FOLDER" \
 --argjson indi_allsky_auth_all_views "$FLASK_AUTH_ALL_VIEWS" \
 --arg migration_folder "$MIGRATION_FOLDER" \
 --arg allsky_service_name "${ALLSKY_SERVICE_NAME}.service" \
 --arg allsky_timer_name "${ALLSKY_SERVICE_NAME}.timer" \
 --arg indiserver_service_name "${INDISERVER_SERVICE_NAME}.service" \
 --arg indiserver_timer_name "${INDISERVER_SERVICE_NAME}.timer" \
 --arg gunicorn_service_name "${GUNICORN_SERVICE_NAME}.service" \
 '.SQLALCHEMY_DATABASE_URI = $sqlalchemy_database_uri | .INDI_ALLSKY_DOCROOT = $indi_allsky_docroot | .INDI_ALLSKY_AUTH_ALL_VIEWS = $indi_allsky_auth_all_views | .MIGRATION_FOLDER = $migration_folder | .ALLSKY_SERVICE_NAME = $allsky_service_name | .ALLSKY_TIMER_NAME = $allsky_timer_name | .INDISERVER_SERVICE_NAME = $indiserver_service_name | .INDISERVER_TIMER_NAME = $indiserver_timer_name | .GUNICORN_SERVICE_NAME = $gunicorn_service_name' \
 "${ALLSKY_DIRECTORY}/flask.json_template" > "$TMP_FLASK"


if [[ -f "${ALLSKY_ETC}/flask.json" ]]; then
    # make a backup
    cp -f "${ALLSKY_ETC}/flask.json" "${ALLSKY_ETC}/flask.json_old"
    chmod 640 "${ALLSKY_ETC}/flask.json_old"

    # attempt to merge configs giving preference to the original config (listed 2nd)
    jq -s '.[0] * .[1]' "$TMP_FLASK" "${ALLSKY_ETC}/flask.json" > "$TMP_FLASK_MERGE"
    cp -f "$TMP_FLASK_MERGE" "${ALLSKY_ETC}/flask.json"
else
    # new config
    cp -f "$TMP_FLASK" "${ALLSKY_ETC}/flask.json"
fi


OBSY_FLASK_SECRET_KEY=$(jq -r '.SECRET_KEY' "${ALLSKY_ETC}/flask.json")
if [[ -z "$OBSY_FLASK_SECRET_KEY" || "$OBSY_FLASK_SECRET_KEY" == "CHANGEME" ]]; then
    # generate flask secret key
    OBSY_FLASK_SECRET_KEY=$(${PYTHON_BIN} -c 'import secrets; print(secrets.token_hex())')

    TMP_FLASK_SKEY=$(mktemp --suffix=.json)
    jq --arg secret_key "$OBSY_FLASK_SECRET_KEY" '.SECRET_KEY = $secret_key' "${ALLSKY_ETC}/flask.json" > "$TMP_FLASK_SKEY"
    cp -f "$TMP_FLASK_SKEY" "${ALLSKY_ETC}/flask.json"
    [[ -f "$TMP_FLASK_SKEY" ]] && rm -f "$TMP_FLASK_SKEY"
fi


OBSY_FLASK_PASSWORD_KEY=$(jq -r '.PASSWORD_KEY' "${ALLSKY_ETC}/flask.json")
if [[ -z "$OBSY_FLASK_PASSWORD_KEY" || "$OBSY_FLASK_PASSWORD_KEY" == "CHANGEME" ]]; then
    # generate password key for encryption
    OBSY_FLASK_PASSWORD_KEY=$(${PYTHON_BIN} -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')

    TMP_FLASK_PKEY=$(mktemp --suffix=.json)
    jq --arg password_key "$OBSY_FLASK_PASSWORD_KEY" '.PASSWORD_KEY = $password_key' "${ALLSKY_ETC}/flask.json" > "$TMP_FLASK_PKEY"
    cp -f "$TMP_FLASK_PKEY" "${ALLSKY_ETC}/flask.json"
    [[ -f "$TMP_FLASK_PKEY" ]] && rm -f "$TMP_FLASK_PKEY"
fi


sudo chown "$USER":"$PGRP" "${ALLSKY_ETC}/flask.json"
sudo chmod 660 "${ALLSKY_ETC}/flask.json"

[[ -f "$TMP_FLASK" ]] && rm -f "$TMP_FLASK"
[[ -f "$TMP_FLASK_MERGE" ]] && rm -f "$TMP_FLASK_MERGE"



# create a backup of the key
if [ ! -f "${ALLSKY_ETC}/password_key_backup.json" ]; then
    jq -n --arg password_key "$OBSY_PASSWORD_KEY" '.PASSWORD_KEY_BACKUP = $password_key' '{}' > "${ALLSKY_ETC}/password_key_backup.json"
fi

chmod 400 "${ALLSKY_ETC}/password_key_backup.json"



echo "**** Setup DB ****"
[[ ! -d "$DB_FOLDER" ]] && sudo mkdir "$DB_FOLDER"
sudo chmod 775 "$DB_FOLDER"
sudo chown -R "$USER":"$PGRP" "$DB_FOLDER"
[[ ! -d "${DB_FOLDER}/backup" ]] && sudo mkdir "${DB_FOLDER}/backup"
sudo chmod 775 "$DB_FOLDER/backup"
sudo chown "$USER":"$PGRP" "${DB_FOLDER}/backup"
if [[ -f "${DB_FILE}" ]]; then
    sudo chmod 664 "${DB_FILE}"
    sudo chown "$USER":"$PGRP" "${DB_FILE}"

    echo "**** Backup DB prior to migration ****"
    DB_BACKUP="${DB_FOLDER}/backup/backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    sqlite3 "${DB_FILE}" .dump | gzip -c > "$DB_BACKUP"

    chmod 640 "$DB_BACKUP"

    echo "**** Vacuum DB ****"
    sqlite3 "${DB_FILE}" "VACUUM;"
fi


# Setup migration folder
if [[ ! -d "$MIGRATION_FOLDER" ]]; then
    # Folder defined in flask config
    flask db init

    # Move migrations out of git checkout
    cd "${ALLSKY_DIRECTORY}/migrations/versions" || catch_error
    find . -type f -name "*.py" | cpio -pdmu "${MIGRATION_FOLDER}/versions"
    cd "$OLDPWD" || catch_error

    # Cleanup old files
    find "${ALLSKY_DIRECTORY}/migrations/versions" -type f -name "*.py" -exec rm -f {} \;
fi


flask db revision --autogenerate
flask db upgrade head


sudo chmod 664 "${DB_FILE}"
sudo chown "$USER":"$PGRP" "${DB_FILE}"


# some schema changes require data to be populated
echo "**** Populate database fields ****"
"${ALLSKY_DIRECTORY}/misc/populate_data.py"


if [ -f "${ALLSKY_ETC}/config.json" ]; then
    echo
    echo
    echo "Configurations are now being stored in the database"
    echo "This script will move your existing configuration into"
    echo "the database."
    echo
    sleep 5

    "${ALLSKY_DIRECTORY}/config.py" load -c "${ALLSKY_ETC}/config.json"

    mv -f "${ALLSKY_ETC}/config.json" "${ALLSKY_ETC}/legacy_config.json"

    # Move old backup config
    if [ -f "${ALLSKY_ETC}/config.json_old" ]; then
        mv -f "${ALLSKY_ETC}/config.json_old" "${ALLSKY_ETC}/legacy_config.json_old"
    fi
fi


### Mysql
if [[ "$USE_MYSQL_DATABASE" == "true" ]]; then
    sudo cp -f "${ALLSKY_DIRECTORY}/service/mysql_obsy.conf" "$MYSQL_ETC/mariadb.conf.d/90-mysql_obsy.conf"
    sudo chown root:root "$MYSQL_ETC/mariadb.conf.d/90-mysql_obsy.conf"
    sudo chmod 644 "$MYSQL_ETC/mariadb.conf.d/90-mysql_obsy.conf"

    if [[ ! -d "$MYSQL_ETC/ssl" ]]; then
        sudo mkdir "$MYSQL_ETC/ssl"
    fi

    sudo chown root:root "$MYSQL_ETC/ssl"
    sudo chmod 755 "$MYSQL_ETC/ssl"


    if [[ ! -f "$MYSQL_ETC/ssl/obsy_mysql.key" || ! -f "$MYSQL_ETC/ssl/obsy_mysq.pem" ]]; then
        sudo rm -f "$MYSQL_ETC/ssl/obsy_mysql.key"
        sudo rm -f "$MYSQL_ETC/ssl/obsy_mysql.pem"

        SHORT_HOSTNAME=$(hostname -s)
        MYSQL_KEY_TMP=$(mktemp)
        MYSQL_CRT_TMP=$(mktemp)

        # sudo has problems with process substitution <()
        openssl req \
            -new \
            -newkey rsa:4096 \
            -sha512 \
            -days 3650 \
            -nodes \
            -x509 \
            -subj "/CN=${SHORT_HOSTNAME}.local" \
            -keyout "$MYSQL_KEY_TMP" \
            -out "$MYSQL_CRT_TMP" \
            -extensions san \
            -config <(cat /etc/ssl/openssl.cnf <(printf "\n[req]\ndistinguished_name=req\n[san]\nsubjectAltName=DNS:%s.local,DNS:%s,DNS:localhost" "$SHORT_HOSTNAME" "$SHORT_HOSTNAME"))

        sudo cp -f "$MYSQL_KEY_TMP" "$MYSQL_ETC/ssl/obsy_mysql.key"
        sudo cp -f "$MYSQL_CRT_TMP" "$MYSQL_ETC/ssl/obsy_mysql.pem"

        rm -f "$MYSQL_KEY_TMP"
        rm -f "$MYSQL_CRT_TMP"
    fi


    sudo chown root:root "$MYSQL_ETC/ssl/obsy_mysql.key"
    sudo chmod 600 "$MYSQL_ETC/ssl/obsy_mysql.key"
    sudo chown root:root "$MYSQL_ETC/ssl/obsy_mysql.pem"
    sudo chmod 644 "$MYSQL_ETC/ssl/obsy_mysql.pem"

    # system certificate store
    sudo cp -f "$MYSQL_ETC/ssl/obsy_mysql.pem" /usr/local/share/ca-certificates/obsy_mysql.crt
    sudo chown root:root /usr/local/share/ca-certificates/obsy_mysql.crt
    sudo chmod 644 /usr/local/share/ca-certificates/obsy_mysql.crt
    sudo update-ca-certificates


    sudo systemctl enable mariadb
    sudo systemctl restart mariadb
fi


# bootstrap initial config
"${ALLSKY_DIRECTORY}/config.py" bootstrap || true


# dump config for processing
TMP_CONFIG_DUMP=$(mktemp --suffix=.json)
"${ALLSKY_DIRECTORY}/config.py" dump > "$TMP_CONFIG_DUMP"


# Detect location
LOCATION_LATITUDE=$(jq -r '.LOCATION_LATITUDE' "$TMP_CONFIG_DUMP")
LOCATION_LONGITUDE=$(jq -r '.LOCATION_LONGITUDE' "$TMP_CONFIG_DUMP")


while [ -z "${LOCATION_LATITUDE_INPUT:-}" ]; do
    # shellcheck disable=SC2068
    LOCATION_LATITUDE_INPUT=$(whiptail --title "Latitude" --nocancel --inputbox "Please enter your latitude [90.0 to -90.0].  Positive values for the Northern Hemisphere, negative values for the Southern Hemisphere" 0 0 -- "$LOCATION_LATITUDE" 3>&1 1>&2 2>&3)
    if [[ "$LOCATION_LATITUDE_INPUT" =~ ^[+-]?[0-9]{3}$ ]]; then
        unset LOCATION_LATITUDE_INPUT
        whiptail --msgbox "Error: Invalid latitude" 0 0
        continue
    fi

    if ! [[ "$LOCATION_LATITUDE_INPUT" =~ ^[+-]?[0-9]{1,2}\.?[0-9]*$ ]]; then
        unset LOCATION_LATITUDE_INPUT
        whiptail --msgbox "Error: Invalid latitude" 0 0
        continue
    fi

    if [[ $(echo "$LOCATION_LATITUDE_INPUT < -90" | bc -l) -eq 1 || $(echo "$LOCATION_LATITUDE_INPUT > 90" | bc -l) -eq 1 ]]; then
        unset LOCATION_LATITUDE_INPUT
        whiptail --msgbox "Error: Invalid latitude" 0 0
        continue
    fi
done

while [ -z "${LOCATION_LONGITUDE_INPUT:-}" ]; do
    # shellcheck disable=SC2068
    LOCATION_LONGITUDE_INPUT=$(whiptail --title "Longitude" --nocancel --inputbox "Please enter your longitude [-180.0 to 180.0].  Negative values for the Western Hemisphere, positive values for the Eastern Hemisphere" 0 0 -- "$LOCATION_LONGITUDE" 3>&1 1>&2 2>&3)
    if [[ "$LOCATION_LATITUDE_INPUT" =~ ^[+-]?[0-9]{4}$ ]]; then
        unset LOCATION_LONGITUDE_INPUT
        whiptail --msgbox "Error: Invalid longitude" 0 0
        continue
    fi

    if ! [[ "$LOCATION_LONGITUDE_INPUT" =~ ^[+-]?[0-9]{1,3}\.?[0-9]*$ ]]; then
        unset LOCATION_LONGITUDE_INPUT
        whiptail --msgbox "Error: Invalid longitude" 0 0
        continue
    fi

    if [[ $(echo "$LOCATION_LONGITUDE_INPUT < -180" | bc -l) -eq 1 || $(echo "$LOCATION_LONGITUDE_INPUT > 180" | bc -l) -eq 1 ]]; then
        unset LOCATION_LONGITUDE_INPUT
        whiptail --msgbox "Error: Invalid longitude" 0 0
        continue
    fi
done


TMP_LOCATION=$(mktemp --suffix=.json)
jq \
    --argjson latitude "$LOCATION_LATITUDE_INPUT" \
    --argjson longitude "$LOCATION_LONGITUDE_INPUT" \
    '.LOCATION_LATITUDE = $latitude | .LOCATION_LONGITUDE = $longitude' "${TMP_CONFIG_DUMP}" > "$TMP_LOCATION"

cat "$TMP_LOCATION" > "$TMP_CONFIG_DUMP"

[[ -f "$TMP_LOCATION" ]] && rm -f "$TMP_LOCATION"



if [[ "$DISTRO_ID" == "debian" || "$DISTRO_ID" == "ubuntu" || "$DISTRO_ID" == "raspbian" ]]; then
    # reconfigure system timezone
    if [ -n "${OBSY_TIMEZONE:-}" ]; then
        # this is not validated
        echo
        echo "Setting timezone to $OBSY_TIMEZONE"
        echo "$OBSY_TIMEZONE" | sudo tee /etc/timezone
        sudo dpkg-reconfigure -f noninteractive tzdata
    else
        sudo dpkg-reconfigure tzdata
    fi
else
    echo "Unable to set timezone for distribution"
    exit 1
fi


# Detect IMAGE_FOLDER
IMAGE_FOLDER=$(jq -r '.IMAGE_FOLDER' "$TMP_CONFIG_DUMP")


echo
echo
echo "Detected IMAGE_FOLDER: $IMAGE_FOLDER"
sleep 3


# replace the flask IMAGE_FOLDER
TMP_FLASK_3=$(mktemp --suffix=.json)
jq --arg image_folder "$IMAGE_FOLDER" '.INDI_ALLSKY_IMAGE_FOLDER = $image_folder' "${ALLSKY_ETC}/flask.json" > "$TMP_FLASK_3"
cp -f "$TMP_FLASK_3" "${ALLSKY_ETC}/flask.json"
[[ -f "$TMP_FLASK_3" ]] && rm -f "$TMP_FLASK_3"


TMP_GUNICORN=$(mktemp)
cat "${ALLSKY_DIRECTORY}/service/gunicorn.conf.py" > "$TMP_GUNICORN"

cp -f "$TMP_GUNICORN" "${ALLSKY_ETC}/gunicorn.conf.py"
chmod 644 "${ALLSKY_ETC}/gunicorn.conf.py"
[[ -f "$TMP_GUNICORN" ]] && rm -f "$TMP_GUNICORN"



if [[ "$ASTROBERRY" == "true" ]]; then
    echo "**** Disabling apache web server (Astroberry) ****"
    sudo systemctl stop apache2 || true
    sudo systemctl disable apache2 || true


    echo "**** Setup astroberry nginx ****"
    TMP3=$(mktemp)
    sed \
     -e "s|%ALLSKY_DIRECTORY%|$ALLSKY_DIRECTORY|g" \
     -e "s|%ALLSKY_ETC%|$ALLSKY_ETC|g" \
     -e "s|%DOCROOT_FOLDER%|$DOCROOT_FOLDER|g" \
     -e "s|%IMAGE_FOLDER%|$IMAGE_FOLDER|g" \
     -e "s|%HTTP_PORT%|$HTTP_PORT|g" \
     -e "s|%HTTPS_PORT%|$HTTPS_PORT|g" \
     -e "s|%UPSTREAM_SERVER%|unix:$DB_FOLDER/$GUNICORN_SERVICE_NAME.sock|g" \
     "${ALLSKY_DIRECTORY}/service/nginx_astroberry_ssl" > "$TMP3"


    #sudo cp -f /etc/nginx/sites-available/astroberry_ssl "/etc/nginx/sites-available/astroberry_ssl_$(date +%Y%m%d_%H%M%S)"
    sudo cp -f "$TMP3" /etc/nginx/sites-available/obsy_ssl
    sudo chown root:root /etc/nginx/sites-available/obsy_ssl
    sudo chmod 644 /etc/nginx/sites-available/obsy_ssl
    sudo ln -s -f /etc/nginx/sites-available/obsy_ssl /etc/nginx/sites-enabled/obsy_ssl

    sudo systemctl enable nginx
    sudo systemctl restart nginx

else
    if systemctl -q is-active nginx; then
        echo "!!! WARNING - nginx is active - This might interfere with apache !!!"
        sleep 3
    fi

    if systemctl -q is-active lighttpd; then
        echo "!!! WARNING - lighttpd is active - This might interfere with apache !!!"
        sleep 3
    fi

    echo "**** Start apache2 service ****"
    TMP3=$(mktemp)
    sed \
     -e "s|%ALLSKY_DIRECTORY%|$ALLSKY_DIRECTORY|g" \
     -e "s|%ALLSKY_ETC%|$ALLSKY_ETC|g" \
     -e "s|%IMAGE_FOLDER%|$IMAGE_FOLDER|g" \
     -e "s|%HTTP_PORT%|$HTTP_PORT|g" \
     -e "s|%HTTPS_PORT%|$HTTPS_PORT|g" \
     -e "s|%UPSTREAM_SERVER%|unix:$DB_FOLDER/$GUNICORN_SERVICE_NAME.sock\|http://localhost/obsy|g" \
     "${ALLSKY_DIRECTORY}/service/apache_obsy.conf" > "$TMP3"


    if [[ "$DISTRO_ID" == "debian" || "$DISTRO_ID" == "ubuntu" || "$DISTRO_ID" == "raspbian" ]]; then
        sudo cp -f "$TMP3" /etc/apache2/sites-available/obsy.conf
        sudo chown root:root /etc/apache2/sites-available/obsy.conf
        sudo chmod 644 /etc/apache2/sites-available/obsy.conf


        if [[ ! -d "/etc/apache2/ssl" ]]; then
            sudo mkdir /etc/apache2/ssl
        fi

        sudo chown root:root /etc/apache2/ssl
        sudo chmod 755 /etc/apache2/ssl


        if [[ ! -f "/etc/apache2/ssl/obsy_apache.key" || ! -f "/etc/apache2/ssl/obsy_apache.pem" ]]; then
            sudo rm -f /etc/apache2/ssl/obsy_apache.key
            sudo rm -f /etc/apache2/ssl/obsy_apache.pem

            SHORT_HOSTNAME=$(hostname -s)
            APACHE_KEY_TMP=$(mktemp)
            APACHE_CRT_TMP=$(mktemp)

            # sudo has problems with process substitution <()
            openssl req \
                -new \
                -newkey rsa:4096 \
                -sha512 \
                -days 3650 \
                -nodes \
                -x509 \
                -subj "/CN=${SHORT_HOSTNAME}.local" \
                -keyout "$APACHE_KEY_TMP" \
                -out "$APACHE_CRT_TMP" \
                -extensions san \
                -config <(cat /etc/ssl/openssl.cnf <(printf "\n[req]\ndistinguished_name=req\n[san]\nsubjectAltName=DNS:%s.local,DNS:%s,DNS:localhost" "$SHORT_HOSTNAME" "$SHORT_HOSTNAME"))

            sudo cp -f "$APACHE_KEY_TMP" /etc/apache2/ssl/obsy_apache.key
            sudo cp -f "$APACHE_CRT_TMP" /etc/apache2/ssl/obsy_apache.pem

            rm -f "$APACHE_KEY_TMP"
            rm -f "$APACHE_CRT_TMP"
        fi


        sudo chown root:root /etc/apache2/ssl/obsy_apache.key
        sudo chmod 600 /etc/apache2/ssl/obsy_apache.key
        sudo chown root:root /etc/apache2/ssl/obsy_apache.pem
        sudo chmod 644 /etc/apache2/ssl/obsy_apache.pem

        # system certificate store
        sudo cp -f /etc/apache2/ssl/obsy_apache.pem /usr/local/share/ca-certificates/obsy_apache.crt
        sudo chown root:root /usr/local/share/ca-certificates/obsy_apache.crt
        sudo chmod 644 /usr/local/share/ca-certificates/obsy_apache.crt
        sudo update-ca-certificates


        sudo a2enmod rewrite
        sudo a2enmod headers
        sudo a2enmod ssl
        sudo a2enmod http2
        sudo a2enmod proxy
        sudo a2enmod proxy_http
        sudo a2enmod proxy_http2
        sudo a2enmod expires

        sudo a2dissite 000-default
        sudo a2dissite default-ssl

        sudo a2ensite obsy

        if [[ ! -f "/etc/apache2/ports.conf_pre_OBSY" ]]; then
            sudo cp /etc/apache2/ports.conf /etc/apache2/ports.conf_pre_OBSY

            # Comment out the Listen directives
            TMP9=$(mktemp)
            sed \
             -e 's|^\(.*\)[^#]\?\(listen.*\)|\1#\2|i' \
             /etc/apache2/ports.conf_pre_OBSY > "$TMP9"

            sudo cp -f "$TMP9" /etc/apache2/ports.conf
            sudo chown root:root /etc/apache2/ports.conf
            sudo chmod 644 /etc/apache2/ports.conf
            [[ -f "$TMP9" ]] && rm -f "$TMP9"
        fi

        sudo systemctl enable apache2
        sudo systemctl restart apache2

    elif [[ "$DISTRO_ID" == "centos" ]]; then
        sudo cp -f "$TMP3" /etc/httpd/conf.d/obsy.conf
        sudo chown root:root /etc/httpd/conf.d/obsy.conf
        sudo chmod 644 /etc/httpd/conf.d/obsy.conf

        sudo systemctl enable httpd
        sudo systemctl restart httpd
    fi

fi

[[ -f "$TMP3" ]] && rm -f "$TMP3"


# Allow web server access to mounted media
if [[ -d "/media/${USER}" ]]; then
    sudo chmod ugo+x "/media/${USER}"
fi


echo "**** Setup HTDOCS folder ****"
[[ ! -d "$HTDOCS_FOLDER" ]] && sudo mkdir "$HTDOCS_FOLDER"
sudo chmod 755 "$HTDOCS_FOLDER"
sudo chown -R "$USER":"$PGRP" "$HTDOCS_FOLDER"
[[ ! -d "$HTDOCS_FOLDER/js" ]] && mkdir "$HTDOCS_FOLDER/js"
chmod 775 "$HTDOCS_FOLDER/js"

for F in $HTDOCS_FILES; do
    cp -f "${ALLSKY_DIRECTORY}/html/${F}" "${HTDOCS_FOLDER}/${F}"
    chmod 664 "${HTDOCS_FOLDER}/${F}"
done


echo "**** Setup image folder ****"
[[ ! -d "$IMAGE_FOLDER" ]] && sudo mkdir -p "$IMAGE_FOLDER"
sudo chmod 775 "$IMAGE_FOLDER"
sudo chown -R "$USER":"$PGRP" "$IMAGE_FOLDER"
[[ ! -d "${IMAGE_FOLDER}/darks" ]] && mkdir "${IMAGE_FOLDER}/darks"
chmod 775 "${IMAGE_FOLDER}/darks"
[[ ! -d "${IMAGE_FOLDER}/export" ]] && mkdir "${IMAGE_FOLDER}/export"
chmod 775 "${IMAGE_FOLDER}/export"

if [ "$IMAGE_FOLDER" != "${ALLSKY_DIRECTORY}/html/images" ]; then
    for F in $IMAGE_FOLDER_FILES; do
        cp -f "${ALLSKY_DIRECTORY}/html/images/${F}" "${IMAGE_FOLDER}/${F}"
        chmod 664 "${IMAGE_FOLDER}/${F}"
    done
fi


# Disable raw frames with libcamera when running less than 1GB of memory
if [ "$MEM_TOTAL" -lt "768000" ]; then
    TMP_LIBCAM_TYPE=$(mktemp --suffix=.json)
    jq --arg libcamera_file_type "jpg" '.LIBCAMERA.IMAGE_FILE_TYPE = $libcamera_file_type' "$TMP_CONFIG_DUMP" > "$TMP_LIBCAM_TYPE"

    cat "$TMP_LIBCAM_TYPE" > "$TMP_CONFIG_DUMP"

    [[ -f "$TMP_LIBCAM_TYPE" ]] && rm -f "$TMP_LIBCAM_TYPE"
fi

# 25% ffmpeg scaling with libcamera when running 1GB of memory
if [[ "$CAMERA_INTERFACE" == "libcamera_imx477" || "$CAMERA_INTERFACE" == "libcamera_imx378" || "$CAMERA_INTERFACE" == "libcamera_ov5647" || "$CAMERA_INTERFACE" == "libcamera_imx219" || "$CAMERA_INTERFACE" == "libcamera_imx519" || "$CAMERA_INTERFACE" == "libcamera_imx708" || "$CAMERA_INTERFACE" == "libcamera_64mp_hawkeye" || "$CAMERA_INTERFACE" == "libcamera_64mp_owlsight" ]]; then
    if [ "$MEM_TOTAL" -lt "1536000" ]; then
        TMP_LIBCAM_FFMPEG=$(mktemp --suffix=.json)
        jq --arg ffmpeg_vfscale "iw*.25:ih*.25" '.FFMPEG_VFSCALE = $ffmpeg_vfscale' "$TMP_CONFIG_DUMP" > "$TMP_LIBCAM_FFMPEG"

        cat "$TMP_LIBCAM_FFMPEG" > "$TMP_CONFIG_DUMP"

        [[ -f "$TMP_LIBCAM_FFMPEG" ]] && rm -f "$TMP_LIBCAM_FFMPEG"
    fi
fi


echo "**** Ensure user is a member of the dialout, video, i2c, spi groups ****"
# for GPS and serial port access
sudo usermod -a -G dialout,video "$USER"

if getent group i2c >/dev/null 2>&1; then
    sudo usermod -a -G i2c "$USER"
fi

if getent group spi >/dev/null 2>&1; then
    sudo usermod -a -G spi "$USER"
fi


echo "**** Disabling Thomas Jacquin's allsky (ignore errors) ****"
# Not trying to push out the competition, these just cannot run at the same time :-)
sudo systemctl stop allsky || true
sudo systemctl disable allsky || true


echo "**** Starting ${GUNICORN_SERVICE_NAME}.socket"
# this needs to happen after creating the $DB_FOLDER
systemctl --user start ${GUNICORN_SERVICE_NAME}.socket


echo "**** Update config camera interface ****"
TMP_CAMERA_INT=$(mktemp --suffix=.json)
jq --arg camera_interface "$CAMERA_INTERFACE" '.CAMERA_INTERFACE = $camera_interface' "$TMP_CONFIG_DUMP" > "$TMP_CAMERA_INT"

cat "$TMP_CAMERA_INT" > "$TMP_CONFIG_DUMP"

[[ -f "$TMP_CAMERA_INT" ]] && rm -f "$TMP_CAMERA_INT"


# final config syntax check
json_pp < "${ALLSKY_ETC}/flask.json" > /dev/null


USER_COUNT=$("${ALLSKY_DIRECTORY}/config.py" user_count)
# there is a system user
if [ "$USER_COUNT" -le 1 ]; then
    while [ -z "${WEB_USER:-}" ]; do
        # shellcheck disable=SC2068
        WEB_USER=$(whiptail --title "Username" --nocancel --inputbox "Please enter a username to login" 0 0 3>&1 1>&2 2>&3)
    done

    while [ -z "${WEB_PASS:-}" ]; do
        # shellcheck disable=SC2068
        WEB_PASS=$(whiptail --title "Password" --nocancel --passwordbox "Please enter the password (8+ chars)" 0 0 3>&1 1>&2 2>&3)

        if [ "${#WEB_PASS}" -lt 8 ]; then
            WEB_PASS=""
            whiptail --msgbox "Error: Password needs to be at least 8 characters" 0 0
            continue
        fi


        WEB_PASS2=$(whiptail --title "Password (#2)" --nocancel --passwordbox "Please enter the password (8+ chars)" 0 0 3>&1 1>&2 2>&3)

        if [ "$WEB_PASS" != "$WEB_PASS2" ]; then
            WEB_PASS=""
            whiptail --msgbox "Error: Passwords did not match" 0 0
            continue
        fi

    done

    while [ -z "${WEB_NAME:-}" ]; do
        # shellcheck disable=SC2068
        WEB_NAME=$(whiptail --title "Full Name" --nocancel --inputbox "Please enter the users name" 0 0 3>&1 1>&2 2>&3)
    done

    while [ -z "${WEB_EMAIL:-}" ]; do
        # shellcheck disable=SC2068
        WEB_EMAIL=$(whiptail --title "Full Name" --nocancel --inputbox "Please enter the users email" 0 0 3>&1 1>&2 2>&3)
    done

    "$ALLSKY_DIRECTORY/misc/usertool.py" adduser -u "$WEB_USER" -p "$WEB_PASS" -f "$WEB_NAME" -e "$WEB_EMAIL"
    "$ALLSKY_DIRECTORY/misc/usertool.py" setadmin -u "$WEB_USER"
fi


# load all changes
"${ALLSKY_DIRECTORY}/config.py" load -c "$TMP_CONFIG_DUMP" --force
[[ -f "$TMP_CONFIG_DUMP" ]] && rm -f "$TMP_CONFIG_DUMP"


# ensure indiserver is running
systemctl --user start ${INDISERVER_SERVICE_NAME}.service

# ensure latest code is active
systemctl --user restart ${GUNICORN_SERVICE_NAME}.service


echo
echo
echo
echo
echo "*** Configurations are now stored in the database and *NOT* /etc/obsy/config.json ***"
echo
echo "Services can be started at the command line or can be started from the web interface"
echo
echo "    systemctl --user start obsy"
echo
echo
echo "The web interface may be accessed with the following URL"
echo " (You may have to manually access by IP)"
echo

if [[ "$HTTPS_PORT" -eq 443 ]]; then
    echo "    https://$(hostname -s).local/obsy/"
else
    echo "    https://$(hostname -s).local:$HTTPS_PORT/obsy/"

fi

END_TIME=$(date +%s)

echo
echo
echo "Completed in $((END_TIME - START_TIME))s"
echo

echo
echo "Enjoy!"