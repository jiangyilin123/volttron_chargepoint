import ast
import logging
from collections import defaultdict

import pytz
import re
from basedb import DbDriver


def create_schema(connection):
    _log = logging.getLogger(__name__)
    _log.debug("Creating crate tables if necessary.")

    create_queries = [
        """
        CREATE TABLE IF NOT EXISTS topic(
            id string,
            name string,
            primary key (id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS meta(
            topic_id string,
            meta_data string,
            primary key (topic_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS analysis(
            topic_id string,
            ts timestamp NOT NULL,
            result float,
            primary key (topic_id, ts)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS datalogger(
            topic_id string,
            ts timestamp NOT NULL,
            result float,
            primary key (topic_id, ts)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS device(
            topic_id string,
            ts timestamp NOT NULL,
            result float,
            primary key (topic_id, ts)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS record(
            topic_id string,
            ts timestamp NOT NULL,
            result string,
            primary key (topic_id, ts)
        )
        """
    ]
    try:
        cursor = connection.cursor()
        for t in create_queries:
            cursor.execute(t)
            _log.debug("Query took: {}ms".format(cursor.duration))
        #cursor.execute(query)
        _log.debug("Query took: {}ms".format(cursor.duration))
    finally:
        cursor.close()

#
# def query(self, topic_ids, id_name_map, start=None, end=None, skip=0,
#           agg_type=None,
#           agg_period=None, count=None, order="FIRST_TO_LAST"):
#
#     _log = logging.getLogger(__name__)
#     _log.debug("Creating crate tables if necessary.")
#     table_name = self.data_table
#     if agg_type and agg_period:
#         table_name = agg_type + "_" + agg_period
#
#     query = '''SELECT topic_id, ts, result
#             FROM ''' + table_name + '''
#             {where}
#             {order_by}
#             {limit}
#             {offset}'''
#
#     where_clauses = ["WHERE topic_id = %s"]
#     args = [topic_ids[0]]
#
#     if start is not None:
#         if not self.MICROSECOND_SUPPORT:
#             start_str = start.isoformat()
#             start = start_str[:start_str.rfind('.')]
#
#     if end is not None:
#         if not self.MICROSECOND_SUPPORT:
#             end_str = end.isoformat()
#             end = end_str[:end_str.rfind('.')]
#
#     if start and end and start == end:
#         where_clauses.append("ts = %s")
#         args.append(start)
#     elif start:
#         where_clauses.append("ts >= %s")
#         args.append(start)
#     elif end:
#         where_clauses.append("ts < %s")
#         args.append(end)
#
#     where_statement = ' AND '.join(where_clauses)
#
#     order_by = 'ORDER BY ts ASC'
#     if order == 'LAST_TO_FIRST':
#         order_by = ' ORDER BY topic_id DESC, ts DESC'
#
#     # can't have an offset without a limit
#     # -1 = no limit and allows the user to
#     # provide just an offset
#     if count is None:
#         count = 100
#
#     limit_statement = 'LIMIT %s'
#     args.append(int(count))
#
#     offset_statement = ''
#     if skip > 0:
#         offset_statement = 'OFFSET %s'
#         args.append(skip)
#
#     _log.debug("About to do real_query")
#     values = defaultdict(list)
#     for topic_id in topic_ids:
#         args[0] = topic_id
#         real_query = query.format(where=where_statement,
#                                   limit=limit_statement,
#                                   offset=offset_statement,
#                                   order_by=order_by)
#         _log.debug("Real Query: " + real_query)
#         _log.debug("args: " + str(args))
#
#         rows = self.select(real_query, args)
#         if rows:
#             for _id, ts, value in rows:
#                 values[id_name_map[topic_id]].append(
#                     (utils.format_timestamp(ts.replace(tzinfo=pytz.UTC)),
#                      jsonapi.loads(value)))
#         _log.debug("query result values {}".format(values))
#     return values


class CrateDriver(DbDriver):
    def __init__(self, connect_params, table_names):
        # kwargs['dbapimodule'] = 'mysql.connector'
        super(CrateDriver, self).__init__('mysql.connector', **connect_params)
        self.MICROSECOND_SUPPORT = None

        self.data_table = None
        self.topics_table = None
        self.meta_table = None
        self.agg_topics_table = None
        self.agg_meta_table = None

        if table_names:
            self.data_table = table_names['data_table']
            self.topics_table = table_names['topics_table']
            self.meta_table = table_names['meta_table']
            self.agg_topics_table = table_names.get('agg_topics_table', None)
            self.agg_meta_table = table_names.get('agg_meta_table', None)

