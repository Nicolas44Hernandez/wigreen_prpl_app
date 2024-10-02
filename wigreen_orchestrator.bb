FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://orchestrator.py"
SRC_URI += "file://script.sh"

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
        install -d ${D}/usr/srv
        install -D -p -m 0755 orchestrator.py ${D}/usr/srv/
}

FILES:${PN} += "/etc/init.d/orchestrator"
FILES:${PN} += "/usr/srv/orchestrator.py"


do_install:append () {
        # Specify install commands here
    install -d ${D}/etc/init.d
    install -D -p -m 0755 script.sh ${D}/etc/init.d/orchestrator
}

inherit update-rc.d
INITSCRIPT_NAME = "orchestrator"
INITSCRIPT_PARAMS = "start 99 2 3 4 5 . stop 10 0 1 6 ."