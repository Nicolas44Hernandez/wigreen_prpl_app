FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI += "file://orchestrator.py"

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
        :
}