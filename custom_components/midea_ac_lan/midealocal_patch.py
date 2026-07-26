"""Temporary runtime patches for the pinned `midealocal` release.

Each patch here works around a bug in the `midea-local` version pinned in
`manifest.json`. Drop the patch as soon as the pin moves to a release that
contains the upstream fix.
"""

import logging

from midealocal.devices.ac import message as ac_message

_LOGGER = logging.getLogger(__name__)

# midea-local 6.11.0 decodes the new-protocol `0x7e` tag as a subtype-8
# temperature payload on every AC that reports the tag, although the byte
# offsets were only ever verified on subtype-8 firmware. On other models the
# tag carries unrelated data: model 22251759 / subtype 32773 decodes to
# -15.0 C, and the first such frame latches `_prefer_new_protocol_temperature`,
# after which the correct C0 target/indoor/outdoor temperatures are discarded
# for the rest of the session.
#
# Upstream fix: https://github.com/midea-lan/midea-local/pull/567
#
# A negative tag id can never match a parsed parameter (they are built from
# two unsigned bytes), so pointing the constant at one disables the whole
# `0x7e` temperature path without touching any library file.
_UNREACHABLE_TAG = -1


def apply_patches() -> None:
    """Apply the runtime patches. Safe to call more than once."""
    tag = getattr(ac_message, "SUBTYPE8_TEMPERATURE_TAG", None)
    if tag is None:
        # The constant is gone: the pinned release no longer needs this patch.
        return
    if tag != _UNREACHABLE_TAG:
        ac_message.SUBTYPE8_TEMPERATURE_TAG = _UNREACHABLE_TAG
        _LOGGER.debug("Patched midealocal: AC 0x7e temperature decoding disabled")
