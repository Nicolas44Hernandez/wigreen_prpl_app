FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://server"
SRC_URI += "file://poc"
SRC_URI += "file://start.sh"


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
        ### APP
        install -d ${D}/usr/srv/server
        install -m 0644 ${S}/server/app.py ${D}/usr/srv/server/
        install -m 0644 ${S}/server/__init__.py ${D}/usr/srv/server/

        ### CONFIG
        install -d ${D}/usr/srv/server/config
        install -m 0644 ${S}/server/config/* ${D}/usr/srv/server/config/

        ### COMMON
        install -d ${D}/usr/srv/server/common
        install -m 0644 ${S}/server/common/__init__.py ${D}/usr/srv/server/common/
        install -d ${D}/usr/srv/server/common/exception
        install -m 0644 ${S}/server/common/exception/* ${D}/usr/srv/server/common/exception/

        ### INTERFACES
        install -d ${D}/usr/srv/server/interfaces
        install -m 0644 ${S}/server/interfaces/__init__.py ${D}/usr/srv/server/interfaces/
        # amx_usp_interface
        install -d ${D}/usr/srv/server/interfaces/amx_usp_interface
        install -m 0644 ${S}/server/interfaces/amx_usp_interface/* ${D}/usr/srv/server/interfaces/amx_usp_interface/
        # mqtt_interface
        install -d ${D}/usr/srv/server/interfaces/mqtt_interface
        install -m 0644 ${S}/server/interfaces/mqtt_interface/* ${D}/usr/srv/server/interfaces/mqtt_interface/

        ### MANAGERS
        install -d ${D}/usr/srv/server/managers
        install -m 0644 ${S}/server/managers/__init__.py ${D}/usr/srv/server/managers/
        # wifi_bands_manager
        install -d ${D}/usr/srv/server/managers/wifi_bands_manager
        install -m 0644 ${S}/server/managers/wifi_bands_manager/* ${D}/usr/srv/server/managers/wifi_bands_manager/
        # mqtt manager
        install -d ${D}/usr/srv/server/managers/mqtt_manager
        install -m 0644 ${S}/server/managers/mqtt_manager/* ${D}/usr/srv/server/managers/mqtt_manager/
        # electrical panel manager
        install -d ${D}/usr/srv/server/managers/electrical_panel_manager
        install -m 0644 ${S}/server/managers/electrical_panel_manager/* ${D}/usr/srv/server/managers/electrical_panel_manager/

        ### ORCHESTRATOR
        install -d ${D}/usr/srv/server/orchestrator
        install -m 0644 ${S}/server/orchestrator/__init__.py ${D}/usr/srv/server/orchestrator/
        install -m 0644 ${S}/server/orchestrator/service.py ${D}/usr/srv/server/orchestrator/
        # notification
        install -d ${D}/usr/srv/server/orchestrator/notification
        install -m 0644 ${S}/server/orchestrator/notification/* ${D}/usr/srv/server/orchestrator/notification/
        # polling
        install -d ${D}/usr/srv/server/orchestrator/polling
        install -m 0644 ${S}/server/orchestrator/polling/* ${D}/usr/srv/server/orchestrator/polling/

        ### REST API
        install -d ${D}/usr/srv/server/rest_api
        install -m 0644 ${S}/server/rest_api/__init__.py ${D}/usr/srv/server/rest_api/
        # wifi_controller
        install -d ${D}/usr/srv/server/rest_api/wifi_controller
        install -m 0644 ${S}/server/rest_api/wifi_controller/* ${D}/usr/srv/server/rest_api/wifi_controller/
        # mqtt_controller
        install -d ${D}/usr/srv/server/rest_api/mqtt_controller
        install -m 0644 ${S}/server/rest_api/mqtt_controller/* ${D}/usr/srv/server/rest_api/mqtt_controller/
        # electrical_panel_controller
        install -d ${D}/usr/srv/server/rest_api/electrical_panel_controller
        install -m 0644 ${S}/server/rest_api/electrical_panel_controller/* ${D}/usr/srv/server/rest_api/electrical_panel_controller/

        ### POC
        install -d ${D}/usr/srv/poc
        install -m 0644 ${S}/poc/__init__.py ${D}/usr/srv/poc/
        # usp poc
        install -d ${D}/usr/srv/poc/usp
        install -m 0644 ${S}/poc/usp/__init__.py ${D}/usr/srv/poc/usp/
        install -m 0644 ${S}/poc/usp/* ${D}/usr/srv/poc/usp/
        # http poc
        install -d ${D}/usr/srv/poc/http
        install -m 0644 ${S}/poc/http/__init__.py ${D}/usr/srv/poc/http/
        install -m 0644 ${S}/poc/http/* ${D}/usr/srv/poc/http/
        # mqtt poc
        install -d ${D}/usr/srv/poc/mqtt
        install -m 0644 ${S}/poc/mqtt/__init__.py ${D}/usr/srv/poc/mqtt/
        install -d ${D}/usr/srv/poc/mqtt/basic
        install -m 0644 ${S}/poc/mqtt/basic/* ${D}/usr/srv/poc/mqtt/basic/
        install -d ${D}/usr/srv/poc/mqtt/interface
        install -m 0644 ${S}/poc/mqtt/interface/* ${D}/usr/srv/poc/mqtt/interface/

}

FILES:${PN} += "/usr/srv/server/*"
FILES:${PN} += "/usr/srv/poc/*"

do_install:append () {
        # Service script
        install -d ${D}/etc/init.d
        install -D -p -m 0755 start.sh ${D}/etc/init.d/wigreen
}

inherit update-rc.d
INITSCRIPT_NAME = "wigreen"
INITSCRIPT_PARAMS = "start 99 2 3 4 5 . stop 10 0 1 6 ."
