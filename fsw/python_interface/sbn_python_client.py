#
# GSC-18396-1, “Software Bus Network Client for External Process”
#
# Copyright © 2019 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# No copyright is claimed in the United States under Title 17, U.S. Code.
# All Other Rights Reserved.
#
# Licensed under the NASA Open Source Agreement version 1.3
# See "NOSA GSC-18396-1.pdf"
#

import ctypes
from ctypes import *

# SB
CFE_SB_PEND_FOREVER = -1


# /**
#  * \brief Full CCSDS header
#  */
# typedef struct
# {
#     CCSDS_PrimaryHeader_t Pri; /**< \brief CCSDS Primary Header */
# } CCSDS_SpacePacket_t;

# /**
#  * \brief cFS generic base message
#  *
#  * This provides the definition of CFE_MSG_Message_t
#  */
# union CFE_MSG_Message
# {
#     CCSDS_SpacePacket_t CCSDS;                             /**< \brief CCSDS Header (Pri or Pri + Ext) */
#     uint8               Byte[sizeof(CCSDS_SpacePacket_t)]; /**< \brief Byte level access */
# };

# /**
#  * \brief cFS command header
#  *
#  * This provides the definition of CFE_MSG_CommandHeader_t
#  */
# struct CFE_MSG_CommandHeader
# {
#     CFE_MSG_Message_t                Msg; /**< \brief Base message */
#     CFE_MSG_CommandSecondaryHeader_t Sec; /**< \brief Secondary header */
# };

# /**
#  * \brief cFS telemetry header
#  *
#  * This provides the definition of CFE_MSG_TelemetryHeader_t
#  */
# struct CFE_MSG_TelemetryHeader
# {
#     CFE_MSG_Message_t                  Msg;      /**< \brief Base message */
#     CFE_MSG_TelemetrySecondaryHeader_t Sec;      /**< \brief Secondary header */
#     uint8                              Spare[4]; /**< \brief Pad to avoid compiler padding if payload
#                                                              requires 64 bit alignment */
# };

# /**********************************************************************
#  * Structure definitions for CCSDS headers.
#  *
#  * CCSDS headers must always be in network byte order per the standard.
#  * MSB at the lowest address which is commonly referred to as "BIG Endian"
#  *
#  */

# /**
#  * \brief CCSDS packet primary header
#  */
# typedef struct CCSDS_PrimaryHeader
# {
#     uint8 StreamId[2]; /**< \brief packet identifier word (stream ID) */
#                        /*  bits  shift   ------------ description ---------------- */
#                        /* 0x07FF    0  : application ID                            */
#                        /* 0x0800   11  : secondary header: 0 = absent, 1 = present */
#                        /* 0x1000   12  : packet type:      0 = TLM, 1 = CMD        */
#                        /* 0xE000   13  : CCSDS version:    0 = ver 1, 1 = ver 2    */

#     uint8 Sequence[2]; /**< \brief packet sequence word */
#                        /*  bits  shift   ------------ description ---------------- */
#                        /* 0x3FFF    0  : sequence count                            */
#                        /* 0xC000   14  : segmentation flags:  3 = complete packet  */

#     uint8 Length[2]; /**< \brief packet length word */
#                      /*  bits  shift   ------------ description ---------------- */
#                      /* 0xFFFF    0  : (total packet length) - 7                 */
# } CCSDS_PrimaryHeader_t;

# /**
#  * \brief cFS command secondary header
#  */
# typedef struct
# {
#     uint8 FunctionCode; /**< \brief Command Function Code */
#                         /* bits shift ---------description-------- */
#                         /* 0x7F  0    Command function code        */
#                         /* 0x80  7    Reserved                     */

#     uint8 Checksum; /**< \brief Command checksum  (all bits, 0xFF)      */
# } CFE_MSG_CommandSecondaryHeader_t;

# /**
#  * \brief cFS telemetry secondary header
#  */
# typedef struct
# {
#     uint8 Time[6]; /**< \brief Time, big endian: 4 byte seconds, 2 byte subseconds */
# } CFE_MSG_TelemetrySecondaryHeader_t;

# Note: Not currently dealing with the whole union issue
class CCSDS_PrimaryHeader_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("StreamId", c_uint16),
                ("Sequence", c_uint16),
                ("Length", c_uint16)]

class CCSDS_SpacePacket_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("Pri", CCSDS_PrimaryHeader_t)]

class CFE_MSG_Message_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("CCSDS", CCSDS_SpacePacket_t),
                ("Byte", c_uint8[sizeof(CCSDS_SpacePacket_t)])]

