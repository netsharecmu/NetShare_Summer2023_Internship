# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: task.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ntask.proto\"\xb6\x01\n\x0cStartingTask\x12\x0f\n\x07task_id\x18\x01 \x01(\x03\x12\x11\n\ttask_kind\x18\x02 \x01(\t\x12\x12\n\ncreated_at\x18\x03 \x01(\t\x12\x19\n\x11\x64\x61taset_file_name\x18\x04 \x01(\t\x12\x1c\n\x14\x64\x61taset_file_content\x18\x05 \x01(\x0c\x12\x18\n\x10\x63onfig_file_name\x18\x06 \x01(\t\x12\x1b\n\x13\x63onfig_file_content\x18\x07 \x01(\x0c\"K\n\x0eStartingStatus\x12\x0f\n\x07task_id\x18\x01 \x01(\x03\x12\x11\n\ttask_name\x18\x02 \x01(\t\x12\x15\n\ris_successful\x18\x03 \x01(\x08\"1\n\x0bRunningTask\x12\x0f\n\x07task_id\x18\x01 \x01(\x03\x12\x11\n\ttask_name\x18\x02 \x01(\t\"z\n\rRunningStatus\x12\x0f\n\x07task_id\x18\x01 \x01(\x03\x12\x11\n\ttask_name\x18\x02 \x01(\t\x12\x14\n\x0cis_completed\x18\x03 \x01(\x08\x12\x15\n\rlog_file_name\x18\x04 \x01(\t\x12\x18\n\x10log_file_content\x18\x05 \x01(\t\"3\n\rCompletedTask\x12\x0f\n\x07task_id\x18\x01 \x01(\x03\x12\x11\n\ttask_name\x18\x02 \x01(\t\"5\n\nResultFile\x12\x11\n\tfile_name\x18\x01 \x01(\t\x12\x14\n\x0c\x66ile_content\x18\x02 \x01(\x0c\x32\x94\x01\n\x04Task\x12/\n\tStartTask\x12\r.StartingTask\x1a\x0f.StartingStatus\"\x00(\x01\x12-\n\x0bQueryStatus\x12\x0c.RunningTask\x1a\x0e.RunningStatus\"\x00\x12,\n\tGetResult\x12\x0e.CompletedTask\x1a\x0b.ResultFile\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'task_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_STARTINGTASK']._serialized_start=15
  _globals['_STARTINGTASK']._serialized_end=197
  _globals['_STARTINGSTATUS']._serialized_start=199
  _globals['_STARTINGSTATUS']._serialized_end=274
  _globals['_RUNNINGTASK']._serialized_start=276
  _globals['_RUNNINGTASK']._serialized_end=325
  _globals['_RUNNINGSTATUS']._serialized_start=327
  _globals['_RUNNINGSTATUS']._serialized_end=449
  _globals['_COMPLETEDTASK']._serialized_start=451
  _globals['_COMPLETEDTASK']._serialized_end=502
  _globals['_RESULTFILE']._serialized_start=504
  _globals['_RESULTFILE']._serialized_end=557
  _globals['_TASK']._serialized_start=560
  _globals['_TASK']._serialized_end=708
# @@protoc_insertion_point(module_scope)