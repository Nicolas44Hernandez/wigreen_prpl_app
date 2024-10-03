FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://server"
SRC_URI += "file://tests"


S = "${WORKDIR}"

LICENSE = "CLOSED"
LIC_FILES_CHKSUM = ""

DEPENDS += "python3"
RDEPENDS:${PN} += "python3"


do_configure () {
        # Specify any needed configure commands here
        :
}

do_compile () {
        # Specify compilation commands here
        :
}

do_install () {
        # APP
        install -d ${D}/usr/srv/server        
        install -m 0644 ${S}/server/app.py ${D}/usr/srv/server/ 
        install -m 0644 ${S}/server/__init__.py ${D}/usr/srv/server/ 
        
        # CONFIG
        install -d ${D}/usr/srv/server/config
        install -m 0644 ${S}/server/config/* ${D}/usr/srv/server/config/

        # INTERFACES
        install -d ${D}/usr/srv/server/interfaces
        install -m 0644 ${S}/server/interfaces/__init__.py ${D}/usr/srv/server/interfaces/
        install -d ${D}/usr/srv/server/interfaces/amx_usp_interface
        install -m 0644 ${S}/server/interfaces/amx_usp_interface/* ${D}/usr/srv/server/interfaces/amx_usp_interface/

        # MANAGERS
        install -d ${D}/usr/srv/server/managers
        install -m 0644 ${S}/server/managers/__init__.py ${D}/usr/srv/server/managers/
        install -d ${D}/usr/srv/server/managers/wifi_bands_manager
        install -m 0644 ${S}/server/managers/wifi_bands_manager/* ${D}/usr/srv/server/managers/wifi_bands_manager/

        # REST API
        install -d ${D}/usr/srv/server/rest_api
        install -m 0644 ${S}/server/rest_api/__init__.py ${D}/usr/srv/server/rest_api/
        install -d ${D}/usr/srv/server/rest_api/wifi_controler
        install -m 0644 ${S}/server/rest_api/wifi_controler/* ${D}/usr/srv/server/rest_api/wifi_controler/

        # TEST
        install -d ${D}/usr/srv/tests
        install -m 0644 ${S}/tests/test_usp.py ${D}/usr/srv/tests/
        install -m 0644 ${S}/tests/test_usp_basic.py ${D}/usr/srv/tests/
}

FILES:${PN} += "/usr/srv/server/*"
FILES:${PN} += "/usr/srv/tests/*"