class CFE_MSG_TelemetrySecondaryHeader_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("Seconds", c_uint32),
                ("Subseconds", c_uint16)]

class CFE_MSG_CommandSecondaryHeader_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("FunctionCode", c_uint8),
                ("Checksum", c_uint8)]
    
class CFE_MSG_CommandHeader_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("Msg", CFE_MSG_Message_t),
                ("Sec", CFE_MSG_CommandSecondaryHeader_t),
                ("Spare", c_uint32)]
    
class CFE_MSG_TelemetryHeader_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [("Msg", CFE_MSG_Message_t),
                ("Sec", CFE_MSG_TelemetrySecondaryHeader_t),
                ("Spare", c_uint32)]

# class CFE_SB_Msg_t(Structure):
#     _pack_ = 1
#     _fields_ = [("Primary", Primary_Header_t),
#                 ("Secondary", Secondary_Header_t)]

#for generic data type
# TODO Should the max message size be hardcoded or somehow taken from the mps_defs directory?
class sbn_data_generic_t(Structure):
    _pack_ = 1
    _fields_ = [("TlmHeader", CFE_MSG_TelemetryHeader_t),
                ("byte_array", c_ubyte * 65536)]

sbn_client = None
cmd_pipe = c_uint32()
cmd_pipe_name = create_string_buffer(b'cmd_pipe')


def print_header(message_p):
    recv_msg = message_p.contents
    print("Message Header: {} {} {}".format(hex(recv_msg.TlmHeader.Msg.CCSDS.Pri.StreamId),
                                            hex(recv_msg.TlmHeader.Msg.CCSDS.Pri.Sequence),
                                            hex(recv_msg.TlmHeader.MSG.CCSDS.Pri.Length)))
    print("Message Time: {} {}".format(hex(recv_msg.TlmHeader.Sec.Seconds),
                                       hex(recv_msg.TlmHeader.Sec.Subseconds)))

# TODO: Common file?
def cfs_error_convert (number):
    if number < 0:
        return number + (2**32)
    else:
        return number

def sbn_load_and_init():
    global sbn_client
    global cmd_pipe
    global cmd_pipe_name

    ctypes.cdll.LoadLibrary('./sbn_client.so')
    sbn_client = CDLL('sbn_client.so')
    print("SBN Client library loaded: '{}'".format(sbn_client))
    status = sbn_client.SBN_Client_Init()
    print("SBN Client init: {}".format(status))
    status = sbn_client.__wrap_CFE_SB_CreatePipe(byref(cmd_pipe), 10, cmd_pipe_name)
    print("SBN Client command pipe: {}".format(status))
    print("SBN Client sbn_load_and_init pipe: {}".format(cmd_pipe))

def send_msg(send_msg_p):
    global sbn_client

    # Adding debug print
    send_msg = send_msg_p.contents
    print("Message: {} {} {}".format(hex(send_msg.Hdr.StreamId), hex(send_msg.Hdr.Sequence), hex(send_msg.Hdr.Length)))
    print_header(send_msg_p)

    sbn_client.__wrap_CFE_SB_TransmitMsg(send_msg_p, true)

def recv_msg(recv_msg_p):
    global sbn_client
    global cmd_pipe

    print("SBN Client recv_msg: recv_msg_p: {}".format(recv_msg_p))
    print("SBN Client recv_msg: before read pipe: {}".format(cmd_pipe))
    status = sbn_client.__wrap_CFE_SB_ReceiveBuffer(byref(recv_msg_p), cmd_pipe, CFE_SB_PEND_FOREVER)

    print("SBN Client recv_msg: after read pipe: {}".format(cmd_pipe))
    print_header(recv_msg_p)
    if (status != 0):
        print("status of __wrap_CFE_SB_ReceiveBuffer = %X" % cfs_error_convert(status))
    # debug print
    recv_msg = recv_msg_p.contents
    print("Message: {} {} {}".format(hex(recv_msg.Hdr.StreamId), hex(recv_msg.Hdr.Sequence), hex(recv_msg.Hdr.Length)))
    print_header(recv_msg_p)

def subscribe(msgid):
    global cmd_pipe

    print("SBN Client subscribe msgid: {}".format(msgid))
    print("SBN Client subscribe before_sub pipe: {}".format(cmd_pipe))
    status = sbn_client.__wrap_CFE_SB_Subscribe(msgid, cmd_pipe)
    print("SBN Client subscribe after_sub pipe: {}".format(cmd_pipe))
    print("SBN Client subscribe msg (id {}): {}".format(hex(msgid), status))
